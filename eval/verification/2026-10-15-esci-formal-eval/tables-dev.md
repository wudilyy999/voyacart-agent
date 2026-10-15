### dev（状态 COMPLETED）

#### 全库召回（top_k=50，不传类目）

| 策略 | 站点 | 查询数 | ndcg_at_10 | recall_at_10 | recall_at_50 | judged_at_10 |
|---|---|---:|---:|---:|---:|---:|
| bm25 | all | 100 | 0.5516 | 0.4621 | 0.7376 | 0.7480 |
| bm25 | us | 50 | 0.5498 | 0.5048 | 0.7755 | 0.7560 |
| bm25 | es | 25 | 0.5775 | 0.4315 | 0.7434 | 0.7560 |
| bm25 | jp | 25 | 0.5294 | 0.4074 | 0.6561 | 0.7240 |
| embedding_only | all | 100 | 0.6297 | 0.5429 | 0.8128 | 0.8060 |
| embedding_only | us | 50 | 0.6362 | 0.6025 | 0.8543 | 0.8400 |
| embedding_only | es | 25 | 0.6331 | 0.4643 | 0.7667 | 0.7880 |
| embedding_only | jp | 25 | 0.6134 | 0.5024 | 0.7756 | 0.7560 |
| hybrid_only | all | 100 | 0.6286 | 0.5356 | 0.8123 | 0.8350 |
| hybrid_only | us | 50 | 0.6198 | 0.5838 | 0.8423 | 0.8440 |
| hybrid_only | es | 25 | 0.6502 | 0.4993 | 0.7840 | 0.8480 |
| hybrid_only | jp | 25 | 0.6244 | 0.4754 | 0.7804 | 0.8040 |
| keyword_2gram | all | 100 | 0.4605 | 0.3746 | 0.5718 | 0.6307 |
| keyword_2gram | us | 50 | 0.4809 | 0.4264 | 0.6412 | 0.6400 |
| keyword_2gram | es | 25 | 0.5170 | 0.4017 | 0.5821 | 0.6886 |
| keyword_2gram | jp | 25 | 0.3633 | 0.2439 | 0.4225 | 0.5543 |

#### 排序（候选列表内，与 KDD Cup 任务一同口径）

| 策略 | 站点 | 查询数 | ndcg | ndcg_at_10 |
|---|---|---:|---:|---:|
| bm25 | all | 100 | 0.8117 | 0.6593 |
| bm25 | us | 50 | 0.7962 | 0.6519 |
| bm25 | es | 25 | 0.8306 | 0.6918 |
| bm25 | jp | 25 | 0.8237 | 0.6414 |
| embedding_only | all | 100 | 0.8515 | 0.7300 |
| embedding_only | us | 50 | 0.8319 | 0.7147 |
| embedding_only | es | 25 | 0.8591 | 0.7413 |
| embedding_only | jp | 25 | 0.8830 | 0.7492 |
| hybrid_only | all | 100 | 0.8313 | 0.6949 |
| hybrid_only | us | 50 | 0.8125 | 0.6850 |
| hybrid_only | es | 25 | 0.8429 | 0.7256 |
| hybrid_only | jp | 25 | 0.8573 | 0.6841 |
| keyword_2gram | all | 100 | 0.7966 | 0.6436 |
| keyword_2gram | us | 50 | 0.7824 | 0.6469 |
| keyword_2gram | es | 25 | 0.8144 | 0.6606 |
| keyword_2gram | jp | 25 | 0.8072 | 0.6198 |

#### 硬约束（top_k=5）

| 策略 | 站点 | 用例数 | 泄漏数 | 应为空准确率 | Recall@5 | Precision@5 |
|---|---|---:|---:|---:|---:|---:|
| bm25 | all | 100 | 0 | 1.0000 | 0.5901 | 0.3356 |
| bm25 | us | 50 | 0 | 1.0000 | 0.6358 | 0.3489 |
| bm25 | es | 25 | 0 | 1.0000 | 0.5151 | 0.3909 |
| bm25 | jp | 25 | 0 | 1.0000 | 0.5663 | 0.2476 |
| embedding_only | all | 100 | 0 | 1.0000 | 0.6356 | 0.3600 |
| embedding_only | us | 50 | 0 | 1.0000 | 0.7096 | 0.3915 |
| embedding_only | es | 25 | 0 | 1.0000 | 0.5782 | 0.4091 |
| embedding_only | jp | 25 | 0 | 1.0000 | 0.5300 | 0.2381 |
| hybrid_only | all | 100 | 0 | 1.0000 | 0.6717 | 0.3689 |
| hybrid_only | us | 50 | 0 | 1.0000 | 0.7153 | 0.3830 |
| hybrid_only | es | 25 | 0 | 1.0000 | 0.5697 | 0.4000 |
| hybrid_only | jp | 25 | 0 | 1.0000 | 0.6808 | 0.3048 |
| keyword_2gram | all | 100 | 0 | 1.0000 | 0.4502 | 0.2833 |
| keyword_2gram | us | 50 | 0 | 1.0000 | 0.5210 | 0.3000 |
| keyword_2gram | es | 25 | 0 | 1.0000 | 0.3352 | 0.3000 |
| keyword_2gram | jp | 25 | 0 | 1.0000 | 0.4121 | 0.2286 |

- embedding_rerank：NOT_EXECUTED，原因 reranker_not_configured
- hybrid_rerank：NOT_EXECUTED，原因 reranker_not_configured
