import os
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
PATHS = [
    'data/raw',
    'data/processed',
    'logs',
    'backups',
    'output',
]

# Создание директорий
for rel in PATHS:
    full = os.path.join(ROOT, rel)
    os.makedirs(full, exist_ok=True)

log_entries = []
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for rel in PATHS:
    full = os.path.join(ROOT, rel)
    log_entries.append(f"{now} | DIR CREATED | {full}")

# Создание файлов с разными кодировками
files = [
    ('example_utf8.txt', 'Привет мир! Hello World!'),
    ('example_iso.txt', '¡Hola mundo!'),
    ('пример_win1251.txt', 'Тест на кириллицу'),
]
encodings = ['utf-8', 'iso-8859-1', 'cp1251']

for (name, content), enc in zip(files, encodings):
    path = os.path.join(ROOT, 'data', 'raw', name)
    with open(path, 'w', encoding=enc) as f:
        f.write(content)
    log_entries.append(f"{now} | FILE CREATED | {path} | encoding={enc}")

# Запись лога
log_path = os.path.join(ROOT, 'logs', 'setup.log')
with open(log_path, 'a', encoding='utf-8') as f:
    for line in log_entries:
        f.write(line + '\n')
