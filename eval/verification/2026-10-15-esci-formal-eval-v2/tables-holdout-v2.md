### holdout（状态 COMPLETED）

#### 全库召回（top_k=50，不传类目）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| embedding_only | all | 300 | 0.6131 | 0.5018 | 0.7995 | 0.7927 |
| embedding_only | us | 150 | 0.6319 | 0.5642 | 0.8332 | 0.8093 |
| embedding_only | es | 75 | 0.5867 | 0.4458 | 0.7651 | 0.7867 |
| embedding_only | jp | 75 | 0.6020 | 0.4328 | 0.7667 | 0.7653 |

#### 排序（候选列表内，与 KDD Cup 任务一同口径）

| 策略 | 站点 | 查询数 | ndcg | ndcg_at_10 |
|---|---|---:|---:|---:|
| embedding_only | all | 300 | 0.8528 | 0.7334 |
| embedding_only | us | 150 | 0.8505 | 0.7466 |
| embedding_only | es | 75 | 0.8394 | 0.7010 |
| embedding_only | jp | 75 | 0.8708 | 0.7394 |

#### 硬约束（top_k=5）

| 策略 | 站点 | 用例数 | 泄漏数 | 应为空准确率 | Recall@5 | Precision@5 |
|---|---|---:|---:|---:|---:|---:|
| embedding_only | all | 300 | 0 | 1.0000 | 0.5912 | 0.3081 |
| embedding_only | us | 150 | 0 | 1.0000 | 0.6060 | 0.2851 |
| embedding_only | es | 75 | 0 | 1.0000 | 0.5416 | 0.3175 |
| embedding_only | jp | 75 | 0 | 1.0000 | 0.6068 | 0.3485 |

#### 中文派生集（冻结策略）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| embedding_only | all | 200 | 0.5075 | 0.4240 | 0.7054 | 0.6565 |
| embedding_only | us | 100 | 0.5621 | 0.5031 | 0.7731 | 0.7280 |
| embedding_only | es | 50 | 0.4834 | 0.3597 | 0.6636 | 0.6360 |
| embedding_only | jp | 50 | 0.4222 | 0.3302 | 0.6116 | 0.5340 |

#### 中文派生集兜底对比（远端嵌入不可用）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| keyword_2gram | all | 200 | 0.1281 | 0.1138 | 0.1734 | 0.1718 |
| keyword_2gram | us | 100 | 0.1041 | 0.1042 | 0.1470 | 0.1310 |
| keyword_2gram | es | 50 | 0.1304 | 0.1216 | 0.1621 | 0.1870 |
| keyword_2gram | jp | 50 | 0.1737 | 0.1254 | 0.2376 | 0.2383 |
| local_embedding | all | 200 | 0.2067 | 0.1560 | 0.3685 | 0.2910 |
| local_embedding | us | 100 | 0.1868 | 0.1496 | 0.3881 | 0.2770 |
| local_embedding | es | 50 | 0.1998 | 0.1561 | 0.4004 | 0.3060 |
| local_embedding | jp | 50 | 0.2531 | 0.1687 | 0.2972 | 0.3040 |

