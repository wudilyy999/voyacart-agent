"""预建中文派生集兜底对比用的本地多语种索引；设置取自 run_esci.local_index_settings，留出档复用已写入的向量。"""
import asyncio, json, sys, time
from pathlib import Path
from app.infrastructure.embedding.local_multilingual import LocalMultilingualEmbedding
from app.infrastructure.persistence.in_memory_repositories import InMemoryProductRepository
from app.infrastructure.persistence.seed_products import _product_from_record
from app.infrastructure.settings import load_settings
from app.infrastructure.vector.index_bootstrap import bootstrap_product_index
from app.infrastructure.vector.qdrant_product_index import QdrantProductIndex
from scripts.eval.run_esci import local_index_settings, read_rows

async def main(catalog, index_dir, model_dir, output):
    model = LocalMultilingualEmbedding(model_dir, local_files_only=True)
    settings = local_index_settings(load_settings(require_llm_key=False), index_dir, model)
    products = [_product_from_record(row) for row in read_rows(catalog)]
    index = QdrantProductIndex(settings); report = {}; started = time.perf_counter()
    try:
        complete = await bootstrap_product_index(InMemoryProductRepository(products), model, index, report=report)
    finally:
        await index.close()
    report.update(seconds=time.perf_counter() - started, complete=complete, products=len(products),
                  model=model.model_name, version=model.version, dimension=model.dimension)
    Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

asyncio.run(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]))
