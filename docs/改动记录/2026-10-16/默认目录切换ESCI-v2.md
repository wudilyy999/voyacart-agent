# 默认目录切换为 ESCI v2

## 需求

应用默认商品目录从 `catalog-demo.jsonl.gz`（3,700 件原合成样例 + 2,000 件 ESCI 商品，共 5,700 件）切换为 ESCI v2 的 12,299 件真实商品，并重建应用向量索引。

## 具体变更

- `app/infrastructure/persistence/seed_products.py`：默认目录改为 `catalog-esci-v2.jsonl.gz`（容器内 `catalog/`，本地 `data/`）。原样例与历史评测继续显式选择各自目录，`catalog-demo.jsonl.gz` 保留。
- `Dockerfile`、`.dockerignore`：镜像改为打包 `data/catalog-esci-v2.jsonl.gz`。
- `README.md`：注明默认目录构成，补充向量索引补齐命令。
- 依赖原默认目录中合成商品的测试改为显式绑定 `catalog-demo.jsonl.gz`，详见下文“测试”。

## 编号复用与已有数据

v2 的商品编号为 P100000–P112298。原 demo 目录中 2,000 件 ESCI 商品同样使用 P100000–P101999，但两份目录在这些编号上对应的是不同商品（0/2,000 相同）。库存初始化按 SKU 编号保留已扣减库存，只刷新标题与报价，无法识别“同编号换了商品”。

- 本机现有 `data/voyacart.db`：7,105 条库存记录全部来自更早的合成目录，P100000–P101999 区间 0 条，订单 0 条，不受影响。
- 曾以 demo 目录运行过的环境（如旧的 Compose 数据卷）切换前应使用新的数据卷，否则这 2,000 个编号的库存、订单和收藏会对应到新目录的其他商品。

## 应用向量索引

- 本机开发依赖的 Qdrant / Redis 原容器已停止，新建 `voyacart-dev-qdrant`（127.0.0.1:6333）与 `voyacart-dev-redis`（127.0.0.1:16379，AOF）及新数据卷，端口与 `.env` 一致。
- 首次同步在第一次嵌入请求即连接超时，0 件写入：[首次失败](../../../eval/verification/2026-10-16-app-index-esci-v2-first-timeout/)。网络复测正常后重跑。
- 重跑改为逐批 10 件顺序嵌入，约 4 件/秒，预计 50 分钟；写入 210 件后停止：[停止记录](../../../eval/verification/2026-10-16-app-index-esci-v2-stopped-sequential/)。
- ESCI v2 评测索引由同一建库代码生成，点结构与 `embedding_key` 一致，因此将 12,299 个点复制到应用集合 `voyacart_products`（7.6 秒）：[复制记录](../../../eval/verification/2026-10-16-app-index-esci-v2/copy-from-eval-index.log)。
- 随后用应用同步脚本核对：12,299 件全部按文本指纹与模型复用，嵌入调用 0，`complete=true`：[同步报告](../../../eval/verification/2026-10-16-app-index-esci-v2/sync-report.json)。

## 验证

- 默认目录加载：12,299 件、SKU 无重复、11,069 件有库存、9 个类目。
- 中文检索抽查（应用检索用例 + 应用索引，未配置精排）：“旅行颈枕 长途飞行”“无线蓝牙耳机 运动”返回相关的美国站原文商品；“儿童防晒霜”在寄往中国、200 元以内条件下未命中防晒类商品：[抽查结果](../../../eval/verification/2026-10-16-app-index-esci-v2/search-check.json)。
- 日本站 3,768 个标题中有 8 个是 ESCI 原始数据自带的乱码（v1、demo 同样存在），按原文保留规则未改动。
- 后端测试结果见下文“测试”。前端未改动。

## 测试

- 切换默认目录后首轮后端全量：70 项失败、4 项报错、2017 项通过。失败用例均以原合成样例为前提（P1001、P1003 等编号与固定报价、旅行类合成商品）。
- 新增 `tests/conftest.py`：会话级固定把测试使用的默认目录指向 `catalog-demo.jsonl.gz`，与这些用例的编写前提一致；应用默认目录不受影响。
- `tests/test_runtime_distribution.py`：镜像打包断言改为 v2，并新增“默认目录为 ESCI v2、12,299 件、三站点”断言。
- 修复后复跑首轮失败与报错的 31 个测试函数（参数化后 45 项）：全部通过。
- 第二轮全量 1 项失败、2091 项通过：`test_catalog_fixture.py` 在导入时取得默认目录常量，校验的却是 demo 目录构成。改为显式读取 `catalog-demo.jsonl.gz` 并更名为 `test_demo_catalog_adds_real_amazon_products_and_preserves_existing_records`：[第二轮日志](../../../eval/verification/2026-10-16-app-index-esci-v2/pytest-before-fixture-test.log)。
- 最终后端全量：2092 项通过、4 项跳过、0 失败，见 [pytest.log](../../../eval/verification/2026-10-16-app-index-esci-v2/pytest.log)。

## 启用与回滚

合并后默认生效。回滚时把默认目录改回 `catalog-demo.jsonl.gz`，并使用与该目录匹配的数据卷和向量集合。
