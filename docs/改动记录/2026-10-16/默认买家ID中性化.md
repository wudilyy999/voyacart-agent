# 默认买家 ID 中性化

## 需求

仓库要去掉原课程工程的痕迹。默认买家 ID `pao-coder` 是原课程作者的账号名，前端页面右上角会显示它。经用户确认，新默认值为 `demo-buyer`；前端、后端、迁移脚本与测试统一使用这个值，`VITE_BUYER_ID` 仍可覆盖。

分支 `chore/demo-buyer-default` 从 main `264ef63` 开始，代码、测试、本记录和证据在同一提交中。固定买家与迁移脚本最早引入时的证据见 [fixed-buyer-20260909](../../../eval/verification/fixed-buyer-20260909/migration.json)。

## 出现位置分类

改动前 `git grep -c pao-coder` 共 28 个文件，见 [occurrences.log](../../../eval/verification/2026-10-16-demo-buyer-default/occurrences.log)：

| 类别 | 文件 | 处理 |
|---|---|---|
| 代码默认值 | `app/infrastructure/model_registry.py`、`frontend/src/App.tsx`、`frontend/src/hooks/useCommerceAgent.ts`、`frontend/src/lib/commerceClient.ts`、`scripts/migrate_local_buyer.py`（`--target` 默认值） | 改为 `demo-buyer` |
| 测试夹具 | `tests/test_fixed_buyer_persistence.py`、`frontend/tests/runRecovery.test.ts` | 改为 `demo-buyer`；前端用例里的会话 ID `pao-history` 同时改为 `demo-history` |
| 历史证据 | `eval/verification/` 下 21 个原始日志、JSON 与验收脚本 | 不改写 |

改动后，`eval/verification/` 之外已没有 `pao-coder`，前端构建产物里也没有。

## 具体变更

- 默认值：[`model_registry.py`](../../../app/infrastructure/model_registry.py) 中 `resolve()` 的 `buyer_id` 默认值；[`App.tsx`](../../../frontend/src/App.tsx) 右上角显示名；[`useCommerceAgent.ts`](../../../frontend/src/hooks/useCommerceAgent.ts) 与 [`commerceClient.ts`](../../../frontend/src/lib/commerceClient.ts) 的请求身份。生产路径上 `resolve()` 的调用方都显式传入 `buyer_id`，这个默认值只在测试直接调用 `resolve()` 时生效。
- 迁移脚本 [`migrate_local_buyer.py`](../../../scripts/migrate_local_buyer.py)：
  - `--target` 默认值改为 `demo-buyer`。
  - 迁移范围补上 `models.sqlite3`（模型配置、默认模型、显示偏好、校验票据，均按 `buyer_id` 归属）与 `shopping_forms.db`（按 `buyer` 列归属）。原脚本漏掉了这两个库，迁移后模型偏好和购物表单会留在旧 ID 下。
  - 备份文件沿用源文件权限。`models.sqlite3` 由模型注册表设为 0600，里面有 API Key 密文，备份不能放宽权限。
- 测试：[`test_fixed_buyer_persistence.py`](../../../tests/test_fixed_buyer_persistence.py) 新增 `test_migrate_covers_model_preferences_and_shopping_forms`，覆盖新纳入的两个库：迁移后 `*` 公共模型配置不变，备份权限为 0600。用改动前的脚本运行这个用例会断言失败，见 [old-migration-check.log](../../../eval/verification/2026-10-16-demo-buyer-default/old-migration-check.log)。

## 旧数据

**本机：** 只读扫描 `data/` 下迁移脚本列出的全部 SQLite 库，每张买家表中 `pao-coder` 与 `demo-buyer` 的归属行数都是 0，任意列含 `pao-coder` 的行也是 0；JSON 文件存储目录 `preferences/`、`sessions/`、`conversations/` 不存在。所以本机没有需要迁移的数据，也就没有执行迁移和备份。证据见 [local-data-scan.log](../../../eval/verification/2026-10-16-demo-buyer-default/local-data-scan.log)，扫描脚本 [scan_local_buyer.py](../../../eval/verification/2026-10-16-demo-buyer-default/scan_local_buyer.py) 只输出计数。

