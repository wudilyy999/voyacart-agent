"""使用真实预选文件核对 JSONL 读取与缓存原样保留；不调用模型。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root))
from scripts.esci.finalize_catalog import load_rows
from scripts.esci.prepare import cache_key, read_cache

output = Path(__file__).resolve().parent
prepared = root / 'eval/verification/2026-10-14-t2-input-plan'
paths = [prepared / name for name in ('products.jsonl', 'examples.jsonl', 'enrichment-inputs.jsonl')]
cache = root / 'data/esci/query-class-v1.jsonl'
paths.append(cache)
before = {str(p.relative_to(root)): hashlib.blake2b(p.read_bytes()).hexdigest() for p in paths}
counts = {}
unicode_counts = {}
for path in paths:
    with path.open(encoding='utf-8') as stream:
        expected = [json.loads(line) for line in stream if line.strip()]
    if load_rows(path) != expected:
        raise ValueError('JSONL 与独立文件逐行读取结果不同')
    if path == cache and read_cache(path) != {cache_key(row): row for row in expected}:
        raise ValueError('真实查询缓存读取结果不同')
    counts[str(path.relative_to(root))] = len(expected)
    unicode_counts[str(path.relative_to(root))] = {f'U+{ord(ch):04X}': path.read_text().count(ch)
                                                for ch in ('\u2028', '\u2029', '\u0085')}
after = {str(p.relative_to(root)): hashlib.blake2b(p.read_bytes()).hexdigest() for p in paths}
if before != after:
    raise ValueError('读取过程改变了真实输入或缓存')
status = subprocess.run(['git', 'status', '--porcelain', '--', 'app', 'scripts/eval', 'tests', 'configs',
                         'pyproject.toml', 'uv.lock', 'Makefile', '.github', 'data/catalog-v1.jsonl'],
                         cwd=root, check=True, capture_output=True, text=True).stdout
if status:
    raise ValueError('默认 Harness 源码范围出现改动')
sources = [root / 'scripts/esci/prepare.py', root / 'scripts/esci/finalize_catalog.py', Path(__file__)]
result = {'status': 'passed', 'record_counts': counts, 'unicode_separator_counts': unicode_counts,
          'input_bytes_unchanged': True, 'model_calls': 0, 'external_http_attempts': 0,
          'default_harness_source_unchanged': True, 'input_fingerprints': before,
          'source_fingerprints': {str(p.relative_to(root)): hashlib.blake2b(p.read_bytes()).hexdigest() for p in sources}}
with (output / 'real-input-verification.json').open('x') as stream:
    stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('status', 'record_counts', 'input_bytes_unchanged',
                                       'model_calls', 'external_http_attempts')}, ensure_ascii=False))
