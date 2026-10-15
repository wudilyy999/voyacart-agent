"""在 ESCI 全量商品 parquet 的全部文本列中做不区分大小写的子串计数。

子串不出现即任何整词切分都不会出现。需要 pyarrow（项目可选依赖 esci）：
uv run --no-project --with 'pyarrow>=23,<24' python -I scan_esci.py <parquet> <子串...>
"""
import sys

import pyarrow.compute as pc
import pyarrow.parquet as pq

path, *needles = sys.argv[1:]
source = pq.ParquetFile(path)
columns = [field.name for field in source.schema_arrow if str(field.type) in ("string", "large_string")]
counts = dict.fromkeys(needles, 0)
rows = 0
for index in range(source.num_row_groups):
    table = source.read_row_group(index, columns=columns)
    rows += table.num_rows
    for needle in needles:
        for column in columns:
            counts[needle] += pc.sum(pc.match_substring(table[column], needle, ignore_case=True)).as_py() or 0
print(f"rows={rows} columns={columns}")
for needle, count in counts.items():
    print(f"{needle!r} matched_cells={count}")
