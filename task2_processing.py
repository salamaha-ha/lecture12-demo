import os
import chardet
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, 'data', 'raw')
PROCESSED = os.path.join(ROOT, 'data', 'processed')
OUTPUT = os.path.join(ROOT, 'output')

# 1. Чтение и обработка файлов с определением кодировки
def invert_case(text):
    return ''.join([c.lower() if c.isupper() else c.upper() for c in text])

results = []
for fname in os.listdir(RAW):
    fpath = os.path.join(RAW, fname)
    # Определяем кодировку
    with open(fpath, 'rb') as f:
        rawdata = f.read()
        enc = chardet.detect(rawdata)['encoding']
    with open(fpath, 'r', encoding=enc) as f:
        original = f.read()
    processed = invert_case(original)
    # Сохраняем в processed
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

# 2. Сериализация в JSON
json_path = os.path.join(OUTPUT, 'processed_data.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
