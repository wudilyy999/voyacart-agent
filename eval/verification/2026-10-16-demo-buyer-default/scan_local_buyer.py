"""只读统计 data/ 下各 SQLite 买家表中旧、新固定买家的归属行数（只输出计数，不输出内容）。"""
import sqlite3,sys
from pathlib import Path
from scripts.migrate_local_buyer import FILES

data=Path(sys.argv[1]) if len(sys.argv)>1 else Path('data')
for name in FILES:
    path=data/name
    if not path.exists():
        print(f'{name}: 不存在');continue
    db=sqlite3.connect(f'file:{path}?mode=ro',uri=True)
    for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        cols=[r[1] for r in db.execute(f'PRAGMA table_info("{table}")')]
        owner='buyer_id' if 'buyer_id' in cols else 'buyer' if table in ('context_evidence','shopping_forms') else 'owner_id' if table=='session_write_claims' else None
        text_hits=sum(db.execute(f'SELECT count(*) FROM "{table}" WHERE CAST("{c}" AS TEXT) LIKE ?',('%pao-coder%',)).fetchone()[0] for c in cols)
        if owner is None and not text_hits:continue
        total=db.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]
        counts={b:db.execute(f'SELECT count(*) FROM "{table}" WHERE "{owner}"=?',(b,)).fetchone()[0] for b in ('pao-coder','demo-buyer')} if owner else {}
        print(f'{name}/{table}: 总行数={total} 归属列={owner} pao-coder={counts.get("pao-coder","-")} demo-buyer={counts.get("demo-buyer","-")} 任意列含pao-coder的行={text_hits}')
    db.close()
