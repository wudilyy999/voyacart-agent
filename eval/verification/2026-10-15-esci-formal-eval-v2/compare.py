"""v1（代理类目）与 v2（批量商品增强）的开发档、留出档并排对照；只读两边原始 report.json。"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
V = {'v1': {'dev': 'eval/verification/2026-10-15-esci-dev', 'holdout': 'eval/verification/2026-10-15-esci-holdout'},
     'v2': {'dev': 'eval/verification/2026-10-15-esci-dev-v2', 'holdout': 'eval/verification/2026-10-15-esci-holdout-v2'}}
RECALL = ('ndcg_at_10', 'recall_at_10', 'recall_at_50', 'judged_at_10')


def load(version, split):
    return json.loads((ROOT / V[version][split] / 'report.json').read_text())


def row(label, values):
    return f'| {label} | ' + ' | '.join(f'{v:.4f}' for v in values) + ' |'


def main():
    out = []
    for split, strategy_filter in (('dev', None), ('holdout', None)):
        reports = {v: load(v, split) for v in V}
        out += [f'### {split}：全库召回对照（站点=全部）', '', '| 策略 / 版本 | nDCG@10 | Recall@10 | Recall@50 | judged@10 |', '|---|---:|---:|---:|---:|']
        for name in reports['v2']['summary']['retrieval']:
            for v in ('v1', 'v2'):
                summary = reports[v]['summary']['retrieval'].get(name)
                if summary:
                    out.append(row(f'{name} {v}', [summary['all']['metrics'][m] for m in RECALL]))
        out.append('')
    h1, h2 = load('v1', 'holdout'), load('v2', 'holdout')
    out += ['### holdout：中文派生集（200 条）', '', '| 路径 / 版本 | nDCG@10 | Recall@10 | Recall@50 | judged@10 |', '|---|---:|---:|---:|---:|']
    for v, h in (('v1', h1), ('v2', h2)):
        out.append(row(f'远端向量 {v}', [h['summary']['crosslingual']['embedding_only']['all']['metrics'][m] for m in RECALL]))
        for name in ('local_embedding', 'keyword_2gram'):
            out.append(row(f'{name} {v}', [h['crosslingual_fallback']['summary'][name]['all']['metrics'][m] for m in RECALL]))
    out += ['', '### holdout：硬约束', '', '| 版本 | 用例数 | 泄漏数 | 应为空准确率 | Recall@5 | Precision@5 |', '|---|---:|---:|---:|---:|---:|']
    for v, h in (('v1', h1), ('v2', h2)):
        s = h['summary']['constraints']['embedding_only']['all']
        out.append(f"| {v} | {s['queries']} | {s['constraint_violations']} | {s['empty_accuracy']:.4f} | {s['metrics']['recall_at_5']:.4f} | {s['metrics']['precision_at_5']:.4f} |")
    print('\n'.join(out))


main()
