"""T2 缓存、枚举边界、服务中断和最终中文子集对齐。"""
import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from scripts.esci.build_catalog import TARGETS, preselect
from scripts.esci.enrich_catalog import VERSIONS, fill_cache, parse_result, read_cache
from scripts.esci.finalize_catalog import translation_inputs
from scripts.esci.prepare import CATEGORIES, SEED, json_line
from scripts.esci.test_build_catalog import classified_pool
from scripts.esci.test_catalog_records import product


def settings(concurrency=2,retries=0):
    return SimpleNamespace(llm_base_url='https://model.example/v1',llm_api_key='test-only-credential',
        llm_model='test-model',llm_max_concurrency=concurrency,llm_min_interval_seconds=0,llm_max_retries=retries)


def input_rows(mode):
    if mode=='enrich':
        return [{'locale':'us','asin':str(i),'title':'backpack','brand':'example',
            'description':'metal strap','bullet_points':''} for i in range(8)]
    return [{'locale':'us','query_id':i,'query':'backpack'} for i in range(8)]


def answer(mode,invalid=False):
    content={'category':'旅行装备','material_tags':['金属']} if mode=='enrich' else {'translation':'轻便背包'}
    if invalid:
        content={'category':'越界类目','material_tags':[]} if mode=='enrich' else {'translation':''}
    return {'choices':[{'finish_reason':'stop','message':{'content':json_line(content).strip()}}]}


@pytest.mark.parametrize('separator', ['\u2028', '\u2029', '\u0085'])
def test_translation_cache_preserves_unicode_line_separators(tmp_path, separator):
    row = {'locale': 'jp', 'query_id': 1, 'prompt_version': VERSIONS['translate'], 'status': 'ok',
           'query': f'原文{separator}検索', 'translation': f'中文{separator}查询'}
    path = tmp_path / 'translate.jsonl'
    path.write_text(json_line(row))
    assert read_cache(path, 'translate') == {('jp', 1, VERSIONS['translate']): row}


@pytest.mark.parametrize('mode',['enrich','translate'])
async def test_cache_replay_is_zero_call_deterministic_and_concurrency_is_capped(tmp_path,mode):
    calls=active=maximum=0
    async def respond(request):
        nonlocal calls,active,maximum
        calls+=1;active+=1;maximum=max(maximum,active)
        payload=json.loads(request.content)
        assert payload['temperature']==0 and payload['response_format']=={'type':'json_object'}
        row=json.loads(payload['messages'][1]['content'])
        await asyncio.sleep(0.001)
        active-=1
        return httpx.Response(200,json=answer(mode,str(row.get('asin',row.get('query_id')))=='3'))

    rows=input_rows(mode);cache=tmp_path/'cache.jsonl';first=tmp_path/'first';replay=tmp_path/'replay';reverse=tmp_path/'reverse'
    for output in (first,replay,reverse):output.mkdir()
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        report=await fill_cache(rows,mode,cache,first,settings(8),client)
        before=cache.read_bytes()
        replay_report=await fill_cache(list(reversed(rows)),mode,cache,replay,settings(8),client)
        assert cache.read_bytes()==before
        await fill_cache(list(reversed(rows)),mode,tmp_path/'reverse-cache.jsonl',reverse,settings(8),client)
    assert maximum==2 and calls==16 and report['model_calls']==8
    assert report['failed_outputs']==report['cached_failure_count']==1
    assert replay_report['model_calls']==0 and replay_report['cache_hits']==8
    assert replay_report['cached_failure_count']==1
    assert (tmp_path/'reverse-cache.jsonl').read_bytes()==before
    assert len(read_cache(cache,mode))==8
    assert len((first/'failures.jsonl').read_text().splitlines())==1
    assert settings().llm_api_key not in (first/'requests.jsonl').read_text()
    changed=[{**rows[0],('title' if mode=='enrich' else 'query'):'changed input'}]
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ValueError,match='内容指纹已变化'):
            await fill_cache(changed,mode,cache,tmp_path,settings(),client)
    assert calls==16


@pytest.mark.parametrize('failure',['http','connection'])
async def test_service_failure_keeps_completed_items_and_resume_only_calls_missing(tmp_path,failure):
    calls=0
    def respond(request):
        nonlocal calls
        calls+=1
        if calls==2:
            if failure=='connection':raise httpx.ConnectError('connection failed',request=request)
            return httpx.Response(503,text=settings().llm_api_key)
        return httpx.Response(200,json=answer('enrich'))
    cache=tmp_path/'cache.jsonl';rows=input_rows('enrich')[:3]
    first=tmp_path/'first';first.mkdir();resume=tmp_path/'resume';resume.mkdir()
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ExceptionGroup,match='TaskGroup'):
            await fill_cache(rows,'enrich',cache,first,settings(1),client)
        assert len(read_cache(cache,'enrich'))==1
        partial=json.loads((first/'call-counts.json').read_text())
        assert partial['model_calls']==2 and partial['completed_calls']==1
        report=await fill_cache(rows,'enrich',cache,resume,settings(1),client)
    assert report['model_calls']==2 and report['cache_hits']==1 and len(read_cache(cache,'enrich'))==3
    assert len((first/'failures.jsonl').read_text().splitlines())==1
    assert settings().llm_api_key not in (first/'requests.jsonl').read_text()


