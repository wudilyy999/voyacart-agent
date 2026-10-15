# -*- coding: utf-8 -*-
"""运行独立于 HTTP 订阅存在；日志写入成功后事件才对 SSE 可见。"""
from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
import logging
import time
import uuid

from ag_ui.core import RunAgentInput

from app.application.agents.ag_ui_adapter import AGUIRunAdapter
from app.application.agents.orchestrator import SubmitIntentInput
from app.infrastructure.ag_ui_journal import AGUIJournal, JournalLeaseLost, JournalNotFound, JournalForbidden, JournalConflict
from app.domain.queue.ports.task_queue import IntentTask, QueueCapacityExceeded
from app.infrastructure.ag_ui_signals import AGUISignals
from app.infrastructure.eventbus import observe_run_events
from app.infrastructure.learning_context import learning_scope

logger = logging.getLogger(__name__)
RECOVERY_INTERVAL_SECONDS = 5


@dataclass
class Running:
    owner: str
    deadline: float
    valid: bool = True
    reason: str = ""
    task: asyncio.Task | None = None

    def is_valid(self):
        return self.valid and time.monotonic() < self.deadline


class AGUIRuntime:
    def __init__(self, journal: AGUIJournal, orchestrator, confirmations=None, *, lease_seconds=30, heartbeat_seconds=5,
                 delta_coalesce_ms=0, backplane=None, task_queue=None, queue_max_pending=200, queue_wait_seconds=300, queue_enabled=False):
        self.journal, self.orchestrator, self.confirmations = journal, orchestrator, confirmations
        self.lease_seconds, self.heartbeat_seconds = lease_seconds, heartbeat_seconds
        self.running: dict[str, Running] = {}
        self.delta_coalesce_ms = delta_coalesce_ms
        self.signals = AGUISignals(backplane)
        self._recovery_task = None
        self.task_queue = task_queue
        self.queue_enabled = queue_enabled or task_queue is not None
        self.queue_max_pending, self.queue_wait_seconds = queue_max_pending, queue_wait_seconds

    async def startup(self):
        await self.journal.initialize()
        await self.journal.recover_expired()
        self._recovery_task = asyncio.create_task(self._recover_periodically(), name="agui-recovery")

    async def _recover_periodically(self):
        while True:
            await asyncio.sleep(RECOVERY_INTERVAL_SECONDS)
            await self.journal.recover_expired()

    async def shutdown(self):
        if self._recovery_task is not None:
            self._recovery_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._recovery_task
            self._recovery_task = None
        active = list(self.running.items())
        for _, entry in active:
            entry.reason = "restart"
            entry.valid = False
            if entry.task:
                entry.task.cancel()
        await asyncio.gather(*(entry.task for _, entry in active if entry.task), return_exceptions=True)
        for run_id, entry in active:
            await self.journal.end_owned(run_id, entry.owner)
            self.running.pop(run_id, None)

    async def submit(self, body: RunAgentInput, intent: SubmitIntentInput):
        if self.task_queue is None:
            return await self.start(body, intent, queue_fallback=self.queue_enabled)
        try:
            await self.journal.run(body.run_id, intent.buyer_id, body.thread_id)
        except JournalNotFound:
            pass
        else:
            return await self.start(body, intent)
        # 历史与客户端 state 不参与执行，重连请求只绑定本轮有效输入。
        props = {"buyerId": intent.buyer_id, "locale": intent.locale, "currency": intent.currency}
        if intent.selected_skill is not None:
            props["selectedSkill"] = body.forwarded_props["selectedSkill"]
        payload = body.model_copy(update={"messages": [body.messages[-1]], "state": {},
            "context": [], "forwarded_props": props}).model_dump(mode="json", by_alias=True)
        task = IntentTask("agui:" + body.run_id, body.thread_id, intent.buyer_id,
            intent.locale, intent.currency, intent.raw_query, ag_ui_input=payload)
        try:
            await self.task_queue.enqueue(task, max_pending=self.queue_max_pending)
        except QueueCapacityExceeded:
            raise
        except ValueError as error:
            raise JournalConflict(str(error)) from error
        except Exception as error:
            logger.warning("AG-UI 入队失败，转为进程内执行：%s", type(error).__name__)
            return await self.start(body, intent, queue_fallback=True)
        return {"runId": body.run_id, "threadId": body.thread_id, "status": "queued", "cursor": 0}

    async def queued_task(self, run_id, buyer_id):
        task = await self.task_queue.get_task("agui:" + run_id) if self.task_queue is not None else None
        if task is None:
            raise JournalNotFound("运行不存在")
        if task.buyer_id != buyer_id:
            raise JournalForbidden("无权访问该买家的运行")
        return task

    async def run(self, run_id, buyer_id):
        try:
            return await self.journal.run(run_id, buyer_id)
        except JournalNotFound:
            task = await self.queued_task(run_id, buyer_id)
            status = await self.task_queue.get_status(task.task_id)
            return {"runId": run_id, "threadId": task.shopping_session_id,
                "status": "failed" if status.state == "failed" else "queued", "cursor": 0,
                "messages": task.ag_ui_input["messages"], "input": task.ag_ui_input, "state": {}, "stopRequested": False}

    async def start(self, body: RunAgentInput, intent: SubmitIntentInput, *, automation_ticket=None, queue_fallback=False):
        owner = uuid.uuid4().hex
        started = time.monotonic()
        run, created = await self.journal.reserve(body.model_dump(mode="json", by_alias=True), intent.buyer_id, owner, self.lease_seconds, automation_ticket=automation_ticket)
        if created:
            entry = Running(owner, started + self.lease_seconds)
            self.running[body.run_id] = entry
            effective = RunAgentInput.model_validate(run["input"])
            entry.task = asyncio.create_task(self._produce(effective, intent, entry, queue_fallback=queue_fallback), name=f"agui-run:{body.run_id}")
        return run

    async def cancel(self, run_id, buyer_id):
        try:
            run = await self.journal.request_stop(run_id, buyer_id)
        except JournalNotFound:
            task = await self.queued_task(run_id, buyer_id)
            owner = uuid.uuid4().hex
            _, created = await self.journal.reserve(task.ag_ui_input, buyer_id, owner, self.lease_seconds)
            run = await self.journal.request_stop(run_id, buyer_id)
            if created:
                await self.journal.end_owned(run_id, owner, stopped=True)
                return await self.journal.run(run_id, buyer_id)
        entry = self.running.get(run_id)
        if entry and entry.task:
            entry.reason = "stop"
            entry.valid = False
            entry.task.cancel()
            await asyncio.shield(asyncio.gather(entry.task, return_exceptions=True))
            await self.journal.end_owned(run_id, entry.owner, stopped=True)
            self.running.pop(run_id, None)
            run = await self.journal.run(run_id, buyer_id)
        return run

    async def _produce(self, body, intent, entry, *, queue_fallback=False):
        queue = asyncio.Queue()
        adapter = AGUIRunAdapter(body, queue.put_nowait, authoritative_state=body.state)

        async def write_events():
            while True:
                event = await queue.get()
                if event is None:
                    return
                events = [event]
                ending = False
                deadline = time.monotonic() + self.delta_coalesce_ms / 1000
                while len(events) < 64:
                    if not queue.empty():
                        following = queue.get_nowait()
                    elif self.delta_coalesce_ms and events[-1].type in {"TEXT_MESSAGE_CONTENT", "TOOL_CALL_ARGS"}:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            break
                        try:
                            following = await asyncio.wait_for(queue.get(), remaining)
                        except asyncio.TimeoutError:
                            break
                    else:
                        break
                    if following is None:
                        ending = True
                        break
                    events.append(following)
                payloads = [value.model_dump(mode="json", by_alias=True, exclude_none=True) for value in events]
                if self.delta_coalesce_ms:
                    merged = []
                    for value in payloads:
                        identity = "messageId" if value["type"] == "TEXT_MESSAGE_CONTENT" else "toolCallId" if value["type"] == "TOOL_CALL_ARGS" else None
                        if (identity and merged and merged[-1]["type"] == value["type"]
                                and merged[-1][identity] == value[identity]):
                            merged[-1]["delta"] += value["delta"]
                        else:
                            merged.append(value)
                    payloads = merged
                if entry.reason == "restart":
                    for value in payloads:
                        if value["type"] == "RUN_ERROR":
                            value["code"] = "SERVER_RESTART"
                try:
                    await self.journal.append(body.run_id, entry.owner, payloads)
                except Exception:
                    entry.valid = False
                    entry.reason = "restart"
                    if entry.task:
                        entry.task.cancel()
                    raise
                await self.signals.publish(body.run_id, body.thread_id)
                if ending:
                    return

        async def heartbeat():
            while True:
                await asyncio.sleep(self.heartbeat_seconds)
                started = time.monotonic()
                try:
                    renewed = await asyncio.wait_for(self.journal.renew(body.run_id, entry.owner, self.lease_seconds),
                                                    max(0.001, entry.deadline - started))
                    if not renewed:
                        run = await self.journal.run(body.run_id, intent.buyer_id)
                        entry.reason = "stop" if run["stopRequested"] else "restart"
                        raise JournalLeaseLost("运行日志租约失效或收到跨实例停止请求")
                    entry.deadline = started + self.lease_seconds
                except Exception:
                    entry.valid = False
                    if entry.task:
                        entry.task.cancel()
                    return

        writer = asyncio.create_task(write_events())
        lease_task = asyncio.create_task(heartbeat())
        adapter.start()
        if queue_fallback:
            from ag_ui.core import CustomEvent
            queue.put_nowait(CustomEvent(name="runtime.degraded", value={"component": "queue", "fallback": "in_process"}))
        def on_trade_event(event):
            if event.type == "usage.summary":
                from ag_ui.core import CustomEvent
                queue.put_nowait(CustomEvent(name="usage.summary", value=event.payload))
            adapter.on_trade_event(event)
        try:
            if self.confirmations is not None:
                saved = await self.confirmations.list(intent.buyer_id, intent.shopping_session_id)
                adapter.state["confirmations"] = saved["confirmations"]
                adapter.snapshot()
            with learning_scope(self.journal, body.run_id, intent.buyer_id, intent.shopping_session_id), observe_run_events(on_trade_event):
                result = await self.orchestrator.handle_intent(intent, event_observer=adapter.on_agent_event,
                    use_semantic_cache=False, persistence_guard=entry.is_valid)
            if not entry.is_valid():
                raise asyncio.CancelledError()
            if getattr(result,"error_code",None)=="SESSION_VERSION_CHANGED":
                adapter.state["resumeDestination"]=await self.journal.latest_destination(intent.shopping_session_id,intent.buyer_id)
            if result.error or adapter.error:
                adapter.fail(result.error if getattr(result,"error_code",None) in {"SESSION_VERSION_CHANGED","CONTEXT_CAPACITY_EXCEEDED","MODEL_RESPONSE_INCOMPLETE"} else adapter.error or "本轮服务暂时未能完成请求，请重试。", code=getattr(result,"error_code",None))
            else:
                adapter.finish(result.final_text)
        except asyncio.CancelledError:
            adapter.fail("本轮已明确停止" if entry.reason == "stop" else "服务重启或执行中断，已保存的内容仍可恢复。",
                         cancelled=entry.reason == "stop", code=None if entry.reason == "stop" else "SERVER_RESTART")
        except Exception:
            logger.exception("AG-UI 运行失败：%s", body.run_id)
            adapter.fail("本轮服务暂时未能完成请求，请重试。")
        finally:
            lease_task.cancel()
            await asyncio.gather(lease_task, return_exceptions=True)
            queue.put_nowait(None)
            try:
                await writer
            except Exception:
                logger.exception("AG-UI 日志写入失败，等待持久租约过期后标记中断：%s", body.run_id)
            entry.valid = False
            self.running.pop(body.run_id, None)
