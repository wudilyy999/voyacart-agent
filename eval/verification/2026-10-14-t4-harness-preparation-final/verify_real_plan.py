"""直接回查训练预选、人工标签和原文商品；保存一次独立来源核验。"""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
output = Path(__file__).resolve().parent
prepared = root / 'eval/verification/2026-10-14-t2-input-plan'
path = root / 'eval/harness/esci-v1/preparation.json'
plan = json.loads(path.read_text())
selection = json.loads((prepared / 'selection-plan.json').read_text())
dev = {(q['locale'], q['query_id']): q for q in selection['queries']['dev']}
labels = {(row['product_locale'], row['query_id'], row['product_id']): row
          for row in map(json.loads, (prepared / 'examples.jsonl').read_text().splitlines())
          if row['split'] == 'train'}
products = {(row['product_locale'], row['product_id']): row
            for row in map(json.loads, (prepared / 'products.jsonl').read_text().splitlines())}
verified = []
for case in plan['cases']:
    q = case['source_query']
    key = q['locale'], q['query_id']
    checks = {'query_is_train': q['split'] == 'train' and dev[key]['split'] == 'train',
              'query_text_matches': q['query'] == dev[key]['query'],
              'exact_labels_match': all(labels[q['locale'], q['query_id'], p['asin']]['esci_label'] == 'E'
                                        for p in case['source_products']),
              'titles_match': all(products[p['locale'], p['asin']]['product_title'] == p['title']
                                  for p in case['source_products']),
              'final_ids_pending': all('product_id' not in p and 'sku_id' not in p for p in case['source_products'])}
    if not all(checks.values()):
        raise ValueError('真实训练来源核验失败：' + case['id'])
    verified.append({'case_id': case['id'], 'checks': checks})
source_paths = ('app', 'scripts/eval', 'tests', 'configs', 'pyproject.toml', 'uv.lock', 'Makefile',
                '.github', 'data/catalog-v1.jsonl')
status = subprocess.run(['git', 'status', '--porcelain', '--', *source_paths], cwd=root,
                        check=True, capture_output=True, text=True).stdout
if status:
    raise ValueError('默认 Harness 源码范围出现改动')
same_bytes = path.read_bytes() == (output / 'generated/preparation.json').read_bytes()
if not same_bytes or plan['runnable'] is not False or len(verified) != 10:
    raise ValueError('准备态或确定性重生成核验失败')
files = [root / 'eval/harness/esci-v1/prepare.py', path, output / 'test_preparation.py', Path(__file__)]
result = {'status': 'verified_preparation', 'runnable': False, 'cases_verified': verified,
          'byte_identical_regeneration': same_bytes, 'default_harness_source_unchanged': True,
          'model_calls': 0, 'http_attempts': 0, 'full_harness': 'not_run',
          'source_commit': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, check=True,
                                          capture_output=True, text=True).stdout.strip(),
          'source_fingerprints': {str(p.relative_to(root)): hashlib.blake2b(p.read_bytes()).hexdigest() for p in files},
          'input_fingerprints': plan['input_fingerprints'],
          'missing_files': [p for p in plan['required_artifacts'] if p.startswith(('data/', 'eval/'))
                            and not (root / p).exists()],
          'pending_other_requirements': [p for p in plan['required_artifacts']
                                         if not p.startswith(('data/', 'eval/'))]}
with (output / 'real-source-verification.json').open('x') as stream:
    stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('status', 'runnable', 'byte_identical_regeneration',
                                       'default_harness_source_unchanged', 'model_calls', 'http_attempts')}, ensure_ascii=False))