@pytest.mark.parametrize('recovers',[True,False])
async def test_timeout_attempts_are_counted_and_retry_limit_is_honored(tmp_path,monkeypatch,recovers):
    calls=0;delays=[]
    async def wait(delay):delays.append(delay)
    def respond(request):
        nonlocal calls
        calls+=1
        if calls<3 or not recovers:raise httpx.ReadTimeout('request timed out',request=request)
        return httpx.Response(200,json=answer('translate'))
    monkeypatch.setattr('scripts.esci.enrich_catalog.asyncio.sleep',wait)
    cache=tmp_path/'cache.jsonl'
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        if recovers:
            report=await fill_cache(input_rows('translate')[:1],'translate',cache,tmp_path,settings(1,2),client)
            assert report['completed_calls']==1
        else:
            with pytest.raises(ExceptionGroup):
                await fill_cache(input_rows('translate')[:1],'translate',cache,tmp_path,settings(1,2),client)
    assert calls==3 and delays==[6,18]
    assert len(read_cache(cache,'translate'))==int(recovers)
    assert json.loads((tmp_path/'call-counts.json').read_text())['model_calls']==3


@pytest.mark.parametrize('content',[
    {'category':'旅行装备','material_tags':['未知材质']},
    {'category':'旅行装备','material_tags':['金属','金属']},
    {'category':'旅行装备','material_tags':'金属'},
    {'category':'旅行装备','material_tags':[],'extra':'field'},
    {'category':'旅行装备'},
])
def test_product_response_requires_exact_schema_and_enumerated_labels(content):
    with pytest.raises(ValueError):parse_result(json_line(content),'enrich')


async def test_incomplete_response_is_saved_as_failed_and_replayed_without_call(tmp_path):
    body=answer('enrich');body['choices'][0]['finish_reason']='length'
    cache=tmp_path/'cache.jsonl';replay=tmp_path/'replay';replay.mkdir()
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=body))) as client:
        report=await fill_cache(input_rows('enrich')[:1],'enrich',cache,tmp_path,settings(),client)
        assert report['failed_outputs']==1
        replay_report=await fill_cache(input_rows('enrich')[:1],'enrich',cache,replay,settings(),client)
    assert replay_report['model_calls']==0
    assert next(iter(read_cache(cache,'enrich').values()))['status']=='failed'


def test_translation_inputs_are_selected_after_product_enrichment(tmp_path):
    rows,cache=classified_pool();queries=preselect(rows,cache)
    (tmp_path/'selection-plan.json').write_text(json_line({'seed':SEED,'targets':TARGETS,'queries':queries}))
    sources=[];examples=[];enhanced=[];rejected=set()
    for dataset,group in queries.items():
        for i,row in enumerate(group):
            asin=str(row['query_id']);category=row['category']
            if dataset=='holdout' and i%30==0:
                category='其他';rejected.add((row['locale'],row['query_id']))
            sources.append(product(row['locale'],asin))
            examples.append({'product_locale':row['locale'],'query_id':row['query_id'],'product_id':asin,'esci_label':'E'})
            enhanced.append({'locale':row['locale'],'asin':asin,'prompt_version':VERSIONS['enrich'],
                'status':'ok','category':category,'material_tags':[]})
    for name,records in (('products.jsonl',sources),('examples.jsonl',examples),('enriched.jsonl',enhanced)):
        (tmp_path/name).write_text(''.join(json_line(row) for row in records))
    selected=translation_inputs(tmp_path,tmp_path/'enriched.jsonl')
    assert len(selected)==200
    assert [sum(row['locale']==locale for row in selected) for locale in ('us','es','jp')]==[100,50,50]
    assert not rejected & {(row['locale'],row['query_id']) for row in selected}
    assert selected==translation_inputs(tmp_path,tmp_path/'enriched.jsonl')
    for status in ('failed','unexpected'):
        enhanced[0].update(status=status);(tmp_path/'enriched.jsonl').write_text(''.join(json_line(row) for row in enhanced))
        with pytest.raises(ValueError,match='状态或字段无效'):
            translation_inputs(tmp_path,tmp_path/'enriched.jsonl')
