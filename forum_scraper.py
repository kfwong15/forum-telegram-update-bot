import os
import requests
from bs4 import BeautifulSoup
import hashlib
import json
from datetime import datetime

# 配置
FORUM_URL = "https://myvirtual.free.nf/forum"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CACHE_FILE = "sent_cache.json"

# 加载已发送缓存
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

# 保存已发送缓存
def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

# 生成唯一 ID（基于标题和链接）
def generate_id(title, link):
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

# 抓取论坛帖子
def fetch_forum_updates():
    try:
        response = requests.get(FORUM_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []

    for post in soup.select(".asgaros-post-title"):
        a_tag = post.find("a")
        if a_tag:
            title = a_tag.get_text(strip=True)
            link = a_tag["href"]
            full_link = link if link.startswith("http") else f"https://myvirtual.free.nf{link}"
            posts.append({"title": title, "link": full_link})
    return posts

# 发送到 Telegram
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print(f"[INFO] 已发送: {message[:30]}...")
    except Exception as e:
        print(f"[ERROR] Telegram 发送失败: {e}")

# 主流程
def main():
    print(f"[START] {datetime.now().isoformat()}")
    cache = load_cache()
    updates = fetch_forum_updates()

    new_posts = []
    for post in updates:
        uid = generate_id(post["title"], post["link"])
        if uid not in cache:
            new_posts.append(post)
            cache[uid] = True

    if not new_posts:
        print("[INFO] 没有新帖子")
    else:
        for post in new_posts:
            msg = f"*{post['title']}*\n[查看帖子]({post['link']})"
            send_to_telegram(msg)

    save_cache(cache)
    print(f"[END] 共发送 {len(new_posts)} 条更新")

if __name__ == "__main__":
    main()
