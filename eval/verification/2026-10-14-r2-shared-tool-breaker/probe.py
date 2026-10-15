"""独立本机 Redis 与独立进程验证现有工具熔断，使用默认三次失败及 60 秒冷却。"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

OUTPUT = Path(__file__).resolve().parent
ROOT = OUTPUT.parents[2]
ENV = {key: os.environ[key] for key in ('PATH', 'TMPDIR') if key in os.environ}
ENV['PYTHONPATH'] = str(ROOT)


async def worker(phase, url):
    from agentscope.message import TextBlock, ToolResultState
    from agentscope.tool import FunctionTool, ToolChunk
    from app.infrastructure.cache.redis_cache import RedisCache
    from app.infrastructure.resilience import ToolResilienceMiddleware
    from app.infrastructure.shared_breaker import SharedCircuitBreakerRegistry

    cache = RedisCache(url)
    assert await cache.ping(), '独立 Redis 未连接'
    registry = SharedCircuitBreakerRegistry(cache)
    calls, observed = [], []
    async def product_search_tool():
        """演练工具：明确注入工具上游连接故障，恢复时返回成功。"""
        calls.append(time.time())
        observed.append(await registry.status_async('product_search_tool'))
        if phase == 'fail':
            raise ConnectionError('演练注入的工具上游连接故障')
        return ToolChunk(content=[TextBlock(type='text', text='演练工具已恢复')],
            state=ToolResultState.SUCCESS)
    tool = FunctionTool(product_search_tool, middlewares=[ToolResilienceMiddleware(registry)])
    results = []
    for _ in range(3 if phase == 'fail' else 1):
        response = await tool()
        if hasattr(response, '__aiter__'):
            response = [chunk async for chunk in response]
            response = response[-1]
        results.append(response.state.value)
        assert response.state == (ToolResultState.ERROR if phase in {'fail', 'blocked'} else ToolResultState.SUCCESS)
    status = await registry.status_async('product_search_tool')
    assert len(calls) == (3 if phase == 'fail' else 0 if phase == 'blocked' else 1)
    assert status == ('closed' if phase == 'recovered' else 'open')
    if phase == 'recovered':
        assert observed == ['half_open']
    row = {'phase': phase, 'pid': os.getpid(), 'observed_at': time.time(),
        'handler_calls': len(calls), 'handler_observed_status': observed,
        'results': results, 'status': status,
        'redis_state': await cache.get_json('voyacart:breaker:product_search_tool')}
    await cache.close()
    print(json.dumps(row, ensure_ascii=False))


if len(sys.argv) > 1:
    asyncio.run(worker(sys.argv[1], sys.argv[2]))
else:
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    command = ['redis-server', '--bind', '127.0.0.1', '--port', str(port),
        '--save', '', '--appendonly', 'no', '--dir', str(OUTPUT)]
    (OUTPUT / 'redis-command.json').write_text(json.dumps(command) + '\n')
    files = ('app/infrastructure/resilience.py', 'app/infrastructure/shared_breaker.py',
        'app/infrastructure/cache/redis_cache.py')
    (OUTPUT / 'source.json').write_text(json.dumps({'commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'content_fingerprints_blake2b': {file: hashlib.blake2b((ROOT / file).read_bytes()).hexdigest()
            for file in files}, 'failure_threshold': 3, 'reset_seconds': 60,
        'model_requests': 0}, indent=2) + '\n')
    with (OUTPUT / 'redis.log').open('x') as log:
        server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=ENV)
        try:
            for _ in range(100):
                if server.poll() is not None:
                    raise RuntimeError('独立 Redis 启动失败，见原始日志')
                try:
                    with socket.create_connection(('127.0.0.1', port), timeout=.1):
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise TimeoutError('独立 Redis 启动超时')
            rows = []
            for phase in ('fail', 'blocked', 'recovered'):
                if phase == 'recovered':
                    print('等待现有 60 秒冷却窗口，独立 Redis 保持运行。', flush=True)
                    while time.time() < rows[0]['redis_state']['opened_at'] + 60.2:
                        time.sleep(.5)
                result = subprocess.run([sys.executable, str(OUTPUT / 'probe.py'), phase,
                    f'redis://127.0.0.1:{port}/0'], cwd=ROOT, env=ENV,
                    capture_output=True, text=True, timeout=30)
                (OUTPUT / (phase + '.stdout.log')).write_text(result.stdout)
                (OUTPUT / (phase + '.stderr.log')).write_text(result.stderr)
                (OUTPUT / (phase + '.exit.json')).write_text(json.dumps({'returncode': result.returncode}) + '\n')
                result.check_returncode()
                rows.append(json.loads(result.stdout))
                print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
            assert len({row['pid'] for row in rows}) == 3
            (OUTPUT / 'report.json').write_text(json.dumps({'passed': True,
                'model_requests': 0, 'rows': rows,
                'elapsed_after_open_seconds': rows[-1]['observed_at'] - rows[0]['redis_state']['opened_at']},
                ensure_ascii=False, indent=2) + '\n')
        finally:
            server.terminate()
            server.wait(timeout=10)
