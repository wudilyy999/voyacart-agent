"""从开发档、留出档原始 report.json 生成按站点分开的指标表；只读原始证据，不重算检索。"""
import json, sys
from pathlib import Path

LOCALES = ('all', 'us', 'es', 'jp')
RECALL = ('ndcg_at_10', 'recall_at_10', 'recall_at_50', 'judged_at_10')


def table(title, rows, metrics):
    lines = [f'#### {title}', '', '| 策略 | 站点 | 查询数 | ' + ' | '.join(metrics) + ' |', '|---|---|---:|' + '---:|' * len(metrics)]
    for name, locales in rows.items():
        for locale in LOCALES:
            if locale in locales:
                v = locales[locale]
                lines.append(f'| {name} | {locale} | {v["queries"]} | ' + ' | '.join(f'{v["metrics"][m]:.4f}' for m in metrics) + ' |')
    return '\n'.join(lines) + '\n'


def constraints(rows):
    lines = ['#### 硬约束（top_k=5）', '', '| 策略 | 站点 | 用例数 | 泄漏数 | 应为空准确率 | Recall@5 | Precision@5 |', '|---|---|---:|---:|---:|---:|---:|']
    for name, locales in rows.items():
        for locale in LOCALES:
            if locale in locales:
                v = locales[locale]; m = v['metrics']
                lines.append(f'| {name} | {locale} | {v["queries"]} | {v["constraint_violations"]} | {v["empty_accuracy"]:.4f} | {m["recall_at_5"]:.4f} | {m["precision_at_5"]:.4f} |')
    return '\n'.join(lines) + '\n'


def main(report_path):
    report = json.loads(Path(report_path).read_text())
    s = report['summary']
    out = [f'### {report["split"]}（状态 {report["status"]}）', '']
    out.append(table('全库召回（top_k=50，不传类目）', s['retrieval'], RECALL))
    out.append(table('排序（候选列表内，与 KDD Cup 任务一同口径）', s['ranking'], ('ndcg', 'ndcg_at_10')))
    out.append(constraints(s['constraints']))
    if 'crosslingual' in s:
        out.append(table('中文派生集（冻结策略）', s['crosslingual'], RECALL))
    if 'crosslingual_fallback' in report:
        out.append(table('中文派生集兜底对比（远端嵌入不可用）', report['crosslingual_fallback']['summary'], RECALL))
    for name, result in report['strategies'].items():
        if result['status'] != 'COMPLETED':
            out.append(f'- {name}：{result["status"]}，原因 {result.get("reason")}')
    print('\n'.join(out))


main(sys.argv[1])
