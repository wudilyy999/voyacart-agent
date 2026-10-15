# ESCI 开发档评测

状态：COMPLETED。

| 组别 | 策略 | 站点 | 查询数 | 指标 |
|---|---|---|---|---|
| ranking | keyword_2gram | all | 100 | ndcg=0.7966, ndcg_at_10=0.6436 |
| ranking | keyword_2gram | us | 50 | ndcg=0.7824, ndcg_at_10=0.6469 |
| ranking | keyword_2gram | es | 25 | ndcg=0.8144, ndcg_at_10=0.6606 |
| ranking | keyword_2gram | jp | 25 | ndcg=0.8072, ndcg_at_10=0.6198 |
| ranking | bm25 | all | 100 | ndcg=0.8117, ndcg_at_10=0.6593 |
| ranking | bm25 | us | 50 | ndcg=0.7962, ndcg_at_10=0.6519 |
| ranking | bm25 | es | 25 | ndcg=0.8306, ndcg_at_10=0.6918 |
| ranking | bm25 | jp | 25 | ndcg=0.8237, ndcg_at_10=0.6414 |
| ranking | embedding_only | all | 100 | ndcg=0.8515, ndcg_at_10=0.7300 |
| ranking | embedding_only | us | 50 | ndcg=0.8319, ndcg_at_10=0.7147 |
| ranking | embedding_only | es | 25 | ndcg=0.8591, ndcg_at_10=0.7413 |
| ranking | embedding_only | jp | 25 | ndcg=0.8830, ndcg_at_10=0.7492 |
| ranking | hybrid_only | all | 100 | ndcg=0.8313, ndcg_at_10=0.6949 |
| ranking | hybrid_only | us | 50 | ndcg=0.8125, ndcg_at_10=0.6850 |
| ranking | hybrid_only | es | 25 | ndcg=0.8429, ndcg_at_10=0.7256 |
| ranking | hybrid_only | jp | 25 | ndcg=0.8573, ndcg_at_10=0.6841 |
| retrieval | keyword_2gram | all | 100 | recall_at_10=0.3746, recall_at_50=0.5718, ndcg_at_10=0.4605, judged_at_10=0.6307 |
| retrieval | keyword_2gram | us | 50 | recall_at_10=0.4264, recall_at_50=0.6412, ndcg_at_10=0.4809, judged_at_10=0.6400 |
| retrieval | keyword_2gram | es | 25 | recall_at_10=0.4017, recall_at_50=0.5821, ndcg_at_10=0.5170, judged_at_10=0.6886 |
| retrieval | keyword_2gram | jp | 25 | recall_at_10=0.2439, recall_at_50=0.4225, ndcg_at_10=0.3633, judged_at_10=0.5543 |
| retrieval | bm25 | all | 100 | recall_at_10=0.4621, recall_at_50=0.7376, ndcg_at_10=0.5516, judged_at_10=0.7480 |
| retrieval | bm25 | us | 50 | recall_at_10=0.5048, recall_at_50=0.7755, ndcg_at_10=0.5498, judged_at_10=0.7560 |
| retrieval | bm25 | es | 25 | recall_at_10=0.4315, recall_at_50=0.7434, ndcg_at_10=0.5775, judged_at_10=0.7560 |
| retrieval | bm25 | jp | 25 | recall_at_10=0.4074, recall_at_50=0.6561, ndcg_at_10=0.5294, judged_at_10=0.7240 |
| retrieval | embedding_only | all | 100 | recall_at_10=0.5429, recall_at_50=0.8128, ndcg_at_10=0.6297, judged_at_10=0.8060 |
| retrieval | embedding_only | us | 50 | recall_at_10=0.6025, recall_at_50=0.8543, ndcg_at_10=0.6362, judged_at_10=0.8400 |
| retrieval | embedding_only | es | 25 | recall_at_10=0.4643, recall_at_50=0.7667, ndcg_at_10=0.6331, judged_at_10=0.7880 |
| retrieval | embedding_only | jp | 25 | recall_at_10=0.5024, recall_at_50=0.7756, ndcg_at_10=0.6134, judged_at_10=0.7560 |
| retrieval | hybrid_only | all | 100 | recall_at_10=0.5356, recall_at_50=0.8123, ndcg_at_10=0.6286, judged_at_10=0.8350 |
| retrieval | hybrid_only | us | 50 | recall_at_10=0.5838, recall_at_50=0.8423, ndcg_at_10=0.6198, judged_at_10=0.8440 |
| retrieval | hybrid_only | es | 25 | recall_at_10=0.4993, recall_at_50=0.7840, ndcg_at_10=0.6502, judged_at_10=0.8480 |
| retrieval | hybrid_only | jp | 25 | recall_at_10=0.4754, recall_at_50=0.7804, ndcg_at_10=0.6244, judged_at_10=0.8040 |
| constraints | keyword_2gram | all | 100 | recall_at_5=0.4502, precision_at_5=0.2833 |
| constraints | keyword_2gram | us | 50 | recall_at_5=0.5210, precision_at_5=0.3000 |
| constraints | keyword_2gram | es | 25 | recall_at_5=0.3352, precision_at_5=0.3000 |
| constraints | keyword_2gram | jp | 25 | recall_at_5=0.4121, precision_at_5=0.2286 |
| constraints | bm25 | all | 100 | recall_at_5=0.5901, precision_at_5=0.3356 |
| constraints | bm25 | us | 50 | recall_at_5=0.6358, precision_at_5=0.3489 |
| constraints | bm25 | es | 25 | recall_at_5=0.5151, precision_at_5=0.3909 |
| constraints | bm25 | jp | 25 | recall_at_5=0.5663, precision_at_5=0.2476 |
| constraints | embedding_only | all | 100 | recall_at_5=0.6356, precision_at_5=0.3600 |
| constraints | embedding_only | us | 50 | recall_at_5=0.7096, precision_at_5=0.3915 |
| constraints | embedding_only | es | 25 | recall_at_5=0.5782, precision_at_5=0.4091 |
| constraints | embedding_only | jp | 25 | recall_at_5=0.5300, precision_at_5=0.2381 |
| constraints | hybrid_only | all | 100 | recall_at_5=0.6717, precision_at_5=0.3689 |
| constraints | hybrid_only | us | 50 | recall_at_5=0.7153, precision_at_5=0.3830 |
| constraints | hybrid_only | es | 25 | recall_at_5=0.5697, precision_at_5=0.4000 |
| constraints | hybrid_only | jp | 25 | recall_at_5=0.6808, precision_at_5=0.3048 |

embedding_rerank：未执行，原因 reranker_not_configured。

hybrid_rerank：未执行，原因 reranker_not_configured。
