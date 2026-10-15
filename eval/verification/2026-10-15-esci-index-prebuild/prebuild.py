"""预建 ESCI 评测远端向量索引；设置与 run_esci 开发档一致，开发档随后复用已写入的向量。"""
import asyncio, json, sys, time
from dataclasses import replace
from pathlib import Path
from app.infrastructure.embedding.openai_embedding_client import OpenAIEmbeddingClient
from app.infrastructure.persistence.in_memory_repositories import InMemoryProductRepository
from app.infrastructure.settings import load_settings
from app.infrastructure.vector.index_bootstrap import bootstrap_product_index
from app.infrastructure.vector.qdrant_product_index import QdrantProductIndex
from scripts.eval.run_esci import read_rows
from app.infrastructure.persistence.seed_products import _product_from_record

async def main(catalog, index_dir, output):
    settings = replace(load_settings(require_llm_key=False), data_dir=index_dir, qdrant_collection='voyacart_products_esci_eval')
    products = [_product_from_record(row) for row in read_rows(catalog)]
    index = QdrantProductIndex(settings); report = {}; started = time.perf_counter()
    try:
        complete = await bootstrap_product_index(InMemoryProductRepository(products), OpenAIEmbeddingClient(settings), index, report=report)
    finally:
        await index.close()
    report.update(seconds=time.perf_counter() - started, complete=complete, products=len(products),
                  embedding_model=settings.embedding_model, qdrant_url_configured=bool(settings.qdrant_url))
    Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

asyncio.run(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]))
