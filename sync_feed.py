import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser
from dotenv import load_dotenv
from git import Repo

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:8b"
STATE_FILE = "state.json"

def load_projects():
    try:
        with open("projects.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def fetch_github_events(repo):
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
    if not events:
        return "Нет активности."
        
    time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
    lines = []
    
    for event in events:
        try:
            created_at = parser.isoparse(event.get("created_at"))
        except Exception:
            continue
        if created_at < time_threshold:
            continue

        etype = event.get("type", "")
        actor = event.get("actor", {}).get("login", "неизвестный автор")
        payload = event.get("payload", {})
        
        if etype == "PushEvent":
            for commit in payload.get("commits", []):
                msg = commit.get("message", "").strip()
                if msg:
                    lines.append(f"  - Коммит от {actor}: {msg}")
                
        elif etype == "PullRequestEvent":
            action = payload.get("action", "")
            pr = payload.get("pull_request", {})
            title = pr.get("title")
            if action in ["closed", "opened"] and title:
                lines.append(f"  - PR #{pr.get('number', '?')} ({action}) от {actor}: {title}")
                if pr.get("body"):
                    lines.append(f"    Описание: {pr['body'][:150]}...")
                    
        elif etype == "IssuesEvent":
            action = payload.get("action", "")
            issue = payload.get("issue", {})
            title = issue.get("title")
            if action in ["opened", "closed"] and title:
                lines.append(f"  - Issue #{issue.get('number', '?')} ({action}) от {actor}: {title}")
                
        elif etype == "ReleaseEvent":
            release = payload.get("release", {})
            tag = release.get("tag_name", "")
            if tag:
                lines.append(f"  - 🚀 РЕЛИЗ {tag} от {actor}: {release.get('name', tag)}")
                if release.get("body"):
                    lines.append(f"    Описание: {release['body'][:150]}...")

    if not lines:
        return "За последние 24 часа значимой активности не было."
    return "\n".join(lines)

def generate_summary_with_ollama(repo_name, log_text):
    prompt = f"""Ты — технический журналист. Сделай краткую новостную выжимку изменений в проекте за сутки.
Используй только факты из текста. Мелкие правки опечаток игнорируй.
Пиши на русском языке. Выдай ответ строго в формате Markdown. Не пиши вступлений (вроде "Вот сводка:"). Сразу начинай с заголовка.

Входные логи активности проекта "{repo_name}":
{log_text}

Требуемый формат ответа:
### 🚀 Главное за сегодня
*2-3 ключевых изменения*

### 🔧 Что еще сделано
*список других важных деталей, багов или issues*
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
    except Exception as e:
        print(f"❌ Ошибка Ollama: {e}")
    return None

def main():
    if not GITHUB_TOKEN:
        print("💡 Создайте файл .env и добавьте туда GITHUB_TOKEN=...")
        return

    print("📥 Синхронизация репозитория (git pull)...")
    try:
        repo = Repo(".")
        origin = repo.remotes.origin
        origin.pull()
    except Exception as e:
        print(f"⚠️ Ошибка при git pull: {e}")

    projects = load_projects()
    if not projects:
        return

    state = load_state()
    posts_created = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    state_changed = False

    for project in projects:
        repo_name = project["repo"]
        name = project["name"]
        category = project.get("category", "general")
        
        print(f"\n{'='*40}")
        print(f"📦 Проект: {name} ({repo_name})")
        
        raw_events = fetch_github_events(repo_name)
        if not raw_events:
            print("😴 Событий нет вообще.")
            continue

        latest_event_id = raw_events[0]["id"]
        last_processed_id = state.get(repo_name)
        
        if last_processed_id == latest_event_id:
            print("😴 Нет новых событий с прошлого запуска.")
            continue

        formatted_log = format_events(raw_events[:30]) 
        if "значимой активности не было" in formatted_log:
            print("😴 Нет свежих данных за 24 часа.")
            state[repo_name] = latest_event_id
            state_changed = True
            continue
            
        summary = generate_summary_with_ollama(name, formatted_log)
        
        if summary:
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
            
            state[repo_name] = latest_event_id
            state_changed = True

    if state_changed:
        save_state(state)
        posts_created.append(STATE_FILE)

    if posts_created:
        print(f"\n📤 Отправка изменений на GitHub...")
        try:
            repo.index.add(posts_created)
            repo.index.commit(f"🤖 Авто-сводка ИИ за {current_date}")
            origin.push()
            print("🎉 Изменения успешно запушены!")
        except Exception as e:
            print(f"❌ Ошибка при git push: {e}")
    else:
        print("\n✨ Новых постов нет, коммит не требуется.")
        
    # Принудительный выход без запуска очистки памяти (фикс WinError 6)
    os._exit(0)

if __name__ == "__main__":
    main()