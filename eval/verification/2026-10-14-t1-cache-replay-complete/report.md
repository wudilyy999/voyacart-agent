# T1 查询预分类

模型调用：0；缓存命中：2000。

| 站点 | 划分 | 类目 | 数量 |
|---|---|---|---|
| us | train | 旅行装备 | 1 |
| us | train | 户外运动 | 50 |
| us | train | 数码配件 | 33 |
| us | train | 家居生活 | 78 |
| us | train | 美妆个护 | 26 |
| us | train | 厨房餐饮 | 50 |
| us | train | 办公学习 | 31 |
| us | train | 母婴宠物 | 42 |
| us | train | 其他 | 187 |
| us | train | 分类失败 | 2 |
| us | test | 旅行装备 | 3 |
| us | test | 户外运动 | 45 |
| us | test | 数码配件 | 42 |
| us | test | 家居生活 | 67 |
| us | test | 美妆个护 | 41 |
| us | test | 厨房餐饮 | 27 |
| us | test | 办公学习 | 27 |
| us | test | 母婴宠物 | 50 |
| us | test | 其他 | 195 |
| us | test | 分类失败 | 3 |
| es | train | 旅行装备 | 2 |
| es | train | 户外运动 | 14 |
| es | train | 数码配件 | 38 |
| es | train | 家居生活 | 32 |
| es | train | 美妆个护 | 11 |
| es | train | 厨房餐饮 | 19 |
| es | train | 办公学习 | 25 |
| es | train | 母婴宠物 | 24 |
| es | train | 其他 | 85 |
| es | train | 分类失败 | 0 |
| es | test | 旅行装备 | 3 |
| es | test | 户外运动 | 27 |
| es | test | 数码配件 | 26 |
| es | test | 家居生活 | 33 |
| es | test | 美妆个护 | 21 |
| es | test | 厨房餐饮 | 18 |
| es | test | 办公学习 | 18 |
| es | test | 母婴宠物 | 21 |
| es | test | 其他 | 83 |
| es | test | 分类失败 | 0 |
| jp | train | 旅行装备 | 1 |
| jp | train | 户外运动 | 25 |
| jp | train | 数码配件 | 20 |
| jp | train | 家居生活 | 28 |
| jp | train | 美妆个护 | 17 |
| jp | train | 厨房餐饮 | 28 |
| jp | train | 办公学习 | 14 |
| jp | train | 母婴宠物 | 14 |
| jp | train | 其他 | 102 |
| jp | train | 分类失败 | 1 |
| jp | test | 旅行装备 | 1 |
| jp | test | 户外运动 | 20 |
| jp | test | 数码配件 | 29 |
| jp | test | 家居生活 | 23 |
| jp | test | 美妆个护 | 25 |
| jp | test | 厨房餐饮 | 23 |
| jp | test | 办公学习 | 15 |
| jp | test | 母婴宠物 | 16 |
| jp | test | 其他 | 98 |
| jp | test | 分类失败 | 0 |

train 目标包含开发查询 100 条与干扰查询 100 条，test 目标为留出查询 300 条。

| 站点 | 划分 | 目标 | 1.3 倍要求 | 可用 | 缺口 |
|---|---|---|---|---|---|
| us | train | 100 | 130 | 311 | 0 |
| us | test | 150 | 195 | 302 | 0 |
| es | train | 50 | 65 | 165 | 0 |
| es | test | 75 | 98 | 167 | 0 |
| jp | train | 50 | 65 | 147 | 0 |
| jp | test | 75 | 98 | 152 | 0 |
