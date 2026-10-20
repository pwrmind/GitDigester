# 🤖 GitDigester

[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Live-blue?style=flat-square)](https://pwrmind.github.io/GitDigester/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black?style=flat-square)](https://ollama.com)

**GitDigester** — это мета-проект, который собирает сырые логи активности (коммиты, Pull Requests, релизы) из open-source репозиториев на GitHub, пропускает их через локальную LLM (Ollama) и генерирует красивый новостной дайджест.

Вся работа происходит **локально на вашем компьютере**. Никаких платных API для нейросетей, никаких серверов. Результат публикуется как статический сайт на GitHub Pages.

🔗 **[Читать ленту](https://pwrmind.github.io/GitDigester/)**

## ⚙️ Как это работает

1. **Сбор данных:** Локальный Python-скрипт обращается к GitHub API и собирает события за последние 24 часа.
2. **Суммаризация:** Текст логов отправляется в локальную модель (`qwen3:8b` через Ollama), которая пишет краткую выжимку на русском языке.
3. **Публикация:** Скрипт создает Markdown-файл с Jekyll Front Matter, делает `git commit` и `git push`.
4. **Рендеринг:** GitHub Pages автоматически собирает сайт, а Alpine.js и Tailwind CSS выводят красивую ленту в браузере.
5. **Дедупликация:** Файл `state.json` хранит ID последних обработанных событий, чтобы скрипт не спамил одинаковыми постами при повторных запусках.

## 🚀 Как добавить свой проект в ленту

Вы можете добавить любой публичный репозиторий в нашу ленту! Это делается автоматически через Pull Request.

1. Форкните этот репозиторий (или создайте ветку).
2. Откройте файл `projects.json` и добавьте свой проект в конец массива:
   ```json
   {
     "name": "Название проекта",
     "repo": "username/repository",
     "category": "web-app",
     "description": "Краткое описание проекта"
   }
   ```
3. Отправьте Pull Request.
4. Наш GitHub Action (`auto-merge-projects.yml`) автоматически проверит JSON, убедится, что вы не удалили чужие проекты, и **сам смержит ваш PR**.

*Примечание: Проекты, добавленные вручную, не удаляются автоматически.*

## 🛠 Локальная установка и запуск

Если вы хотите развернуть такого же бота для своего списка проектов:

### 1. Требования
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (менеджер пакетов)
- [Ollama](https://ollama.com) с моделью `qwen3:8b` (или другой, способной писать на русском)

### 2. Настройка окружения
```bash
# Клонируйте репозиторий
git clone https://github.com/pwrmind/GitDigester.git
cd GitDigester

# Создайте виртуальное окружение и активируйте его
uv venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Установите зависимости
uv pip install requests python-dateutil python-dotenv GitPython jsonschema

# Скачайте модель для Ollama
ollama pull qwen3:8b
```

### 3. Добавьте токен GitHub
Создайте файл `.env` в корне проекта и добавьте туда ваш Personal Access Token (нужен для обхода лимитов API в 60 запросов/час):
```env
GITHUB_TOKEN=ghp_ваш_токен_здесь
```

### 4. Запустите генерацию
```bash
python sync_feed.py
```
Скрипт сделает `git pull`, соберет данные, сгенерирует посты и запушит их обратно в ваш репозиторий. Останется только настроить GitHub Pages в настройках репозитория (Source: `main` -> `/ (root)`).

## 📂 Структура проекта

- `sync_feed.py` — главный скрипт-оркестратор.
- `projects.json` — список отслеживаемых репозиториев.
- `projects.schema.json` — правила валидации для списка проектов.
- `state.json` — база данных последних обработанных событий.
- `_posts/` — сгенерированные Jekyll-посты.
- `_layouts/default.html` — HTML-шаблон сайта.
- `index.html` — логика фронтенда (Alpine.js).
- `posts.json` — JSON-индекс постов для быстрой клиентской фильтрации.

---
*Сгенерировано с любовью к Open Source и локальным LLM.*
