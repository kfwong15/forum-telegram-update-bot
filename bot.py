import os
import requests
from bs4 import BeautifulSoup

FORUM_URL = os.getenv("FORUM_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def fetch_forum_updates():
    response = requests.get(FORUM_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.select('.post-title a')[:5]  # 根据论坛结构调整
    updates = [f"- {post.text.strip()}\n{post['href']}" for post in posts]
    return "\n\n".join(updates)

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    updates = fetch_forum_updates()
    if updates:
        send_to_telegram(f"📰 最新论坛更新：\n\n{updates}")
