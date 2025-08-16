import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FORUM_URL = "https://myvirtual.free.nf/forum"

def fetch_forum_html():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36"
        }
        response = requests.get(FORUM_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        send_telegram_message(f"❌ 无法抓取论坛内容：\n<pre>{e}</pre>")
        return None

def parse_forum_posts(html):
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for item in soup.select(".thread-title a"):
        title = item.get_text(strip=True)
        link = item.get("href")
        if title and link:
            if link.startswith("http"):
                full_link = link
            else:
                full_link = FORUM_URL.rstrip("/") + "/" + link.lstrip("/")
            posts.append(f"• [{title}]({full_link})")
    return posts[:5]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()  # 确保这行是文件的最后一行有效代码        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ 消息已发送到 Telegram")
    except requests.RequestException as e:
        print(f"❌ 发送 Telegram 消息失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            print("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            print("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()
def send_telegram_message(message):
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息已发送。")
    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram 消息发送失败：\n{e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        message = "📢 最新论坛帖子：\n" + "\n".join(posts)
        send_telegram_message(message)

if __name__ == "__main__":
    main()    if html:
        # ✅ 你可以在这里添加 BeautifulSoup 解析逻辑
        send_telegram_message("✅ Forum content fetched successfully.")

if __name__ == "__main__":
    main()                send_telegram_message(f"❌ Bot failed to fetch forum:\n`{e}`")
                return None

if __name__ == "__main__":
    html = fetch_forum()
    if html:
        # You can add your parsing logic here
        send_telegram_message("✅ Forum content fetched successfully.")    response.raise_for_status()

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
