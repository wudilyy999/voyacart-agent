"""验证假模型的检索、确认准备和待批准状态，保留完整 SSE。"""
import json
from pathlib import Path
import time

import httpx

out = Path(__file__).resolve().parent
base = 'http://127.0.0.1:8080'
run_id = 'l1-final-order-run'
buyer, session = 'l1-final-review', 'l1-final-order-session'
body = {'threadId': session, 'runId': run_id,
    'messages':[{'id':'l1-user','role':'user','content':'L1 轨迹检查：预算300元以内，找一个寄到中国的轻便背包并准备确认卡'}],
    'state':{}, 'tools':[], 'context':[], 'forwardedProps':{'buyerId':buyer, 'locale':'zh-CN', 'currency':'CNY'}}
started = time.perf_counter()
response = httpx.post(base + '/commerce/ag-ui/run', json=body, timeout=90)
(out / 'run.sse').write_bytes(response.content)
response.raise_for_status()
events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]
ids = [line[4:] for line in response.text.splitlines() if line.startswith('id: ')]
assert ids == [f'{run_id}:{i}' for i in range(1, len(ids) + 1)]
assert events[-1]['type'] == 'RUN_FINISHED'
run = httpx.get(base + '/commerce/ag-ui/runs/' + run_id, params={'buyer_id':buyer}).json()
(out / 'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2))
assert run['status'] == 'completed'
assert len(run['state']['products']) == 3
assert len(run['state']['confirmations']) == 1
confirmation = run['state']['confirmations'][0]
assert confirmation['status'] == 'pending'
orders = httpx.get(base + '/commerce/orders', params={'buyer_id':buyer}).json()
(out / 'orders.json').write_text(json.dumps(orders, ensure_ascii=False, indent=2))
assert orders['total'] == 0
tool_names = [event['toolCallName'] for event in events if event['type'] == 'TOOL_CALL_START']
assert tool_names == ['product_search_tool', 'create_order_tool']
report = {'run_status':run['status'], 'tools':tool_names, 'products':3, 'pending_confirmations':1,
    'orders':0, 'events':len(ids), 'seconds':time.perf_counter() - started,
    'order_rate_for_check':1, 'ttft_seconds_for_check':0.02, 'token_seconds_for_check':0.001,
    'response_tokens':300, 'scope':'fixed trajectory correctness; capacity unmeasured'}
(out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
