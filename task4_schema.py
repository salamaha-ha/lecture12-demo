import os
import json
from datetime import datetime
from typing import List
import jsonschema

ROOT = os.path.dirname(os.path.abspath(__file__))
PROCESSED = os.path.join(ROOT, 'data', 'processed')
OUTPUT = os.path.join(ROOT, 'output')
SCHEMA_PATH = os.path.join(ROOT, 'output', 'files_schema.json')

class FileInfo:
    def __init__(self, name, full_path, size, created, modified):
        self.name = name
        self.full_path = full_path
        self.size = size
        self.created = created
        self.modified = modified
    def as_dict(self):
        return self.__dict__

# Собираем FileInfo для каждого файла
def get_all_file_info() -> List[dict]:
    result = []
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
        result.append(fi.as_dict())
    return result

# Сохраняем JSON
all_info = get_all_file_info()
json_path = os.path.join(OUTPUT, 'file_info.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_info, f, ensure_ascii=False, indent=2)

# Создаём JSON Schema
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
with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

# Валидация
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    schema = json.load(f)

try:
    jsonschema.validate(data, schema)
    print('Валидация прошла успешно!')
except jsonschema.ValidationError as e:
    print(f'Ошибка валидации: {e.message}')
