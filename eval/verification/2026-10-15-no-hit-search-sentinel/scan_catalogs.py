"""按关键词召回的同一分词规则，统计查询在各版本目录中的命中商品。

用法：PYTHONPATH=. python eval/verification/2026-10-15-no-hit-search-sentinel/scan_catalogs.py <查询> <目录...>
"""
import sys

from app.application.usecases.catalog_search import tokenize
from app.infrastructure.persistence.seed_products import build_seed_products

query, *paths = sys.argv[1:]
terms = tokenize(query)
print(f"query={query!r} terms={sorted(terms)}")
for path in paths:
    products = build_seed_products(path)
    hits = [(p.product_id, sorted(terms & tokenize(p.searchable_text())), p.title[:60])
            for p in products if terms & tokenize(p.searchable_text())]
    print(f"{path} products={len(products)} hits={len(hits)}")
    for hit in hits:
        print("  ", hit)
