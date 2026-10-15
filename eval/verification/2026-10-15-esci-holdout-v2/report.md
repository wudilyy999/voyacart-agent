# ESCI 留出档评测

状态：COMPLETED。

| 组别 | 策略 | 站点 | 查询数 | 指标 |
|---|---|---|---|---|
| ranking | embedding_only | all | 300 | ndcg=0.8528, ndcg_at_10=0.7334 |
| ranking | embedding_only | us | 150 | ndcg=0.8505, ndcg_at_10=0.7466 |
| ranking | embedding_only | es | 75 | ndcg=0.8394, ndcg_at_10=0.7010 |
| ranking | embedding_only | jp | 75 | ndcg=0.8708, ndcg_at_10=0.7394 |
| retrieval | embedding_only | all | 300 | recall_at_10=0.5018, recall_at_50=0.7995, ndcg_at_10=0.6131, judged_at_10=0.7927 |
| retrieval | embedding_only | us | 150 | recall_at_10=0.5642, recall_at_50=0.8332, ndcg_at_10=0.6319, judged_at_10=0.8093 |
| retrieval | embedding_only | es | 75 | recall_at_10=0.4458, recall_at_50=0.7651, ndcg_at_10=0.5867, judged_at_10=0.7867 |
| retrieval | embedding_only | jp | 75 | recall_at_10=0.4328, recall_at_50=0.7667, ndcg_at_10=0.6020, judged_at_10=0.7653 |
| constraints | embedding_only | all | 300 | recall_at_5=0.5912, precision_at_5=0.3081 |
| constraints | embedding_only | us | 150 | recall_at_5=0.6060, precision_at_5=0.2851 |
| constraints | embedding_only | es | 75 | recall_at_5=0.5416, precision_at_5=0.3175 |
| constraints | embedding_only | jp | 75 | recall_at_5=0.6068, precision_at_5=0.3485 |
| crosslingual | embedding_only | all | 200 | recall_at_10=0.4240, recall_at_50=0.7054, ndcg_at_10=0.5075, judged_at_10=0.6565 |
| crosslingual | embedding_only | us | 100 | recall_at_10=0.5031, recall_at_50=0.7731, ndcg_at_10=0.5621, judged_at_10=0.7280 |
| crosslingual | embedding_only | es | 50 | recall_at_10=0.3597, recall_at_50=0.6636, ndcg_at_10=0.4834, judged_at_10=0.6360 |
| crosslingual | embedding_only | jp | 50 | recall_at_10=0.3302, recall_at_50=0.6116, ndcg_at_10=0.4222, judged_at_10=0.5340 |
| crosslingual_fallback | local_embedding | all | 200 | recall_at_10=0.1560, recall_at_50=0.3685, ndcg_at_10=0.2067, judged_at_10=0.2910 |
| crosslingual_fallback | local_embedding | us | 100 | recall_at_10=0.1496, recall_at_50=0.3881, ndcg_at_10=0.1868, judged_at_10=0.2770 |
| crosslingual_fallback | local_embedding | es | 50 | recall_at_10=0.1561, recall_at_50=0.4004, ndcg_at_10=0.1998, judged_at_10=0.3060 |
| crosslingual_fallback | local_embedding | jp | 50 | recall_at_10=0.1687, recall_at_50=0.2972, ndcg_at_10=0.2531, judged_at_10=0.3040 |
| crosslingual_fallback | keyword_2gram | all | 200 | recall_at_10=0.1138, recall_at_50=0.1734, ndcg_at_10=0.1281, judged_at_10=0.1718 |
| crosslingual_fallback | keyword_2gram | us | 100 | recall_at_10=0.1042, recall_at_50=0.1470, ndcg_at_10=0.1041, judged_at_10=0.1310 |
| crosslingual_fallback | keyword_2gram | es | 50 | recall_at_10=0.1216, recall_at_50=0.1621, ndcg_at_10=0.1304, judged_at_10=0.1870 |
| crosslingual_fallback | keyword_2gram | jp | 50 | recall_at_10=0.1254, recall_at_50=0.2376, ndcg_at_10=0.1737, judged_at_10=0.2383 |
