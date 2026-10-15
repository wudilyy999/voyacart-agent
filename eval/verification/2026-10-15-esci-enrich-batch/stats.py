"""批量增强的实测汇总：调用数、状态码、延迟、网关报告的 token、类目分布，并与代理类目和 741 条单件结果描述性对照（一致率不是准确率）。"""
import collections, gzip, json, math, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / 'eval/verification/2026-10-15-esci-enrich-batch'


def rows(path):
    with (gzip.open if str(path).endswith('.gz') else open)(path, 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip()]


requests = [r for run in sorted(D.glob('run-*/requests.jsonl.gz')) for r in rows(run)]
ok = [r for r in requests if r['http_status'] == 200]
lat = sorted(r['elapsed_seconds'] for r in ok)
rank = lambda p: lat[math.ceil(p * len(lat)) - 1]
usage = [json.loads(r['response']).get('usage', {}) for r in ok]
counts = [json.loads(p.read_text()) for p in sorted(D.glob('run-*/call-counts.json'))]
cache = rows(ROOT / 'data/esci/enrichment-batch-v1.jsonl')
proxy = {(r['locale'], r['asin']): r for r in rows(ROOT / 'data/esci/category-proxy-v1.jsonl')}
single = {(r['locale'], r['asin']): r for r in rows(D / 'single-call-cache-741-rows.jsonl') if r['status'] == 'ok'}
batch = {(r['locale'], r['asin']): r for r in cache}
overlap = [k for k in single if k in batch]
tags = collections.Counter(t for r in cache for t in r['material_tags'])
summary = {
    'items': len(cache), 'status': dict(collections.Counter(r['status'] for r in cache)),
    'batch_size_of_saved_rows': dict(collections.Counter(r['batch_size'] for r in cache)),
    'http_requests_logged': len(requests), 'http_status': dict(collections.Counter(str(r['http_status']) for r in requests)),
    'runs': len(counts), 'split_batches_total': sum(c['split_batches'] for c in counts),
    'model_calls_total_across_runs': sum(c['model_calls'] for c in counts),
    'latency_seconds_http200': {'count': len(lat), 'mean': statistics.mean(lat), 'p50': rank(.5), 'p95': rank(.95), 'max': lat[-1],
                                 'scope': '从发起 HTTP 请求计到收到响应，不含网关节流等待；每次请求含 10 件（拆分后含 1 件）'},
    'gateway_reported_usage_http200': {k: sum(u.get(k, 0) for u in usage) for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')},
    'usage_reported_requests': sum(1 for u in usage if u), 'billing': '网关未返回费用，记为未知',
    'category_distribution': dict(collections.Counter(r['category'] for r in cache)),
    'products_with_material_tags': sum(1 for r in cache if r['material_tags']),
    'material_tag_counts': dict(tags),
    'agreement_with_query_proxy_category': sum(batch[k]['category'] == proxy[k]['category'] for k in batch) / len(batch),
    'overlap_with_741_single_call_rows': {
        'products': len(overlap), 'locales': dict(collections.Counter(k[0] for k in overlap)),
        'category_agreement': sum(batch[k]['category'] == single[k]['category'] for k in overlap) / len(overlap),
        'material_tags_exact_agreement': sum(sorted(batch[k]['material_tags']) == sorted(single[k]['material_tags']) for k in overlap) / len(overlap),
        'note': '只说明批量与单件结果的接近程度，不是准确率'},
}
(D / 'stats.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))
