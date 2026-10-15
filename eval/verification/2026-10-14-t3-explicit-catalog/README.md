# 显式商品目录验证证据

原始错配失败保留在 [integrated-v1-recall](../2026-10-14-integrated-v1-recall/run.log)：默认 3,700 件商品用于 v1 金标，Precision 报告显示 0.572，空结果准确率 0.76，门禁 BLOCK。

| 阶段 | 结果 | 证据 |
|---|---|---|
| 修复前新增目录合同 | 4 项失败 | [日志](before/stdout.log)、[命令与内容指纹](before/run.json) |
| 修复后相关测试 | 38 项通过，零跳过 | [日志](after/stdout.log)、[JUnit](after/tests.xml)、[命令与内容指纹](after/run.json) |
| 显式 v1 完整复跑 | 150 条，PASS，输入保持一致 | [实际评测日志](../2026-10-14-integrated-v1-explicit-catalog/run.log) |

商品加载支持指定 JSONL／gzip，保留字段内的 Unicode 分隔符。CLI 测试使用只存在于指定目录中的商品，核对真实召回结果和实际输入清单。既有测试同时核对默认目录仍有 3,700 件。

复跑使用 v1 的 500 件商品、150 条金标和原批准基线，Recall 0.88、Precision 0.6365、MRR 0.888、nDCG 0.8797，空结果 25／25 正确、过滤准确率 1.0。原批准基线和门禁阈值保持原值，模型调用为 0。
