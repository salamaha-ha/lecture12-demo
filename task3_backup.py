import os
import zipfile
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data')
BACKUPS = os.path.join(ROOT, 'backups')

# 1. Создать резервную копию
now = datetime.now().strftime('%Y%m%d')
backup_name = f"backup_{now}.zip"
backup_path = os.path.join(BACKUPS, backup_name)

with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for folder, _, files in os.walk(DATA):
        for file in files:
            abs_path = os.path.join(folder, file)
            rel_path = os.path.relpath(abs_path, ROOT)
            zf.write(abs_path, rel_path)

print(f"Backup created: {backup_path}")

# 2. Восстановление из бэкапа (распаковка)
RESTORE_DIR = os.path.join(ROOT, 'restored_data')
if not os.path.exists(RESTORE_DIR):
    os.makedirs(RESTORE_DIR)
with zipfile.ZipFile(backup_path, 'r') as zf:
    zf.extractall(RESTORE_DIR)

print(f"Restored to: {RESTORE_DIR}")
