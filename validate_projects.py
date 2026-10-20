import json
import sys
import re
from jsonschema import validate, ValidationError

def main():
    try:
        with open('projects.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open('projects.schema.json', 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e.filename} не найден.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка синтаксиса JSON в файле: {e}")
        sys.exit(1)

    # Валидация по схеме
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        print(f"❌ Ошибка валидации схемы: {e.message}")
        print(f"   Путь к ошибке: {e.json_path}")
        sys.exit(1)
        
    # Проверка на дубликаты (регистронезависимая)
    repos = [p['repo'].lower() for p in data]
    if len(repos) != len(set(repos)):
        print("❌ Ошибка: В projects.json найдены дубликаты репозиториев.")
        sys.exit(1)
        
    print("✅ projects.json валиден! Все проверки пройдены.")

if __name__ == "__main__":
    main()