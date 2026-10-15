# ESCI 留出档评测

状态：COMPLETED。

| 组别 | 策略 | 站点 | 查询数 | 指标 |
|---|---|---|---|---|
| ranking | embedding_only | all | 300 | ndcg=0.8459, ndcg_at_10=0.7268 |
| ranking | embedding_only | us | 150 | ndcg=0.8414, ndcg_at_10=0.7400 |
| ranking | embedding_only | es | 75 | ndcg=0.8360, ndcg_at_10=0.7094 |
| ranking | embedding_only | jp | 75 | ndcg=0.8647, ndcg_at_10=0.7178 |
| retrieval | embedding_only | all | 300 | recall_at_10=0.5239, recall_at_50=0.8029, ndcg_at_10=0.6120, judged_at_10=0.7950 |
| retrieval | embedding_only | us | 150 | recall_at_10=0.5882, recall_at_50=0.8327, ndcg_at_10=0.6295, judged_at_10=0.8013 |
| retrieval | embedding_only | es | 75 | recall_at_10=0.4595, recall_at_50=0.7748, ndcg_at_10=0.5769, judged_at_10=0.7707 |
| retrieval | embedding_only | jp | 75 | recall_at_10=0.4595, recall_at_50=0.7715, ndcg_at_10=0.6122, judged_at_10=0.8067 |
| constraints | embedding_only | all | 300 | recall_at_5=0.6082, precision_at_5=0.3148 |
| constraints | embedding_only | us | 150 | recall_at_5=0.6061, precision_at_5=0.2780 |
| constraints | embedding_only | es | 75 | recall_at_5=0.5993, precision_at_5=0.3238 |
| constraints | embedding_only | jp | 75 | recall_at_5=0.6213, precision_at_5=0.3848 |
| crosslingual | embedding_only | all | 200 | recall_at_10=0.4104, recall_at_50=0.6988, ndcg_at_10=0.4967, judged_at_10=0.6420 |
| crosslingual | embedding_only | us | 100 | recall_at_10=0.4664, recall_at_50=0.7417, ndcg_at_10=0.5398, judged_at_10=0.7070 |
| crosslingual | embedding_only | es | 50 | recall_at_10=0.3915, recall_at_50=0.7032, ndcg_at_10=0.4795, judged_at_10=0.5980 |
| crosslingual | embedding_only | jp | 50 | recall_at_10=0.3172, recall_at_50=0.6088, ndcg_at_10=0.4276, judged_at_10=0.5560 |
| crosslingual_fallback | local_embedding | all | 200 | recall_at_10=0.1807, recall_at_50=0.3780, ndcg_at_10=0.2386, judged_at_10=0.3165 |
| crosslingual_fallback | local_embedding | us | 100 | recall_at_10=0.1797, recall_at_50=0.3879, ndcg_at_10=0.2075, judged_at_10=0.2960 |
| crosslingual_fallback | local_embedding | es | 50 | recall_at_10=0.1897, recall_at_50=0.4192, ndcg_at_10=0.2559, judged_at_10=0.3380 |
| crosslingual_fallback | local_embedding | jp | 50 | recall_at_10=0.1738, recall_at_50=0.3170, ndcg_at_10=0.2834, judged_at_10=0.3360 |
| crosslingual_fallback | keyword_2gram | all | 200 | recall_at_10=0.1013, recall_at_50=0.1522, ndcg_at_10=0.1100, judged_at_10=0.1521 |
| crosslingual_fallback | keyword_2gram | us | 100 | recall_at_10=0.0830, recall_at_50=0.1162, ndcg_at_10=0.0797, judged_at_10=0.1068 |
| crosslingual_fallback | keyword_2gram | es | 50 | recall_at_10=0.1191, recall_at_50=0.1486, ndcg_at_10=0.1194, judged_at_10=0.1630 |
| crosslingual_fallback | keyword_2gram | jp | 50 | recall_at_10=0.1201, recall_at_50=0.2279, ndcg_at_10=0.1613, judged_at_10=0.2320 |
