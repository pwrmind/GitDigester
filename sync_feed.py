import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser
from dotenv import load_dotenv
from git import Repo

# Загружаем переменные окружения из .env
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:8b"

def load_projects():
    """Читает список проектов из projects.json"""
    try:
        with open("projects.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Файл projects.json не найден!")
        return []

def fetch_github_events(repo):
    """Запрашивает последние события репозитория"""
    url = f"https://api.github.com/repos/{repo}/events"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Ошибка API для {repo}: {response.status_code}")
        return []
        
    return response.json()

def format_events(events):
    """Превращает сырой JSON в читаемый текст, пропуская пустые заголовки"""
    if not events:
        return "Нет активности."
        
    time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
    lines = []
    
    for event in events:
        try:
            created_at_str = event.get("created_at")
            if not created_at_str:
                continue
            created_at = parser.isoparse(created_at_str)
        except Exception:
            continue
            
        if created_at < time_threshold:
            continue

        etype = event.get("type", "")
        actor = event.get("actor", {}).get("login", "неизвестный автор")
        payload = event.get("payload", {})
        
        if etype == "PushEvent":
            commits = payload.get("commits", [])
            for commit in commits:
                msg = commit.get("message", "").strip()
                if msg:
                    lines.append(f"  - Коммит от {actor}: {msg}")
                
        elif etype == "PullRequestEvent":
            action = payload.get("action", "")
            pr = payload.get("pull_request", {})
            title = pr.get("title")
            # Пропускаем, если нет заголовка или это не открытие/закрытие
            if action in ["closed", "opened"] and title:
                lines.append(f"  - PR #{pr.get('number', '?')} ({action}) от {actor}: {title}")
                body = pr.get("body")
                if body:
                    lines.append(f"    Описание: {body[:150]}...")
                    
        elif etype == "IssuesEvent":
            action = payload.get("action", "")
            issue = payload.get("issue", {})
            title = issue.get("title")
            if action in ["opened", "closed"] and title:
                lines.append(f"  - Issue #{issue.get('number', '?')} ({action}) от {actor}: {title}")
                
        elif etype == "ReleaseEvent":
            release = payload.get("release", {})
            tag = release.get("tag_name", "")
            name = release.get("name", tag)
            if tag:
                lines.append(f"  - 🚀 РЕЛИЗ {tag} от {actor}: {name}")
                body = release.get("body")
                if body:
                    lines.append(f"    Описание: {body[:150]}...")

    if not lines:
        return "За последние 24 часа значимой активности не было."
        
    return "\n".join(lines)

def generate_summary_with_ollama(repo_name, log_text):
    """Отправляет логи в Ollama и возвращает готовый Markdown-текст"""
    prompt = f"""Ты — технический журналист. Твоя задача — сделать краткую, интересную новостную выжимку изменений в open-source проекте за последние сутки.
Используй только предоставленные факты. Не придумывай новые функции, если их нет в тексте. Мелкие правки опечаток или апдейты зависимостей упоминай кратко или игнорируй.

Пиши на русском языке, живо и профессионально. Выдай ответ строго в формате Markdown. Не пиши никаких вступлений от себя (вроде "Вот сводка:"). Сразу начинай с заголовка.

Входные логи активности проекта "{repo_name}":
{log_text}

Требуемый формат ответа (строго Markdown):
### 🚀 Главное за сегодня
*сюда напиши 2-3 ключевых изменения понятным языком*

### 🔧 Что еще сделано
*сюда добавь списком другие важные технические детали, исправления багов или закрытые issues*
"""

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "think": False
    }
    
    print(f"🧠 Генерация саммари через Ollama ({MODEL_NAME})...")
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=120)
        if response.status_code == 200:
            result = response.json().get("response", "")
            return result.strip().removeprefix("```markdown").removesuffix("```").strip()
        else:
            print(f"❌ Ошибка Ollama: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Не удалось связаться с Ollama: {e}")
        return None

def main():
    if not GITHUB_TOKEN:
        print("💡 Создайте файл .env и добавьте туда GITHUB_TOKEN=...")
        return

    # 1. Синхронизация с GitHub (git pull) перед началом
    print("📥 Синхронизация репозитория (git pull)...")
    try:
        repo = Repo(".")
        origin = repo.remotes.origin
        origin.pull()
    except Exception as e:
        print(f"⚠️ Ошибка при git pull (возможно, нет подключения): {e}")

    projects = load_projects()
    if not projects:
        print("Список проектов пуст.")
        return

    posts_created = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    # 2. Сбор данных и генерация
    for project in projects:
        repo_name = project["repo"]
        name = project["name"]
        category = project.get("category", "general")
        
        print(f"\n{'='*40}")
        print(f"📦 Проект: {name} ({repo_name})")
        print(f"{'='*40}")
        
        raw_events = fetch_github_events(repo_name)
        formatted_log = format_events(raw_events[:30]) 
        
        if "значимой активности не было" in formatted_log:
            print("😴 Нет новых данных за 24 часа.")
            continue
            
        summary = generate_summary_with_ollama(name, formatted_log)
        
        if summary:
            # 3. Формируем Jekyll-пост
            safe_name = repo_name.lower().replace("/", "-")
            file_name = f"_posts/{current_date}-{safe_name}.md"
            
            front_matter = f"""---
layout: default
title: "Дайджест {name} за {current_date}"
date: {current_date}
categories: {category}
---

"""
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(front_matter + summary)
                
            print(f"✅ Создан файл: {file_name}")
            posts_created.append(file_name)

    # 4. Отправка изменений на GitHub (git commit + push)
    if posts_created:
        print(f"\n📤 Отправка {len(posts_created)} постов на GitHub...")
        try:
            repo.index.add(posts_created)
            repo.index.commit(f"🤖 Авто-сводка ИИ за {current_date}")
            origin.push()
            print("🎉 Изменения успешно запушены! GitHub Pages обновит сайт через минуту.")
        except Exception as e:
            print(f"❌ Ошибка при git push: {e}")
    else:
        print("\n✨ Новых постов нет, коммит не требуется.")

if __name__ == "__main__":
    main()