**其他已有 `pao-coder` 数据的安装**，二选一：

1. **迁移到新 ID：** 停服后执行

   ```bash
   uv run python -m scripts.migrate_local_buyer --source pao-coder
   ```

   脚本先把每个库整库备份到 `data/backups/buyer-migration-<UTC 时间>/`，再在一个事务里把归属改到 `demo-buyer`，报告写入备份目录的 `migration.json`。如果目标 ID 已有任何记录，脚本会拒绝合并并整体回滚。脚本只改归属，不删除数据。
2. **继续用旧 ID：** 构建前端时设置 `VITE_BUYER_ID=pao-coder`，页面以旧身份读写，不需要迁移。

升级后浏览器里缓存的身份与新默认值不一致，前端会清空本地会话缓存，并从服务端按 `demo-buyer` 恢复。没有迁移也没有设置 `VITE_BUYER_ID` 时，页面看不到旧会话，但数据仍在库里。

**回滚：** 代码回滚即恢复旧默认值。已执行迁移的安装，停服后执行 `--source demo-buyer --target pao-coder`，或把备份目录中的库文件拷回 `data/`。

## 验证

| 阶段 | 证据 | 结果 |
|---|---|---|
| 回归：后端全量（占位凭据） | [pytest.log](../../../eval/verification/2026-10-16-demo-buyer-default/pytest.log) | 2092 passed、4 skipped、0 failed，退出码 0 |
| 迁移用例复测 | [pytest-migration-retest.log](../../../eval/verification/2026-10-16-demo-buyer-default/pytest-migration-retest.log) | 全量启动后，新增用例的旧 ID 夹具由 `pao-coder` 改为 `old-buyer`，单独复测该文件 3 passed |
| 回归：前端测试 | [frontend-test.log](../../../eval/verification/2026-10-16-demo-buyer-default/frontend-test.log) | 19 个文件、250 项通过，退出码 0；包含改名后的“默认固定 demo-buyer”用例 |
| 前端构建 | [frontend-build.log](../../../eval/verification/2026-10-16-demo-buyer-default/frontend-build.log)；产物检索见 [occurrences.log](../../../eval/verification/2026-10-16-demo-buyer-default/occurrences.log) | 构建成功；产物入口脚本有 3 行含 `demo-buyer`，`pao-coder` 0 处 |
| Harness 影响 | [harness-impact.json](../../../eval/verification/2026-10-16-demo-buyer-default/harness-impact.json) | `harness_changed: true`（`model_registry.py`），要求 contracts 与 smoke |
| 离线安全契约（第一次） | [harness-contracts](../../../eval/verification/2026-10-16-demo-buyer-default/harness-contracts/report.html)，[verify 结果](../../../eval/verification/2026-10-16-demo-buyer-default/harness-contracts-verify.log) | 869 passed；之后改了测试夹具，`verify` 判定源码已变化、必须重跑 |
| 离线安全契约（复测） | [harness-contracts-rerun](../../../eval/verification/2026-10-16-demo-buyer-default/harness-contracts-rerun/report.html)，[verify 结果](../../../eval/verification/2026-10-16-demo-buyer-default/harness-contracts-rerun-verify.log) | 869 passed，证据与当前源码一致；`verify` 仍不通过，原因是只跑了 contracts 档位 |
| 真实模型冒烟 `make eval-harness` | 无 | 未执行，按 AGENTS.md 记为未通过 |

改动不涉及真实外部链路和效果验收。

## 未完成项

- 真实模型冒烟未执行。`harness impact` 按文件判定 `model_registry.py` 属于 Harness 范围；本次只改了 `resolve()` 的默认参数，生产调用方都显式传入 `buyer_id`，所以冒烟场景不会经过这个默认值。是否补跑由仓库所有者决定。
- PR 上的 `Real model evaluation` 在仓库配置 `HARNESS_LLM_API_KEY`、`HARNESS_LLM_BASE_URL` 之前会因缺少凭据失败，情况同[无命中检索测试](../2026-10-15/无命中检索测试.md)。
- 其他安装的数据迁移需要各自执行，本机没有可验证的 `pao-coder` 数据。
