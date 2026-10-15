# ESCI 开发档评测

状态：COMPLETED。

| 组别 | 策略 | 站点 | 查询数 | 指标 |
|---|---|---|---|---|
| ranking | keyword_2gram | all | 100 | ndcg=0.8042, ndcg_at_10=0.6454 |
| ranking | keyword_2gram | us | 50 | ndcg=0.7819, ndcg_at_10=0.6377 |
| ranking | keyword_2gram | es | 25 | ndcg=0.8248, ndcg_at_10=0.6542 |
| ranking | keyword_2gram | jp | 25 | ndcg=0.8281, ndcg_at_10=0.6521 |
| ranking | bm25 | all | 100 | ndcg=0.8154, ndcg_at_10=0.6589 |
| ranking | bm25 | us | 50 | ndcg=0.7957, ndcg_at_10=0.6491 |
| ranking | bm25 | es | 25 | ndcg=0.8393, ndcg_at_10=0.6795 |
| ranking | bm25 | jp | 25 | ndcg=0.8310, ndcg_at_10=0.6579 |
| ranking | embedding_only | all | 100 | ndcg=0.8644, ndcg_at_10=0.7458 |
| ranking | embedding_only | us | 50 | ndcg=0.8488, ndcg_at_10=0.7405 |
| ranking | embedding_only | es | 25 | ndcg=0.8733, ndcg_at_10=0.7448 |
| ranking | embedding_only | jp | 25 | ndcg=0.8865, ndcg_at_10=0.7576 |
| ranking | hybrid_only | all | 100 | ndcg=0.8435, ndcg_at_10=0.7104 |
| ranking | hybrid_only | us | 50 | ndcg=0.8223, ndcg_at_10=0.7006 |
| ranking | hybrid_only | es | 25 | ndcg=0.8577, ndcg_at_10=0.7362 |
| ranking | hybrid_only | jp | 25 | ndcg=0.8719, ndcg_at_10=0.7040 |
| retrieval | keyword_2gram | all | 100 | recall_at_10=0.3609, recall_at_50=0.5879, ndcg_at_10=0.4555, judged_at_10=0.6336 |
| retrieval | keyword_2gram | us | 50 | recall_at_10=0.4098, recall_at_50=0.6769, ndcg_at_10=0.4713, judged_at_10=0.6600 |
| retrieval | keyword_2gram | es | 25 | recall_at_10=0.3480, recall_at_50=0.5472, ndcg_at_10=0.4857, judged_at_10=0.6600 |
| retrieval | keyword_2gram | jp | 25 | recall_at_10=0.2759, recall_at_50=0.4505, ndcg_at_10=0.3939, judged_at_10=0.5543 |
| retrieval | bm25 | all | 100 | recall_at_10=0.4569, recall_at_50=0.7356, ndcg_at_10=0.5498, judged_at_10=0.7610 |
| retrieval | bm25 | us | 50 | recall_at_10=0.5133, recall_at_50=0.7914, ndcg_at_10=0.5596, judged_at_10=0.7920 |
| retrieval | bm25 | es | 25 | recall_at_10=0.3698, recall_at_50=0.6939, ndcg_at_10=0.5321, judged_at_10=0.7160 |
| retrieval | bm25 | jp | 25 | recall_at_10=0.4314, recall_at_50=0.6656, ndcg_at_10=0.5480, judged_at_10=0.7440 |
| retrieval | embedding_only | all | 100 | recall_at_10=0.5403, recall_at_50=0.8005, ndcg_at_10=0.6410, judged_at_10=0.8130 |
| retrieval | embedding_only | us | 50 | recall_at_10=0.6040, recall_at_50=0.8568, ndcg_at_10=0.6569, judged_at_10=0.8580 |
| retrieval | embedding_only | es | 25 | recall_at_10=0.4354, recall_at_50=0.7381, ndcg_at_10=0.6319, judged_at_10=0.7880 |
| retrieval | embedding_only | jp | 25 | recall_at_10=0.5179, recall_at_50=0.7503, ndcg_at_10=0.6182, judged_at_10=0.7480 |
| retrieval | hybrid_only | all | 100 | recall_at_10=0.5279, recall_at_50=0.8148, ndcg_at_10=0.6305, judged_at_10=0.8400 |
| retrieval | hybrid_only | us | 50 | recall_at_10=0.5757, recall_at_50=0.8581, ndcg_at_10=0.6261, judged_at_10=0.8640 |
| retrieval | hybrid_only | es | 25 | recall_at_10=0.4649, recall_at_50=0.7646, ndcg_at_10=0.6305, judged_at_10=0.8200 |
| retrieval | hybrid_only | jp | 25 | recall_at_10=0.4954, recall_at_50=0.7785, ndcg_at_10=0.6394, judged_at_10=0.8120 |
| constraints | keyword_2gram | all | 100 | recall_at_5=0.4259, precision_at_5=0.2654 |
| constraints | keyword_2gram | us | 50 | recall_at_5=0.4912, precision_at_5=0.2660 |
| constraints | keyword_2gram | es | 25 | recall_at_5=0.2544, precision_at_5=0.2864 |
| constraints | keyword_2gram | jp | 25 | recall_at_5=0.4598, precision_at_5=0.2421 |
| constraints | bm25 | all | 100 | recall_at_5=0.5381, precision_at_5=0.3089 |
| constraints | bm25 | us | 50 | recall_at_5=0.5856, precision_at_5=0.3149 |
| constraints | bm25 | es | 25 | recall_at_5=0.4097, precision_at_5=0.3545 |
| constraints | bm25 | jp | 25 | recall_at_5=0.5663, precision_at_5=0.2476 |
| constraints | embedding_only | all | 100 | recall_at_5=0.5763, precision_at_5=0.3348 |
| constraints | embedding_only | us | 50 | recall_at_5=0.6899, precision_at_5=0.3730 |
| constraints | embedding_only | es | 25 | recall_at_5=0.4120, precision_at_5=0.3455 |
| constraints | embedding_only | jp | 25 | recall_at_5=0.4943, precision_at_5=0.2381 |
| constraints | hybrid_only | all | 100 | recall_at_5=0.6281, precision_at_5=0.3422 |
| constraints | hybrid_only | us | 50 | recall_at_5=0.6770, precision_at_5=0.3489 |
| constraints | hybrid_only | es | 25 | recall_at_5=0.4581, precision_at_5=0.3545 |
| constraints | hybrid_only | jp | 25 | recall_at_5=0.6967, precision_at_5=0.3143 |

embedding_rerank：未执行，原因 reranker_not_configured。

hybrid_rerank：未执行，原因 reranker_not_configured。
