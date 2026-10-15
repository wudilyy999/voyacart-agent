# ESCI 开发档评测

状态：COMPLETED。

| 组别 | 策略 | 站点 | 查询数 | 指标 |
|---|---|---|---|---|
| ranking | keyword_2gram | all | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| ranking | keyword_2gram | us | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| ranking | bm25 | all | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| ranking | bm25 | us | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| ranking | embedding_only | all | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| ranking | embedding_only | us | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| ranking | hybrid_only | all | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| ranking | hybrid_only | us | 1 | ndcg=1.0000, ndcg_at_10=1.0000 |
| retrieval | keyword_2gram | all | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9871, judged_at_10=0.7500 |
| retrieval | keyword_2gram | us | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9871, judged_at_10=0.7500 |
| retrieval | bm25 | all | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9871, judged_at_10=0.7500 |
| retrieval | bm25 | us | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9871, judged_at_10=0.7500 |
| retrieval | embedding_only | all | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9994, judged_at_10=0.7500 |
| retrieval | embedding_only | us | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9994, judged_at_10=0.7500 |
| retrieval | hybrid_only | all | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9994, judged_at_10=0.7500 |
| retrieval | hybrid_only | us | 1 | recall_at_10=1.0000, recall_at_50=1.0000, ndcg_at_10=0.9994, judged_at_10=0.7500 |
| constraints | keyword_2gram | all | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |
| constraints | keyword_2gram | us | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |
| constraints | bm25 | all | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |
| constraints | bm25 | us | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |
| constraints | embedding_only | all | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |
| constraints | embedding_only | us | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |
| constraints | hybrid_only | all | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |
| constraints | hybrid_only | us | 2 | recall_at_5=1.0000, precision_at_5=1.0000 |

embedding_rerank：未执行，原因 reranker_not_configured。

hybrid_rerank：未执行，原因 reranker_not_configured。
