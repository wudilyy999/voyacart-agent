"""并发补齐 ESCI 评测远端向量索引：嵌入文本、模型、集合与 run_esci 开发档一致；超时批次重试，写入串行。
开发档随后调用原 bootstrap_product_index，按集合内已有向量复用。"""
import asyncio, json, sys, time
from dataclasses import replace
from pathlib import Path
import httpx
from app.infrastructure.embedding.openai_embedding_client import OpenAIEmbeddingClient
from app.infrastructure.persistence.seed_products import _product_from_record
from app.infrastructure.settings import load_settings
from app.infrastructure.vector.qdrant_product_index import QdrantProductIndex
from scripts.eval.run_esci import read_rows

async def main(catalog, index_dir, output, concurrency=16, attempts=4):
    settings = replace(load_settings(require_llm_key=False), data_dir=index_dir, qdrant_collection='voyacart_products_esci_eval')
    products = [_product_from_record(row) for row in read_rows(catalog)]
    embedder = OpenAIEmbeddingClient(settings); index = QdrantProductIndex(settings)
    report = {'products': len(products), 'concurrency': concurrency, 'timeout_retries': 0, 'embedded_products': 0}
    started = time.perf_counter(); gate = asyncio.Semaphore(concurrency); write = asyncio.Lock()
    try:
        pending = await index.products_needing_embeddings(products)
        report['reused_products'] = len(products) - len(pending)
        async def one(batch):
            for attempt in range(attempts):
                try:
                    async with gate:
                        vectors = await embedder.embed_batch([p.searchable_text() for p in batch])
                    break
                except httpx.TimeoutException:
                    if attempt == attempts - 1:
                        raise
                    report['timeout_retries'] += 1
            if len(vectors) != len(batch) or any(len(v) != settings.embedding_dim for v in vectors):
                raise ValueError('embedding 返回数量或维度无效')
            async with write:
                await index.ensure_ready(vector_dim=settings.embedding_dim)
                await index.upsert_products(batch, vectors)
                report['embedded_products'] += len(batch)
        async with asyncio.TaskGroup() as group:
            for start in range(0, len(pending), 10):
                group.create_task(one(pending[start:start + 10]))
        report['remaining_after'] = len(await index.products_needing_embeddings(products))
    finally:
        report['seconds'] = time.perf_counter() - started
        await index.close()
        Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

asyncio.run(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]))
