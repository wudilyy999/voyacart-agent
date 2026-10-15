"""核对已交付目录的原文来源、训练标注来源与字节确定性。"""
from collections import Counter
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from app.infrastructure.persistence.seed_products import build_seed_products
from scripts.esci.build_demo_catalog import build_demo_catalog, LOCALE_COUNTS, PREPARED
from scripts.esci.catalog_records import LOCALES, plain_text
from scripts.esci.download import ROOT

evidence = Path(__file__).resolve().parent
catalog = ROOT / "data/catalog-esci-demo-2000.jsonl.gz"
with gzip.open(catalog, "rt", encoding="utf-8") as stream:
    records = [json.loads(line) for line in stream]
with (PREPARED / "products.jsonl").open(encoding="utf-8") as stream:
    products = {(row["product_locale"], row["product_id"]): row for line in stream if (row := json.loads(line))}
with (PREPARED / "examples.jsonl").open(encoding="utf-8") as stream:
    train_exact = {(row["product_locale"], row["product_id"], row["query_id"]) for line in stream
                   if (row := json.loads(line))["split"] == "train" and row["esci_label"] == "E"}
selection = json.loads((evidence / "selection.json").read_text(encoding="utf-8"))
assert len(records) == 2000
assert len({record["product_id"] for record in records}) == 2000
assert len({record["external_product_id"] for record in records}) == 2000
assert Counter(record["source_locale"] for record in records) == LOCALE_COUNTS
assert [record["product_id"] for record in records] == [f"P{number}" for number in range(100000, 102000)]
for record, basis in zip(records, selection, strict=True):
    locale, asin = record["source_locale"], record["external_product_id"]
    source = products[locale, asin]
    assert record["source_platform"] == "amazon"
    assert record["title"] == source["product_title"].strip()
    assert record["brand"] == (source["product_brand"] or "").strip()
    assert record["description"] == plain_text(source["product_description"])[:1000]
    expected_bullets = [plain_text(line)[:200] for line in (source["product_bullet_point"] or "").splitlines()]
    expected_highlights = [{"label": "要点", "detail": text} for text in expected_bullets if text][:5]
    color = plain_text(source["product_color"])
    if color:
        expected_highlights.append({"label": "颜色", "detail": color})
    assert record["highlights"] == expected_highlights
    sku = record["skus"][0]
    assert sku["spec"] == (color or "默认")
    assert sku["currency"] == LOCALES[locale][0] and sku["price_major"] > 0
    assert type(sku["stock"]) is int and sku["stock"] >= 0
    assert record["material_tags"] == []
    assert record["data_provenance"]["category_status"] == "provisional_unreviewed"
    assert record["data_provenance"]["material_status"] == "unknown"
    assert record["product_id"] == basis["product_id"] and asin == basis["asin"]
    assert all((locale, asin, query["query_id"]) in train_exact for query in basis["train_exact_queries"])
cn_stock = sum(record["skus"][0]["stock"] > 0 and "CN" in record["ships_to"] for record in records)
assert cn_stock > 0
domain_products = build_seed_products(catalog)
assert len(domain_products) == 2000
assert domain_products[0].data_provenance == records[0]["data_provenance"]
with TemporaryDirectory(prefix="voyacart-esci-demo-repeat-") as temporary:
    temporary = Path(temporary)
    build_demo_catalog(PREPARED, ROOT / "data/esci/query-class-v1.jsonl",
                       temporary / "repeat.jsonl.gz", temporary / "evidence")
    assert catalog.read_bytes() == (temporary / "repeat.jsonl.gz").read_bytes()
report = {"status": "passed", "count": 2000, "unique_asins": 2000,
          "original_text_match_count": 2000, "train_exact_source_match_count": 2000,
          "domain_loader_count": 2000, "in_stock_cn_count": cn_stock,
          "repeat_gzip_bytes_equal": True, "model_calls": 0}
(evidence / "verification-summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
