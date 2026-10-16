"""用应用默认目录与应用向量集合执行几条中文选购查询，记录命中商品与实际检索路径。"""
import asyncio
import json
from pathlib import Path

from app.application.usecases.catalog_search import CatalogSearchUseCase
from app.domain.catalog.product_search_spec import ProductSearchSpec
from app.infrastructure.embedding.openai_embedding_client import OpenAIEmbeddingClient
from app.infrastructure.persistence.in_memory_repositories import InMemoryProductRepository
from app.infrastructure.settings import load_settings
from app.infrastructure.vector.qdrant_product_index import QdrantProductIndex

QUERIES = [
    {"normalized_query": "旅行颈枕 长途飞行", "ship_to": "CN", "price_max_major": 300},
    {"normalized_query": "保温杯 不锈钢", "ship_to": "CN"},
    {"normalized_query": "儿童防晒霜", "ship_to": "CN", "price_max_major": 200},
    {"normalized_query": "无线蓝牙耳机 运动", "ship_to": "CN"},
]


async def main() -> None:
    settings = load_settings()
    index = QdrantProductIndex(settings)
    usecase = CatalogSearchUseCase(InMemoryProductRepository(), OpenAIEmbeddingClient(settings), index, None)
    results = []
    try:
        for query in QUERIES:
            result = await usecase.execute(ProductSearchSpec(top_k=3, **query))
            results.append({
                "query": query,
                "path": result.get("retrieval_path") or result.get("strategy"),
                "hits": [
                    {key: hit.get(key) for key in ("product_id", "title", "source_locale", "landed_price", "price")}
                    for hit in result["hits"]
                ],
            })
    finally:
        await index.close()
    output = Path(__file__).with_name("search-check.json")
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in results:
        print(row["query"]["normalized_query"], "| path:", row["path"])
        for hit in row["hits"]:
            print("   ", hit["product_id"], hit["source_locale"], (hit["title"] or "")[:70])


asyncio.run(main())
