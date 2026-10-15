"""缓存模型与真实本地 Qdrant 的小规模诊断；结果不作为 ESCI 质量基线。"""
import argparse
import asyncio
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform
import statistics
import tempfile
import time

from app.application.usecases.catalog_search import CatalogSearchUseCase
from app.domain.catalog.product_search_spec import ProductSearchSpec
from app.infrastructure.embedding.local_multilingual import LocalMultilingualEmbedding
from app.infrastructure.persistence.in_memory_repositories import InMemoryProductRepository
from app.infrastructure.persistence.seed_products import _product_from_record
from app.infrastructure.vector.index_bootstrap import bootstrap_product_index
from app.infrastructure.vector.qdrant_product_index import QdrantProductIndex
from tests.test_retrieval import BrokenEmbeddingClient, _settings


async def main(cache):
    root = Path.cwd()
    output = Path(__file__).resolve().parent
    records = [json.loads(line) for line in (root / "data/catalog-v3.jsonl").read_text().splitlines()]
    selected = [p for language in ("en", "es", "ja")
                for p in [r for r in records if r.get("source_language") == language][:100:4]]
    repo = InMemoryProductRepository([_product_from_record(p) for p in selected])
    started = time.perf_counter()
    model = LocalMultilingualEmbedding(cache, local_files_only=True)
    report = {"scope": "75 existing synthetic catalog products; operational diagnostic",
        "model": model.model_name, "dimension": model.dimension, "version": model.version,
        "model_load_seconds": time.perf_counter() - started,
        "machine": platform.platform(), "processor": platform.processor()}
    with tempfile.TemporaryDirectory() as directory:
        settings = replace(_settings(Path(directory)), embedding_base_url="local://fastembed",
            embedding_model=model.model_name, embedding_dim=model.dimension, embedding_version=model.version)
        index = QdrantProductIndex(settings)
        try:
            started = time.perf_counter()
            report["bootstrap"] = {}
            assert await bootstrap_product_index(repo, model, index, report=report["bootstrap"])
            report["index_seconds"] = time.perf_counter() - started
            report["bootstrap_reuse"] = {}
            assert await bootstrap_product_index(repo, BrokenEmbeddingClient(), index, report=report["bootstrap_reuse"])
            search = CatalogSearchUseCase(repo, embedder=BrokenEmbeddingClient(), vector_index=index,
                local_embedder=model, local_vector_index=index)
            latencies, examples = [], []
            for _ in range(10):
                for query in ("轻便旅行背包", "保温水杯", "降噪耳机"):
                    started = time.perf_counter()
                    result = await search.execute(ProductSearchSpec(normalized_query=query, top_k=3))
                    latencies.append(time.perf_counter() - started)
                    assert result["recall_strategy"] == "local_embedding"
                    assert result["hits"]
                    if len(examples) < 3:
                        examples.append({"query": query, "strategy": result["recall_strategy"],
                            "hits": [{"id": h["product_id"], "title": h["title"]} for h in result["hits"]]})
            report.update(queries=len(latencies), query_seconds=latencies,
                p50_seconds=statistics.median(latencies), p95_seconds=sorted(latencies)[28], examples=examples)
            # 并发请求与长文本共用同一分块编码实现。
            vectors = await asyncio.gather(*(model.embed("旅行背包与保温水杯" * (i * 40 + 1)) for i in range(4)))
            assert all(len(v) == model.dimension for v in vectors)
            report["concurrent_long_texts"] = len(vectors)
        finally:
            await index.close()
    paths = ["app/infrastructure/embedding/local_multilingual.py", "app/application/usecases/catalog_search.py",
        "app/composition.py", "app/infrastructure/settings.py", "data/catalog-v3.jsonl"]
    report["source_fingerprints_blake2b"] = {p: hashlib.blake2b((root / p).read_bytes()).hexdigest() for p in paths}
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("index_seconds", "queries", "p50_seconds", "p95_seconds", "concurrent_long_texts")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    asyncio.run(main(parser.parse_args().cache))
