import httpx,json,time,subprocess,hashlib
from pathlib import Path
out=Path('eval/verification/2026-10-14-t5-integrated')
base='http://127.0.0.1:8080'
body={'threadId':'scale-t5-session','runId':'scale-t5-run','messages':[{'id':'t5-user','role':'user','content':'预算300元以内，找一个寄到中国的轻便背包'}],'state':{},'tools':[],'context':[],'forwardedProps':{'buyerId':'scale-review','locale':'zh-CN','currency':'CNY'}}
response=httpx.post(base+'/commerce/ag-ui/run',json=body,timeout=90)
response.raise_for_status();(out/'run.sse').write_text(response.text)
events=[json.loads(l[6:]) for l in response.text.splitlines() if l.startswith('data: ')]
ids=[l[4:] for l in response.text.splitlines() if l.startswith('id: ')]
assert ids==[f'scale-t5-run:{i}' for i in range(1,len(ids)+1)]
assert events[-1]['type']=='RUN_FINISHED'
run=httpx.get(base+'/commerce/ag-ui/runs/scale-t5-run',params={'buyer_id':'scale-review'}).json()
assert run['status']=='completed' and len(run['state']['products'])==3
assert {p['category'] for p in run['state']['products']}=={'旅行装备'}
replay=httpx.get(base+'/commerce/ag-ui/runs/scale-t5-run/events',params={'buyer_id':'scale-review'},headers={'Last-Event-ID':ids[4]},timeout=10)
(out/'replay.sse').write_text(replay.text)
assert [l[4:] for l in replay.text.splitlines() if l.startswith('id: ')]==ids[5:]
duplicate=httpx.post(base+'/commerce/ag-ui/run',json=body,timeout=10)
assert duplicate.text==response.text
(out/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2))
(out/'report.json').write_text(json.dumps({'http_status':response.status_code,'run_status':run['status'],'products':3,'category':'旅行装备','ordered_events':len(ids),'cursor_replay':True,'duplicate_replay':True,'model':'mock-chat','api_replicas':2,'worker_replicas':2,'full_capacity_evaluation':False},ensure_ascii=False,indent=2))
(out/'containers.txt').write_bytes(subprocess.check_output(['docker','ps','--filter','name=voyacart-scale-review','--format','{{.Names}}\t{{.Status}}']))
print((out/'report.json').read_text())
