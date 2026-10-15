### dev（状态 COMPLETED）

#### 全库召回（top_k=50，不传类目）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| bm25 | all | 100 | 0.5498 | 0.4569 | 0.7356 | 0.7610 |
| bm25 | us | 50 | 0.5596 | 0.5133 | 0.7914 | 0.7920 |
| bm25 | es | 25 | 0.5321 | 0.3698 | 0.6939 | 0.7160 |
| bm25 | jp | 25 | 0.5480 | 0.4314 | 0.6656 | 0.7440 |
| embedding_only | all | 100 | 0.6410 | 0.5403 | 0.8005 | 0.8130 |
| embedding_only | us | 50 | 0.6569 | 0.6040 | 0.8568 | 0.8580 |
| embedding_only | es | 25 | 0.6319 | 0.4354 | 0.7381 | 0.7880 |
| embedding_only | jp | 25 | 0.6182 | 0.5179 | 0.7503 | 0.7480 |
| hybrid_only | all | 100 | 0.6305 | 0.5279 | 0.8148 | 0.8400 |
| hybrid_only | us | 50 | 0.6261 | 0.5757 | 0.8581 | 0.8640 |
| hybrid_only | es | 25 | 0.6305 | 0.4649 | 0.7646 | 0.8200 |
| hybrid_only | jp | 25 | 0.6394 | 0.4954 | 0.7785 | 0.8120 |
| keyword_2gram | all | 100 | 0.4555 | 0.3609 | 0.5879 | 0.6336 |
| keyword_2gram | us | 50 | 0.4713 | 0.4098 | 0.6769 | 0.6600 |
| keyword_2gram | es | 25 | 0.4857 | 0.3480 | 0.5472 | 0.6600 |
| keyword_2gram | jp | 25 | 0.3939 | 0.2759 | 0.4505 | 0.5543 |

#### 排序（候选列表内，与 KDD Cup 任务一同口径）

| 策略 | 站点 | 查询数 | ndcg | ndcg_at_10 |
|---|---|---:|---:|---:|
| bm25 | all | 100 | 0.8154 | 0.6589 |
| bm25 | us | 50 | 0.7957 | 0.6491 |
| bm25 | es | 25 | 0.8393 | 0.6795 |
| bm25 | jp | 25 | 0.8310 | 0.6579 |
| embedding_only | all | 100 | 0.8644 | 0.7458 |
| embedding_only | us | 50 | 0.8488 | 0.7405 |
| embedding_only | es | 25 | 0.8733 | 0.7448 |
| embedding_only | jp | 25 | 0.8865 | 0.7576 |
| hybrid_only | all | 100 | 0.8435 | 0.7104 |
| hybrid_only | us | 50 | 0.8223 | 0.7006 |
| hybrid_only | es | 25 | 0.8577 | 0.7362 |
| hybrid_only | jp | 25 | 0.8719 | 0.7040 |
| keyword_2gram | all | 100 | 0.8042 | 0.6454 |
| keyword_2gram | us | 50 | 0.7819 | 0.6377 |
| keyword_2gram | es | 25 | 0.8248 | 0.6542 |
| keyword_2gram | jp | 25 | 0.8281 | 0.6521 |

#### 硬约束（top_k=5）

| 策略 | 站点 | 用例数 | 泄漏数 | 应为空准确率 | Recall@5 | Precision@5 |
|---|---|---:|---:|---:|---:|---:|
| bm25 | all | 100 | 0 | 1.0000 | 0.5381 | 0.3089 |
| bm25 | us | 50 | 0 | 1.0000 | 0.5856 | 0.3149 |
| bm25 | es | 25 | 0 | 1.0000 | 0.4097 | 0.3545 |
| bm25 | jp | 25 | 0 | 1.0000 | 0.5663 | 0.2476 |
| embedding_only | all | 100 | 0 | 1.0000 | 0.5763 | 0.3348 |
| embedding_only | us | 50 | 0 | 1.0000 | 0.6899 | 0.3730 |
| embedding_only | es | 25 | 0 | 1.0000 | 0.4120 | 0.3455 |
| embedding_only | jp | 25 | 0 | 1.0000 | 0.4943 | 0.2381 |
| hybrid_only | all | 100 | 0 | 1.0000 | 0.6281 | 0.3422 |
| hybrid_only | us | 50 | 0 | 1.0000 | 0.6770 | 0.3489 |
| hybrid_only | es | 25 | 0 | 1.0000 | 0.4581 | 0.3545 |
| hybrid_only | jp | 25 | 0 | 1.0000 | 0.6967 | 0.3143 |
| keyword_2gram | all | 100 | 0 | 1.0000 | 0.4259 | 0.2654 |
| keyword_2gram | us | 50 | 0 | 1.0000 | 0.4912 | 0.2660 |
| keyword_2gram | es | 25 | 0 | 1.0000 | 0.2544 | 0.2864 |
| keyword_2gram | jp | 25 | 0 | 1.0000 | 0.4598 | 0.2421 |

- embedding_rerank：NOT_EXECUTED，原因 reranker_not_configured
- hybrid_rerank：NOT_EXECUTED，原因 reranker_not_configured
