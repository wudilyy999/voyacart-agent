# 2,000 件 Amazon 演示商品

从既有 ESCI 文本与已分类的 train 查询生成，零新增模型调用。商品保留原文标题、品牌、描述、要点和颜色；沿用既有目录处理规则移除 HTML、截取描述至 1,000 字符、每条要点至 200 字符并最多取 5 条。

目录：`data/catalog-esci-demo-2000.jsonl.gz`，全局去重 ASIN 2,000 个，US 1,000 / ES 500 / JP 500，编号 `P100000` 至 `P101999`。素材只使用已准备数据中 train / E 关联商品。商品暂定类目取成功分类查询的众数，同票按既有八类顺序；正式留出标注未用于选品。材质空列表表示未知。价格、库存、配送目的地沿用固定种子演示规则，来源站点作为原产国代理；目录 `data_provenance` 显式记录这些边界。

| 暂定类目 | 商品数 |
|---|---:|
| 旅行装备 | 24 |
| 户外运动 | 333 |
| 数码配件 | 216 |
| 家居生活 | 323 |
| 美妆个护 | 299 |
| 厨房餐饮 | 274 |
| 办公学习 | 228 |
| 母婴宠物 | 303 |

生成命令使用全新证据目录；默认目录文件已存在时会直接报错，重新生成可指定新的 `--catalog` 路径：

```bash
./.venv/bin/python -m scripts.esci.build_demo_catalog \
  --evidence eval/verification/2026-10-14-esci-demo-2000
```

实际验证：

```bash
PYTHONPATH=. ./.venv/bin/python eval/verification/2026-10-14-esci-demo-2000/verify_catalog.py
./.venv/bin/python -m pytest scripts/esci/test_build_demo_catalog.py scripts/esci/test_catalog_records.py -q
```

原文来源与 train / E 来源均 2,000 / 2,000 对应；领域目录加载 2,000 件；两个独立输出路径的 gzip 字节相同；价格有效、库存非负、币种符合站点，1,517 件有库存且可配送 CN。6 项脚本检查通过。原始输出见 [build.log](build.log)、[verify.log](verify.log)、[tests.log](tests.log)，商品依据见 [selection.json](selection.json)，汇总见 [summary.json](summary.json) 与 [verification-summary.json](verification-summary.json)。暂定类目与演示交易字段均未经过正式增强或人工抽检。

初次只读诊断使用 `read_text().splitlines()` 拆分 JSONL，遇到商品描述中的 Unicode 行分隔符 `U+2028`，导致 JSON 解码失败；原始错误见 [product-inspection-first.stderr](product-inspection-first.stderr)。生成器按文件迭代逐行读取，数据源保持原样。

示例：`P100472` 为 SAIREIDER 英文旅行枕，演示 USD 40.42、初始库存 114；`P101216` 为 Desigual 西语钱包，演示 EUR 30.49、初始库存 197；`P101612` 为 JP Design 日语行李箱，演示 JPY 7,638、初始库存 197。三者均可配送 CN。
