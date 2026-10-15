"""在无外网容器中校验默认流式长度与实际耗时。"""
import asyncio
import json
from pathlib import Path
import subprocess
import time

import httpx
from openai import AsyncOpenAI


async def main():
    server = subprocess.Popen(['python','-m','uvicorn','--app-dir','/app/scripts/loadtest',
        'mock_llm:app','--host','127.0.0.1','--port','8082'], stdout=subprocess.DEVNULL)
    try:
        async with httpx.AsyncClient() as health:
            for _ in range(50):
                try:
                    response = await health.get('http://127.0.0.1:8082/health')
                    response.raise_for_status()
                    break
                except httpx.ConnectError:
                    await asyncio.sleep(.1)
            else:
                raise RuntimeError('假模型启动超时')
        async with AsyncOpenAI(api_key='local',base_url='http://127.0.0.1:8082/v1') as client:
            started = time.perf_counter()
            stream = await client.chat.completions.create(model='mock-chat',
                messages=[{'role':'user','content':'默认长度与延迟诊断'}], stream=True,
                stream_options={'include_usage':True})
            stamps, text, usage = [], '', None
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    stamps.append(time.perf_counter() - started)
                    text += chunk.choices[0].delta.content
                if chunk.usage:
                    usage = chunk.usage.model_dump()
            assert len(stamps) == 300 and len(text) == 300
            assert .75 <= stamps[0] <= 2
            assert stamps[-1] >= .8 + 299 * .03 - .1
            print(json.dumps({'simulated_tokens':300,'first_token_seconds':stamps[0],
                'last_token_seconds':stamps[-1], 'usage':usage,
                'intervals_seconds':[b-a for a,b in zip(stamps,stamps[1:])]}, indent=2))
    finally:
        server.terminate()
        server.wait(timeout=10)


asyncio.run(main())
