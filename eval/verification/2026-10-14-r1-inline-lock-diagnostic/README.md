# R1 进程内模式写锁诊断

日期：2026-10-14。范围：只读核对已完成的日志、CSV、资源采样、配置、本机源码和固定镜像元数据；本轮只新增此证据目录。源码、测试、配置与历史证据保持现状，本轮测试、容器启动／停止和模型调用均未执行。镜像核对仅使用父任务允许的 `docker image inspect`。

结论：`inline-a1-w1` 在 64 用户下有 14 个日志库写锁异常组；`inline-a1-w2` 在 128 用户下同时有日志库与会话库写锁异常。两组物理数据库分别分析。当前材料能够确认异常发生于写事务的 `BEGIN IMMEDIATE`，CPU 导致持锁时间增长、线程调度不公平及长期内存增长的因果仍待测量。

## 运行与统计口径

`a1w1` 表示 1 个 API、1 个 worker，`a1w2` 表示 1 个 API、2 个 worker。两者本次均为进程内执行模式，`AGUI_QUEUE_ENABLED=0`、`QUEUE_ENABLED=1`、`AGUI_DELTA_COALESCE_MS=50`。`SEQUENCING_PERSISTENCE_ENABLED=1`，worker 仍执行各自的周期性日志租约恢复。假模型首 token 0.8 秒、后续 token 间隔 0.03 秒、回答 300 token、注入错误比例 0。

请求数、错误率、吞吐及正式完成 P95 来自原始 `runs.csv` 的全部运行记录。延迟分位数采用 nearest-rank，排除缺失时间；成功吞吐采用成功运行数除以原始记录的观察跨度。所有 6 份报告的延迟分位数已重新计算并与原 `report.json` 逐字段一致。成功样本完成 P95 仅用于区分租约恢复长尾，保留正式全样本结果。

| 运行 | 用户 | 运行／成功／错误 | 成功吞吐／秒 | 全样本完成 P95／毫秒 | 成功样本完成 P95／毫秒 |
|---|---:|---:|---:|---:|---:|
| final a1w1 | 32 | 81／81／0 | 1.45560 | 12992.095 | 12992.095 |
| final a1w1 | 64 | 135／119／16 | 2.07766 | 39117.223 | 17377.988 |
| final a1w1 | 128 | 未执行 | 未知 | 未知 | 未知 |
| final a1w2 | 64 | 140／138／2 | 2.41309 | 17708.512 | 17499.558 |
| final a1w2 | 128 | 233／0／233 | 0 | 38445.619 | 无成功样本 |
| baseline-ready a1w1 | 64 | 146／141／5 | 2.52301 | 15828.551 | 15828.551 |
| baseline-high a1w1 | 64 | 146／141／5 | 2.50997 | 16733.921 | 16635.469 |

当前 a1w1 的 32→64 用户成功吞吐增加约 42.74%，64 用户出现 11.85% 错误率。这个档位支持健康运行拐点判断；完整吞吐饱和点仍需由矩阵父任务按全档位结果判断。

## 锁异常与运行错误的对应

### a1w1，64 用户

[原始 API 日志](../2026-10-14-r1-final-matrix/inline-a1-w1/users-64/voyacart-r1-matrix-api-1.log)中的 `database is locked` 出现 14 次，此档恰好对应 14 个异常组。

- `journal.reserve`：2 组，异常栈位于 326–401、406–481 行。源路径为 `run_agent → submit → start → reserve → _db(True)`。原始 CSV 的两次 HTTP 500 完成时间为 10174.482／10177.708 毫秒，与连接设置的 10 秒等待期限接近。
- `journal.append`：12 组，源路径为 `_produce → write_events → append → _db(True)`。12 个日志头的 run_id 与 CSV 的 12 次 `SERVER_RESTART` 一一对应。
- 另外 1 次 `SERVER_RESTART` 为 `load-a94aa0c4d38b42c0b42fd57df53cd5eb`；原始日志缺少匹配 writer 异常，具体原因未知。心跳路径可能取消 producer 并产生相同错误码，该路径当前保留的信息无法证明此次触发原因。
- 1 次 `GreenletExit:` 保留为客户端停载阶段的运行失败记录；统计采用全部 135 条运行。原始 Locust 完成统计只有 133 条，正式结果采用收尾后的 `runs.csv`。

