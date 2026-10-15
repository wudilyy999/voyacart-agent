# 跨进程工具熔断触发与恢复

2026-10-14，整合源码 70b455a。使用一个独立本机 Redis 进程、动态 localhost 端口、关闭持久化，生产 `SharedCircuitBreakerRegistry`、`ToolResilienceMiddleware` 与真实 `FunctionTool`。配置沿用默认连续失败 3 次及冷却 60 秒；付费模型请求 0。应用、预览、容量矩阵的 Redis 和容器保持运行。

| 阶段 | 独立进程 PID | 工具体执行数 | 实际结果 |
|---|---|---|---|
| 注入工具上游连接故障 | 4653 | 3 | 三次结构化 error，共享状态打开，Redis 记录 failures=3 |
| 另一进程调用 | 4657 | 0 | 读取同一 Redis 状态后短路，返回结构化 error |
| 60 秒后恢复探测 | 5089 | 1 | 工具体观测 half_open；返回 success，共享状态闭合、Redis 键清除 |

恢复时距打开 60.918 秒。演练退出 0，Redis 正常接收 SIGTERM 并退出，未使用既有服务数据。

证据：[报告](report.json)、[运行日志](runner.log)、[Redis 原始日志](redis.log)、[源码内容指纹与默认参数](source.json)、[可复核脚本](probe.py)。三个进程的 stdout、stderr 和退出码逐阶段保存。

本次验证顺序故障注入下的跨进程共享、短路与恢复；并发半开探测竞争未执行。主模型故障仍由重试与备用模型处理，原 429／503 演练继续作为独立证据。工具体为演练替身，生产检索故障的完整业务轨迹继续由对应故障演练覆盖。
