# 隔离部署验收准备

本目录保留 2026-10-14 的配置解析与源码准备证据。用户随后要求本轮约 30 分钟交付，干净部署留待后续。

- 配置检查：安全环境白名单、`--env-file /dev/null`、独立项目与端口、假模型配置；两项配置解析退出码均为 0。
- 源码准备：从提交 `70b455ad2dbc848edfabd544da576614a8e3866d` 导出跟踪文件，临时目录 `/tmp/voyacart-clean-scale-source-20261014.9zLyGo`；包含构建输入、默认 3,700 件商品、知识、Prompt、Skill 源码、前端媒体及 ARM 兼容覆盖。
- 凭据与本机数据：导出目录没有本机 `.env`、依赖软链接或运行数据库；配置使用假模型测试值，业务外部服务配置为空。
- 实际构建、容器启动、页面选购、持久恢复和运行健康验收：未执行。
- 取消时核对：该独立项目没有容器；部署启动进程从未创建。原预览和其它项目保持原状态。

配置可解析只证明准备步骤通过。后续实际验收计划在同一 Docker 主机使用新项目、新卷与新镜像标记；主机已有构建层缓存，这一计划不能代替物理新机器验收。

证据包括 `preparation.json`、`preflight.json`、`isolation-config.json`、`config-quiet.stdout`、`config-quiet.stderr`、`config-json.stdout`、`config-json.stderr`、`source-files.json`、`isolated-image-override.json` 和 `deferred-status.json`。