原始 writer 栈行号：494–515、518–539、542–563、565–586、589–610、612–633、635–656、666–687、695–716、718–739、760–781、783–804。完整逐组路径存于 [diagnostic.json](diagnostic.json)。本档 API 日志的 Redis 池连接异常出现次数与初始化重试标记均为 0。初始化重试计数测量的是初始化重试，SQLite 内部等待时间属于独立指标。

### a1w2，64／128 用户

64 用户的 2 个 writer 锁异常都与 2 次 `SERVER_RESTART` 一一对应。

128 用户 [原始 API 日志](../2026-10-14-r1-final-matrix/inline-a1-w2/users-128/voyacart-r1-matrix-api-1.log)中，`database is locked` 出现 318 次，按异常日志头归并为 201 个异常组。SQLAlchemy 同一异常组打印底层异常和包装异常；原始文字出现次数用于复核，分组数量用于路径分析。

| 写事务来源 | 异常组 | 物理数据库 | 示例原始日志行 |
|---|---:|---|---|
| `session_store.assert_owner` | 99 | `/app/data/voyacart.db` | 174–325、3220–3371 |
| `journal.reserve` | 15 | `/app/data/ag_ui_runs.db` | 432–508、511–587 |
| `journal.append` | 69 | `/app/data/ag_ui_runs.db` | 2416–2438、2441–2463 |
| `session_store.model_binding` | 3 | `/app/data/voyacart.db` | 1536–1640、1641–1745 |
| `session_store.bind_run_model` | 4 | `/app/data/voyacart.db` | 1865–1968、1969–2072 |
| `session_store.claim` | 6 | `/app/data/voyacart.db` | 2177–2281、5078–5182 |
| `session_store.save_claim` | 5 | `/app/data/voyacart.db` | 5510–5620、5621–5731 |

114 个 HTTP 500 异常栈分为首次归属创建 99 组与运行日志 reserve 15 组。`assert_owner` 已有归属记录时使用只读路径；本次 99 组属于新会话首次创建的写事务。

69 个 writer 异常的 run_id 都对应 CSV 的 69 次 `SERVER_RESTART`。另外 32 次 `SERVER_RESTART` 缺少匹配 writer 异常，逐条原始原因未知，run_id 列表保存在 JSON。其余 CSV 错误为 `AGENT_ERROR` 17 次、`GreenletExit:` 1 次。会话运行期写锁有 18 组，当前材料缺少全部异常与 AGENT_ERROR 的逐 run 关联，两个数量独立报告。

## 源码已经证实的机制

当前源码内容指纹与矩阵清单中对应的 journal、session_store、客户端、Locust、分析程序逐项一致；运行时与 composition 等补充源码另行记录本轮读取的指纹。

