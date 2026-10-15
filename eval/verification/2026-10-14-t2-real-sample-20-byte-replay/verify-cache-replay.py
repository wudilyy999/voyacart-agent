"""核对缓存后运行原 T2 入口，HTTP 请求边界在本次验证中明确禁止调用。"""
import asyncio
from collections import Counter
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

ROOT=Path.cwd()
sys.path.insert(0,str(ROOT))
from scripts.esci import enrich_catalog
from scripts.esci.finalize_catalog import load_rows
from scripts.esci.prepare import json_line

prepared=Path('/tmp/voyacart-t2-sample-20-20261014-1200')
output=ROOT/'eval/verification/2026-10-14-t2-real-sample-20-byte-replay'
cache_path=ROOT/'data/esci/enrichment-v1.jsonl'
before=cache_path.read_bytes()
cache=enrich_catalog.read_cache(cache_path,'enrich')
rows=load_rows(prepared/'enrichment-inputs.jsonl')
matched=[]
assert len(rows)==20
assert hashlib.blake2b(before).hexdigest()=='5024dff1bb566c3bcd4f8080636d961a8cd5c3809b0f55d039009880e3eeec86e98d97650cdd776e5128c3d819b63abe96f213e4400a3e5861c670b54a66c4d5'
for row in rows:
    key=enrich_catalog.cache_key({**row,'prompt_version':enrich_catalog.VERSIONS['enrich']},'enrich')
    saved=cache[key]
    assert saved['input_fingerprint']==hashlib.blake2b(json_line(row).encode()).hexdigest()
    matched.append({'locale':row['locale'],'asin':row['asin'],'status':saved['status']})

network_attempts=0
async def forbid_request(self,*args,**kwargs):
    global network_attempts
    network_attempts+=1
    raise AssertionError('本次缓存复核禁止任何 HTTP 模型请求')

sys.argv=['scripts.esci.enrich_catalog','--enrich','--prepared',str(prepared),'--output',str(output)]
original_stdout=io.StringIO()
with patch.object(enrich_catalog.httpx.AsyncClient,'post',new=forbid_request),redirect_stdout(original_stdout):
    asyncio.run(enrich_catalog.main())
(output/'stdout.log').write_text(original_stdout.getvalue())
(output/'cache-before.jsonl').write_bytes(before)
after=cache_path.read_bytes()
(output/'cache-after.jsonl').write_bytes(after)
report=json.loads((output/'report.json').read_text())
assert report['candidate_count']==report['cache_hits']==20
assert report['model_calls']==network_attempts==0
assert before==after
verification={'cache_path':str(cache_path.relative_to(ROOT)),'candidate_count':20,'cache_hits':20,
    'matched_input_keys':matched,'before_states':dict(Counter(row['status'] for row in matched)),
    'model_calls':report['model_calls'],'network_attempts':network_attempts,'cache_bytes':len(before),
    'fingerprint_method':'blake2b','before_content_fingerprint':hashlib.blake2b(before).hexdigest(),
    'after_content_fingerprint':hashlib.blake2b(after).hexdigest(),'byte_identical':before==after,
    'command':'.venv/bin/python eval/verification/2026-10-14-t2-real-sample-20-byte-replay/verify-cache-replay.py',
    'request_guard':'httpx.AsyncClient.post 调用即失败；只运行全部键已存在的缓存输入'}
(output/'cache-verification.json').write_text(json_line(verification))
shutil.copyfile(__file__,output/'verify-cache-replay.py')
print(json_line({key:verification[key] for key in ('candidate_count','cache_hits','model_calls','network_attempts','byte_identical','before_states')}).strip())
