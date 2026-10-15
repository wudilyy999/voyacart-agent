# F1 商品卡片组件验收

使用实际组件与 ESCI 的 us/es/jp 原文样例。价格、库存、配送为演示值，订单为组件验证样例。

- shopping.jpg、comparison.jpg、detail.jpg、history.jpg、orders.jpg、favorites.jpg：1280×900 桌面视口。
- shopping-mobile.jpg：319px 窄视口。
- review.tsx、review-data.json、review.html：视觉验收入口与样例，运行时放入 frontend/.cache/。
- frontend-tests.log：首次测试中旧 CSS 选择器引发 3 项失败，保留原始日志。
- ../2026-10-14-f1-product-cards-rerun/：修正选择器后 246 项测试通过，构建日志单独记录。

截图验证组件布局与数据展示；默认目录仍为旧目录，真实模型完整选购尚待后端整合验收。
