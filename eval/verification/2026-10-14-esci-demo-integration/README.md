# 2,000 件真实亚马逊商品接入验证

默认目录共 5,700 件，原 3,700 件逐字保留，新增 US 1,000／ES 500／JP 500 件真实 ESCI 原文商品。商品增强调用 0，价格、库存、配送为演示字段，类目暂定，评分／重量／材质未知。

[实际报告](report.json)记录真实 Gemini 页面查询 P100472／ASIN B079439MQW 的卡片、详情、确认和批准：订单 1，库存 114→113，重复批准不重复扣减；旧订单与 P1013-S1 库存 89 保留，错误买家 403，46 个持久事件连续。无支付或发货。截图 01—04、confirmation-before/after、repeat-approval 与 inventory-after-repeat 保留原始结果。

[源码对应](preview-source.json)核对 182 个镜像应用文件与当前源码一致。[组合目录](combined-catalog.json)记录 5,700 件、9,105 唯一 SKU 与原样例字节前缀保持。独立新向量集合 voyacart_products_esci_demo_5700，最终 index-diagnose.log 与运行核验待补商品数 0；原集合保留。原应用卷备份仅留本机，数据库和秘密文件未加入证据或 Git。

[必要复测](catalog-tests-configured.log)68 项通过、零跳过；[首次](catalog-tests.log)因两项测试缺密钥配置为 66 通过／2 失败，配置占位环境后复测成功，实际模型调用 0。前端源码未改，复用已通过的 250 项及构建。完整新门禁的两次原生库退出失败见相邻 esci-demo-harness 与 esci-demo-harness-rerun，869 契约断言通过但进程退出 -6，make／verify 2，模型阶段未执行，完整门禁未通过。

初次索引遇到请求超时，一次独立补建遇到 400，原始日志分别为 parallel-index.log 和 parallel-index-retry.log。后续实例增量同步已覆盖全部商品，400 响应正文未取得、原因未知。真实向量用量和费用未计量。核对确认 API 的首次脚本误读响应外层 status，引发 KeyError，原 stderr 保留；按原服务的 confirmation 包装读取后成功，应用无此项修改。

本次更新使用独立镜像 voyacart-runtime:esci-demo-2000-20261014、原项目和持久卷。供应商 1 Gemini／阿里向量及原回退配置按原环境载入，容器将本机网关地址改为宿主机可达地址；.env 保持原样。旧 mock 服务保留，当前页面默认真实模型。
