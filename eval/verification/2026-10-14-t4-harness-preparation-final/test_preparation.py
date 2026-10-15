"""独立构造夹具验证场景计划逻辑；真实 ESCI 准备计划单独保留。"""
import json
from pathlib import Path
import runpy

import pytest

entry = runpy.run_path(str(Path(__file__).resolve().parents[3] / 'eval/harness/esci-v1/prepare.py'))
build_preparation, validate_preparation = entry['build_preparation'], entry['validate_preparation']


@pytest.fixture
def prepared(tmp_path):
    folder = tmp_path / 'prepared'
    folder.mkdir()
    queries, products, examples = [], [], []
    for locale in ('us', 'es', 'jp'):
        for number in range(4):
            queries.append({'locale': locale, 'query_id': number, 'query': f'{locale} query {number}', 'split': 'train'})
            for suffix in ('a', 'b'):
                asin = f'{locale}-{number}-{suffix}'
                products.append({'product_locale': locale, 'product_id': asin, 'product_title': f'Title {asin}'})
                examples.append({'product_locale': locale, 'query_id': number, 'product_id': asin,
                                 'esci_label': 'E', 'split': 'train'})
    (folder / 'selection-plan.json').write_text(json.dumps({'queries': {'dev': queries}}))
    for filename, rows in (('products.jsonl', products), ('examples.jsonl', examples)):
        (folder / filename).write_text(''.join(json.dumps(row) + '\n' for row in rows))
    return folder


def test_ten_prepared_cases_are_deterministic_and_bound_to_train_exact(prepared, tmp_path):
    first = build_preparation(prepared)
    assert first == build_preparation(prepared)
    assert first['runnable'] is False and first['case_count'] == 10 and first['model_calls'] == 0
    assert len({c['id'] for c in first['cases']}) == 10
    assert len({(c['source_query']['locale'], c['source_query']['query_id']) for c in first['cases']}) == 10
    for case in first['cases']:
        assert case['source_query']['split'] == 'train'
        assert all(p['esci_label'] == 'E' and 'product_id' not in p for p in case['source_products'])
        assert case['status'] == 'prepared' and 'final_query_selection' in case['pending_fields']
    comparison = next(c for c in first['cases'] if c['scenario'] == 'comparison')
    assert len(comparison['source_products']) == 2
    out = tmp_path / 'preparation.json'
    out.write_text(json.dumps(first))
    assert validate_preparation(out, prepared)['status'] == 'verified_preparation'
    first['cases'][0]['source_products'][0]['asin'] = 'unrelated-product'
    out.write_text(json.dumps(first))
    with pytest.raises(ValueError, match='准备计划'):
        validate_preparation(out, prepared)


@pytest.mark.parametrize('mutation', ['query_split', 'label_split', 'missing_product', 'no_exact', 'query_duplicate'])
def test_invalid_source_inputs_fail_before_preparation(prepared, mutation):
    if mutation in ('query_split', 'query_duplicate'):
        path = prepared / 'selection-plan.json'
        data = json.loads(path.read_text())
        if mutation == 'query_split':
            data['queries']['dev'][0]['split'] = 'test'
        else:
            data['queries']['dev'].append(data['queries']['dev'][0])
        path.write_text(json.dumps(data))
    else:
        path = prepared / ('products.jsonl' if mutation == 'missing_product' else 'examples.jsonl')
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if mutation == 'missing_product':
            rows.pop()
        elif mutation == 'label_split':
            rows[0]['split'] = 'test'
        else:
            for row in rows:
                row['esci_label'] = 'S'
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    with pytest.raises(ValueError):
        build_preparation(prepared)


def test_input_byte_change_invalidates_previous_plan(prepared, tmp_path):
    out = tmp_path / 'preparation.json'
    out.write_text(json.dumps(build_preparation(prepared)))
    path = prepared / 'selection-plan.json'
    path.write_text(path.read_text() + '\n')
    with pytest.raises(ValueError, match='内容指纹'):
        validate_preparation(out, prepared)
