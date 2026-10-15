### holdout（状态 COMPLETED）

#### 全库召回（top_k=50，不传类目）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| embedding_only | all | 300 | 0.6120 | 0.5239 | 0.8029 | 0.7950 |
| embedding_only | us | 150 | 0.6295 | 0.5882 | 0.8327 | 0.8013 |
| embedding_only | es | 75 | 0.5769 | 0.4595 | 0.7748 | 0.7707 |
| embedding_only | jp | 75 | 0.6122 | 0.4595 | 0.7715 | 0.8067 |

#### 排序（候选列表内，与 KDD Cup 任务一同口径）

| 策略 | 站点 | 查询数 | ndcg | ndcg_at_10 |
|---|---|---:|---:|---:|
| embedding_only | all | 300 | 0.8459 | 0.7268 |
| embedding_only | us | 150 | 0.8414 | 0.7400 |
| embedding_only | es | 75 | 0.8360 | 0.7094 |
| embedding_only | jp | 75 | 0.8647 | 0.7178 |

#### 硬约束（top_k=5）

| 策略 | 站点 | 用例数 | 泄漏数 | 应为空准确率 | Recall@5 | Precision@5 |
|---|---|---:|---:|---:|---:|---:|
| embedding_only | all | 300 | 0 | 1.0000 | 0.6082 | 0.3148 |
| embedding_only | us | 150 | 0 | 1.0000 | 0.6061 | 0.2780 |
| embedding_only | es | 75 | 0 | 1.0000 | 0.5993 | 0.3238 |
| embedding_only | jp | 75 | 0 | 1.0000 | 0.6213 | 0.3848 |

#### 中文派生集（冻结策略）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| embedding_only | all | 200 | 0.4967 | 0.4104 | 0.6988 | 0.6420 |
| embedding_only | us | 100 | 0.5398 | 0.4664 | 0.7417 | 0.7070 |
| embedding_only | es | 50 | 0.4795 | 0.3915 | 0.7032 | 0.5980 |
| embedding_only | jp | 50 | 0.4276 | 0.3172 | 0.6088 | 0.5560 |

#### 中文派生集兜底对比（远端嵌入不可用）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| keyword_2gram | all | 200 | 0.1100 | 0.1013 | 0.1522 | 0.1521 |
| keyword_2gram | us | 100 | 0.0797 | 0.0830 | 0.1162 | 0.1068 |
| keyword_2gram | es | 50 | 0.1194 | 0.1191 | 0.1486 | 0.1630 |
| keyword_2gram | jp | 50 | 0.1613 | 0.1201 | 0.2279 | 0.2320 |
| local_embedding | all | 200 | 0.2386 | 0.1807 | 0.3780 | 0.3165 |
| local_embedding | us | 100 | 0.2075 | 0.1797 | 0.3879 | 0.2960 |
| local_embedding | es | 50 | 0.2559 | 0.1897 | 0.4192 | 0.3380 |
| local_embedding | jp | 50 | 0.2834 | 0.1738 | 0.3170 | 0.3360 |

