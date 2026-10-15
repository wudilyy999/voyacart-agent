"""独立初建任务：复用运行时缓存和索引，为当前新增目录补齐向量。"""
import asyncio
import json
from app.infrastructure.settings import load_settings
from app.infrastructure.persistence.seed_products import build_seed_products
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.embedding.openai_embedding_client import OpenAIEmbeddingClient
from app.infrastructure.vector.embedding_identity import embedding_identity
from app.infrastructure.vector.qdrant_product_index import QdrantProductIndex
from app.infrastructure.cache.cached_embedding_client import CachedEmbeddingClient

async def main():
    settings = load_settings()
    cache = RedisCache(settings.redis_url)
    embedder = CachedEmbeddingClient(OpenAIEmbeddingClient(settings, timeout_seconds=90), cache, embedding_identity(settings))
    index = QdrantProductIndex(settings)
    products = build_seed_products()
    pending = await index.products_needing_embeddings(products)
    queue = asyncio.Queue()
    for start in range(0, len(pending), 10):
        queue.put_nowait(pending[start:start + 10])
    written = 0
    async def worker():
        nonlocal written
        while not queue.empty():
            batch = queue.get_nowait()
            vectors = await embedder.embed_batch([p.searchable_text() for p in batch])
            await index.ensure_ready(vector_dim=len(vectors[0]))
            await index.upsert_products(batch, vectors)
            written += len(batch)
            if written % 100 == 0:
                print(json.dumps({"written": written, "pending_at_start": len(pending)}), flush=True)
    try:
        async with asyncio.TaskGroup() as tasks:
            for _ in range(8):
                tasks.create_task(worker())
        remaining = await index.products_needing_embeddings(products)
        print(json.dumps({"products": len(products), "pending_at_start": len(pending), "written": written, "remaining": len(remaining), "concurrency": 8}), flush=True)
        assert not remaining
    finally:
        await index.close()
        await cache.close()

asyncio.run(main())
