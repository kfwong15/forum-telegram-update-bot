import os
import requests
from bs4 import BeautifulSoup

# ✅ 读取环境变量
FORUM_URL = os.getenv("FORUM_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ 校验环境变量是否存在
if not FORUM_URL or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Missing one or more required environment variables: FORUM_URL, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID")

def fetch_forum_updates():
    response = requests.get(FORUM_URL)
    response.raise_for_status()  # 如果请求失败则抛出异常
    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ 示例：提取论坛标题（根据你的论坛结构调整）
    updates = []
    for item in soup.select(".forum-thread-title"):  # 请根据实际 HTML 结构修改选择器
        title = item.get_text(strip=True)
        link = item.get("href")
        if link and not link.startswith("http"):
            link = FORUM_URL.rstrip("/") + "/" + link.lstrip("/")
        updates.append(f"{title}\n{link}")
    return updates

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()

if __name__ == "__main__":
    try:
        updates = fetch_forum_updates()
        if updates:
            message = "<b>📢 Forum Updates:</b>\n\n" + "\n\n".join(updates[:5])  # 最多发送5条
        else:
            message = "No new updates found."
        send_telegram_message(message)
    except Exception as e:
        error_message = f"❌ Bot failed: {str(e)}"
        print(error_message)
        send_telegram_message(error_message)
