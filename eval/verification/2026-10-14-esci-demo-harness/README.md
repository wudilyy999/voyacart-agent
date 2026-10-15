# 真实商品接入后的 v1 门禁首次运行

本次完整门禁未通过。`make eval-harness` 退出 2；确定性契约日志记录 869 项通过、零失败、零跳过，随后测试进程在退出时出现本机 C++ `recursive_mutex lock failed: Invalid argument` 异常，进程退出码为 -6。Harness 按进程失败中止，真实模型阶段未执行。

独立 `verify` 退出 2，拒绝原因见 `verify.json`。实际模型请求、请求与响应轨迹、结算账本均为 0；场景组合未执行。这份报告不能作为完整门禁通过证明。

源树保持冻结；373 个源码归档文件逐字核对，结果见 `result.json`。使用原工程本机环境文件的八项白名单、原供应商和 `gemini-3.8-flash-high` 配置，四项新增开关显式关闭。套件、策略、场景、重试、超时及阈值沿用原 v1 配置，未修改 `.env`，未追加模型探针或自动复跑。

配置来源及完整命令见 `invocation.json`；原始输出在 `run.log`、`stderr.log` 和 `run/contracts.log`；新报告、契约 XML、源码归档及清单保存在 `run/`。已知凭据扫描仅记录计数与路径，见 `secret-scan.json`。
