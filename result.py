# result.py
# Универсальный запуск всех этапов домашнего задания (создание структуры, обработка файлов, архивация, схема и итоговый отчёт)
# Все этапы комментированы для понимания порядка работы.

import os
import chardet  # Для автодетекта кодировки файлов
import zipfile   # Для архивации/распаковки
import json      # Для работы с JSON-файлами
from datetime import datetime
from typing import List
try:
    import jsonschema  # Для валидации JSON Schema
except ImportError:
    jsonschema = None

ROOT = os.path.dirname(os.path.abspath(__file__))

# 1. Создание структуры директорий и тестовых файлов
PATHS = ['data/raw','data/processed','logs','backups','output']
for rel in PATHS:
    full = os.path.join(ROOT, rel)
    os.makedirs(full, exist_ok=True)

log_entries = []
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for rel in PATHS:
    full = os.path.join(ROOT, rel)
    log_entries.append(f"{now} | DIR CREATED | {full}")

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
log_path = os.path.join(ROOT, 'logs', 'setup.log')
with open(log_path, 'a', encoding='utf-8') as f:
    for line in log_entries:
        f.write(line + '\n')
print('[1] Структура создана и файлы записаны.')

# 2. Чтение файлов, преобразование регистра, сериализация в JSON
RAW = os.path.join(ROOT, 'data', 'raw')
PROCESSED = os.path.join(ROOT, 'data', 'processed')
OUTPUT = os.path.join(ROOT, 'output')
def invert_case(text):
    """Инверсия регистра: a->A, A->a"""
    return ''.join([c.lower() if c.isupper() else c.upper() for c in text])
results = []
for fname in os.listdir(RAW):
    fpath = os.path.join(RAW, fname)
    with open(fpath, 'rb') as f:
        rawdata = f.read()
        enc = chardet.detect(rawdata)['encoding']
    with open(fpath, 'r', encoding=enc) as f:
        original = f.read()
    processed = invert_case(original)
    name, ext = os.path.splitext(fname)
    newname = name + '_processed' + ext
    newpath = os.path.join(PROCESSED, newname)
    with open(newpath, 'w', encoding='utf-8') as f:
        f.write(processed)
    results.append({
        'filename': fname,
        'original_text': original,
        'processed_text': processed,
        'size_bytes': os.path.getsize(newpath),
        'last_modified': datetime.fromtimestamp(os.path.getmtime(newpath)).isoformat()
    })
json_path = os.path.join(OUTPUT, 'processed_data.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('[2] Обработка, сериализация и сохранение завершены.')

# 3. Архивация и восстановление
DATA = os.path.join(ROOT, 'data')
BACKUPS = os.path.join(ROOT, 'backups')
nowstr = datetime.now().strftime('%Y%m%d')
backup_name = f"backup_{nowstr}.zip"
backup_path = os.path.join(BACKUPS, backup_name)
with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for folder, _, files in os.walk(DATA):
        for file in files:
            abs_path = os.path.join(folder, file)
            rel_path = os.path.relpath(abs_path, ROOT)
            zf.write(abs_path, rel_path)
print(f'[3] Бэкап создан: {backup_path}')
RESTORE_DIR = os.path.join(ROOT, 'restored_data')
os.makedirs(RESTORE_DIR, exist_ok=True)
with zipfile.ZipFile(backup_path, 'r') as zf:
    zf.extractall(RESTORE_DIR)
print(f'[3] Восстановление в папку: {RESTORE_DIR}')

# 4. Класс FileInfo, JSON Schema и валидация
class FileInfo:
    """Класс для хранения информации о файле (имя, путь, размер, даты)"""
    def __init__(self, name, full_path, size, created, modified):
        self.name = name
        self.full_path = full_path
        self.size = size
        self.created = created
        self.modified = modified
    def as_dict(self):
        return self.__dict__
PROCESSED = os.path.join(ROOT, 'data', 'processed')
all_info = []
for fname in os.listdir(PROCESSED):
    fpath = os.path.join(PROCESSED, fname)
    stat = os.stat(fpath)
    fi = FileInfo(
        name=fname,
        full_path=os.path.abspath(fpath),
        size=stat.st_size,
        created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
        modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )
    all_info.append(fi.as_dict())
json_fileinfo = os.path.join(OUTPUT, 'file_info.json')
with open(json_fileinfo, 'w', encoding='utf-8') as f:
    json.dump(all_info, f, ensure_ascii=False, indent=2)
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "full_path": {"type": "string"},
            "size": {"type": "integer"},
            "created": {"type": "string", "format": "date-time"},
            "modified": {"type": "string", "format": "date-time"}
        },
        "required": ["name", "full_path", "size", "created", "modified"]
    }
}
schema_path = os.path.join(OUTPUT, 'files_schema.json')
with open(schema_path, 'w', encoding='utf-8') as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)
if jsonschema is not None:
    with open(json_fileinfo, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_loaded = json.load(f)
    try:
        jsonschema.validate(data, schema_loaded)
        print('[4] Валидация прошла успешно!')
    except jsonschema.ValidationError as e:
        print(f'[4] Ошибка валидации: {e.message}')
else:
    print('[4] Модуль jsonschema не установлен, валидация пропущена.')

# 5. Итоговый отчёт (формат JSON)
REPORT_PATH = os.path.join(OUTPUT, 'final_report.json')
report = {
    "issues": [
        "Работа с разными кодировками требует использования chardet.",
        "Для JSON Schema нужно устанавливать пакет jsonschema.",
        "Архивирование и восстановление просто реализуются через модуль zipfile.",
    ],
    "time_spent": {
        "task1": "~10 мин",
        "task2": "~20 мин",
        "task3": "~10 мин",
        "task4": "~25 мин",
        "task5": "~10 мин"
    },
    "conclusions": [
        "Все задачи выполнены, проект универсален для любых текстовых файлов и кодировок.",
        "Возможно улучшение: авто-детект структуры файлов, логи в формате CSV, хранение отчётов в одном месте."
    ]
}
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"[5] Итоговый отчёт создан: {REPORT_PATH}")
