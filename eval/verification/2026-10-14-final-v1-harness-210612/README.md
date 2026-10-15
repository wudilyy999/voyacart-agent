# 完整 v1 Harness 开发门禁

本次 `make eval-harness` 完整通过，独立 `verify` 再次返回通过。起点提交 `a6bb2d7bfda9b2f8bd4b1f6f320056fa14490d8f`；本次源码归档包含 373 个文件，与运行结束后源码逐文件一致。

| 项目 | 实际结果 |
|---|---|
| 影响检查 | 相对 `7f29c08` 要求契约及完整开发档 |
| 确定性契约 | 869 项通过，零失败、零错误、零跳过，30 个模块齐全 |
| 真实模型场景／策略组合 | 6 个场景 × current/candidate × 1 次，共 12 行，全部通过 |
| 实际模型请求 | 31 次；31 条请求 trace、31 条响应 trace、31 条已结算账本相互对应 |
| 用量完整性 | 31／31 完整，输入 342,700 token、输出 10,054 token |
| 请求与响应模型 | 全部请求 `gemini-3.8-flash-high`，31 次响应模型核对均匹配 |
| make／独立 verify | 退出码均为 0；验证通过、原因列表为空 |
| 源码稳定性 | 运行期间保持一致；当前源码与清单一致，373 个归档文件逐一核验 |
| 总执行时间 | 238.63 秒，包含契约、模型阶段及独立验证 |
| 实际费用 | 未知；供应商响应未提供实际计费金额，套件定价估算单独保留 |

本次仅运行一次完整门禁。套件、场景、超时、重试与阈值保持原值：串行执行，请求起点间隔 2 秒，模型重试 0，请求超时 45 秒，场景超时 900 秒，输出上限 2,048 token。此前失败的 `h1-dev-cost/current` 本次通过。

配置来自原工程本机被忽略的 `.env`，八项白名单仅经子进程环境注入。四项环境覆盖为 `LOCAL_EMBEDDING_FALLBACK=0`、`AGUI_QUEUE_ENABLED=0`、`AGUI_DELTA_COALESCE_MS=0`、`SEQUENCING_PERSISTENCE_ENABLED=0`。独立阿里嵌入配置随白名单传入；本套件使用临时 SQLite 和合成检索目录，真实嵌入、ESCI 质量和多进程部署由各自证据验收。本结果属于完整开发门禁，收益发布门禁另行执行。

原始证据：

- [入口参数与环境覆盖](invocation.json)
- [影响检查](impact.json)
- [make 原始输出](run.log)与[标准错误](stderr.log)
- [独立验证](verify.json)与[原始输出](verify.stdout.log)
- [实际结果及逐组合请求计数](result.json)
- [交互报告](run/report.html)
- [原始请求账本](run/attempts.jsonl)
- [逐场景证据](run/traces/)
- [契约原始输出](run/contracts.log)与[JUnit](run/contracts.xml)
- [冻结清单](run/manifest.json)与[源码归档](run/source.tar.gz)
- [已知凭据扫描计数](secret-scan.json)
