import os
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(ROOT, 'output')
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

print(f"Итоговый отчёт создан: {REPORT_PATH}")
