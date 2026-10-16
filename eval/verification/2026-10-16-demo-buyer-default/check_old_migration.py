"""用改动前（264ef63）的迁移脚本运行新增用例，确认用例能发现两个库被漏迁。"""
import subprocess,tempfile,types
from pathlib import Path
import tests.test_fixed_buyer_persistence as t

old=types.ModuleType('old_migrate')
exec(subprocess.run(['git','show','264ef63:scripts/migrate_local_buyer.py'],check=True,capture_output=True,text=True).stdout,old.__dict__)
t.migrate=old.migrate
try:
    t.test_migrate_covers_model_preferences_and_shopping_forms(Path(tempfile.mkdtemp()))
    print('旧脚本通过新增用例（不符合预期）')
except AssertionError:
    print('旧脚本未通过新增用例：AssertionError（符合预期）')