- [AGUIJournal._db](../../../app/infrastructure/ag_ui_journal.py#L112)：每次读取／写入创建一个 `aiosqlite` 连接，写入使用 `BEGIN IMMEDIATE`，等待设置为 10 秒；运行期缺少进程内写串行，初始化另有 `_init_lock`。`run`／`events` 使用 `mode=ro` 与 `BEGIN`，当前主要异常栈指向写路径。
- [AGUIJournal._append](../../../app/infrastructure/ag_ui_journal.py#L272)：同一事务中解析／修改投影、序列化 JSON、逐事件 await INSERT，然后 await 更新运行和会话投影，最后在 `_db` 中 await commit。reserve 同一事务中也执行过期恢复；renew 和周期恢复同样经过写事务。
- [SqlSessionStore._transaction](../../../app/infrastructure/persistence/sql/session_store.py#L127)：在会话库执行 `BEGIN IMMEDIATE`，持事务跨过多个 await，运行期同样缺少进程内写串行。现有 fencing、归属和版本约束均位于此事务边界内。
- 当前 composition 把 journal 放在 `/app/data/ag_ui_runs.db`；配置把会话 SQL 存储放在 `/app/data/voyacart.db`。记录工具顺序的 SQL 表位于会话数据库，两者的写争用分别处理。
- 本机 `aiosqlite 0.22.1` 的 `core.py:90` 给每个 Connection 配置独立 Thread，`176–178` 在等待连接时启动；`155–160` 把 SQL 操作送入队列并 await future；`63` 在线程内执行 SQLite 调用，`66` 把结果送回事件循环。因此 SQL 等锁发生于对应连接线程，持事务的 coroutine 仍需事件循环在多个 await 之间继续调度。日志库的读连接也会创建线程；Docker 的线程／任务采样涵盖其他线程。
- [运行心跳](../../../app/application/agent_runtime.py#L212)每 5 秒 renew，默认租约 30 秒。writer 写失败会取消 producer，等待持久租约过期恢复；心跳异常路径会取消 producer，当前缺少原异常日志。由此可解释已经匹配 writer 错误的恢复长尾；缺少匹配栈的运行保留未知归因。

## 资源数据与推断界限

CPU 按同一采样先合计 API 或 worker 角色再取峰值／中位数；进程 RSS 按容器、PID、命令分别取峰值，单位 KiB。Docker `PIDs` 表示线程／任务数量；独立 Python 进程身份采用采样中的 PID 与命令。

| 运行 | 用户 | 样本 | API CPU 峰值／中位数 | worker CPU 合计峰值／中位数 | API 线程／任务峰值 | API uvicorn RSS 峰值 |
|---|---:|---:|---:|---:|---:|---:|
| final a1w1 | 32 | 13 | 134.82%／92.49% | 0.44%／0.07% | 48 | 488412 |
| final a1w1 | 64 | 13 | 139.27%／122.07% | 0.58%／0.10% | 128 | 630004 |
| final a1w2 | 64 | 13 | 135.40%／109.27% | 1.00%／0.14% | 139 | 640204 |
| final a1w2 | 128 | 15 | 149.29%／26.00% | 0.92%／0.36% | 253 | 773452 |

实测采样间隔约 4.57–4.77 秒，包含采样命令耗时。a1w1 的 32／64 用户复用 API PID 217645；a1w2 的 64／128 用户复用 PID 322117。RSS 包含前面负载积累的驻留状态，长期内存趋势未知。worker 单进程峰值约 263036–264744 KiB；各进程数字与额外健康检查 PID 单列在 JSON。

API CPU 高峰和线程／任务增加支持 API 工作量集中这个观察。128 用户 CPU 中位数降至 26%，全程 CPU 饱和缺少证据。写锁竞争已经由实际异常栈证实。大量连接线程与任务可能延长持锁 coroutine 的调度间隔并造成不公平等待，这属于待验证推断；实际锁等待、锁持有跨度、持锁进程和事件循环延迟均未知。

历史 `baseline-ready` 和 `baseline-high` 的 64 用户各有 1 个锁异常，前者来自旧 replay 读路径，后者来自 writer。实验驱动的历史与当前分析程序内容指纹相同，客户端、Locust、假模型、矩阵脚本和 compose 文件指纹不同。选取的主要环境字段相同，但两轮客户端收尾计量和完整机器状态尚未逐项等同；因此数值可以按字段对照，严格的改造收益因果留待父任务核实。

## 基线应用与实验驱动的内容指纹

已确定两个清单的范围：

- 每轮 `manifest.json` 的 `source_fingerprints_blake2b` 由 [matrix.py](../../../scripts/loadtest/matrix.py#L21)读取运行器文件所在宿主仓库生成。`base_commit` 查询运行器工作目录的 HEAD。这两个字段描述实验驱动的源码版本；应用镜像通过独立的 `VOYACART_LOAD_IMAGE=voyacart-runtime:r1-baseline` 选择。
- [baseline-source.json](../2026-10-14-r1-capacity/baseline-source.json)单独保存基线应用的 178 个 app 文件内容指纹。本轮逐文件核对 `/tmp/voyacart-r1-baseline-20261014` 保存的应用构建上下文，178 个文件全部存在且逐项一致。基线应用 journal 内容指纹以 `ba6250f055a2f012` 开头，驱动 manifest 中 journal 的指纹以 `9d4a6b97cce47802` 开头，两个文件的职责与来源分别记录。
- 保存的旧应用源码 `events:338` 使用 `_db(True)`，`_db:117` 执行 `BEGIN IMMEDIATE`；[baseline-ready API 日志](../2026-10-14-r1-capacity/baseline-ready/inline-a1-w1/users-64/voyacart-r1-baseline-api-1.log)2339–2345 行给出同样的实际执行栈。旧应用读路径申请写锁这个结论有源码快照与运行栈共同支持。
- [baseline.Dockerfile](../2026-10-14-r1-capacity/baseline.Dockerfile)先清理 `/app/app`，再复制应用源码；[baseline-build.log](../2026-10-14-r1-capacity/baseline-build.log)记录成功构建 `ad2e274d9016` 并设置 baseline tag。原始导出版本在已有改动记录中声明为 `7f29c08`，两处初始化计数增量保存在 [baseline-instrumentation.patch](../2026-10-14-r1-capacity/baseline-instrumentation.patch)。本轮核对已有材料，导出操作保持原样。
- 本轮只读镜像元数据得到当前 baseline tag 的 ID `ad2e274d9016ba6c033b9b87b9f5167a86a9386e7d90e7c7a547a50d09d0d3f9`，创建时间 `2026-10-14T11:09:47.047601421Z`，与构建日志的前缀一致。详见 [baseline-image-observation.json](baseline-image-observation.json)。历史每轮 baseline manifest 缺少 image ID，当前 tag 观察不能追溯证明每轮 tag 状态。

历史 CSV 和报告按其实际测量保留。正文引用驱动版本时使用每轮 manifest；引用基线应用构建源码时使用 `baseline-source.json`、Dockerfile、构建日志与旧源码快照。相同宿主 journal 指纹只说明驱动文件相同；应用实际代码由对应快照与运行栈核对。

## 最小后续方向

优先在实际写事务入口内验证进程内写入排队，保留跨进程 SQLite 事务、归属校验与 fencing。journal 的 `_db(True)` 覆盖该组件的 reserve／append／renew／recover，锁的范围从连接与 `BEGIN` 之前至 commit／rollback 和连接退出之后，读路径保持原有并发。

会话库锁的覆盖范围单独确认：[composition:250–269](../../../app/composition.py#L250)中，`SqlSessionStore`、`SqlTradeStore`、`SqlConversationStore`、`SqlPreferenceStore` 共享同一 engine 与 `voyacart.db`。交易的 `_transaction` 同样执行 `BEGIN IMMEDIATE`，对话库 touch／append 与偏好库 append 各自提交。单独锁住 session_store 的事务入口能够串行当前抓到的会话栈，其余共享库 writer 继续独立提交。父任务需根据完整矩阵决定最小必要的共享范围，数据库级串行与单个 store 串行的收益分别验收。

修复效果需要使用独立新目录、相同负载和计量口径复核，记录全样本错误率、完成延迟、租约中断与写锁异常组，观察单进程及多进程的差异。当前调查提供了可执行的入口与边界，跨进程争用的收益保留待测。

本轮只完成调查与建议。具体锁范围、生命周期和多进程竞争收益由父任务实施及验收，数据库迁移保持当前范围。

## 可复核材料

- [diagnostic.json](diagnostic.json)：6 个档位的重算指标、逐异常组行号与源码帧、writer／CSV 对应、资源数据、配置摘要与历史指纹对照。
- [analyze.py](analyze.py)：标准库只读分析程序，结果输出到标准输出；重新运行时将输出保存到新证据目录。
- JSON 中 `inputs` 记录本次所有只读输入的字节数与 blake2b 内容指纹，`inputs_stable_after_read` 为 true。本轮分析前后输入保持一致。

```bash
python3 eval/verification/2026-10-14-r1-inline-lock-diagnostic/analyze.py
```
