import requests
from bs4 import BeautifulSoup
import logging
import os

# ✅ 环境变量（确保在 GitHub Secrets 中设置）
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ 日志设置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ 抓取论坛内容
def fetch_forum_updates():
    url = "https://myvirtual.free.nf/forum"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 🎯 示例：抓取最新帖子标题和链接
        updates = []
        for post in soup.select(".threadtitle a")[:5]:  # 取前5个帖子
            title = post.get_text(strip=True)
            link = post["href"]
            full_link = link if link.startswith("http") else f"{url}/{link}"
            updates.append(f"🆕 <b>{title}</b>\n{full_link}")
        return updates

    except requests.RequestException as e:
        logging.error(f"[FETCH] 抓取失败: {e}")
        return []

# ✅ 发送到 Telegram
def send_to_telegram(updates):
    if not updates:
        logging.info("[SEND] 没有新内容可发送")
        return

    for update in updates:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": update,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data=payload,
                timeout=10
            )
            response.raise_for_status()
            logging.info(f"[SEND] 已发送更新: {update[:50]}...")
        except requests.RequestException as e:
            logging.error(f"[SEND] 发送失败: {e}")

# ✅ 主函数
def main():
    updates = fetch_forum_updates()
    send_to_telegram(updates)

if __name__ == "__main__":
    main()        logging.info("[SEND] 没有新内容可发送")
        return

    for update in updatesdef fetch_forum_updates():
    session = create_session()
    try:
        response = session.get(FORUM_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        logging.info("成功获取论坛内容")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")
        return None

# 解析内容（你可以根据论坛结构自定义）
def parse_updates(html):
    # 示例：返回空列表表示没有新帖子
    return []

# 发送到 Telegram
def send_to_telegram(messages):
    if not messages:
        logging.info("没有新帖子")
        return

    for msg in messages:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data=payload,
                timeout=10
            )
            r.raise_for_status()
            logging.info("已发送更新到 Telegram")
        except requests.exceptions.RequestException as e:
            logging.error(f"发送失败: {e}")

# 主流程
def main():
    logging.info("[START]")
    html = fetch_forum_updates()
    if html:
        updates = parse_updates(html)
        send_to_telegram(updates)
        logging.info(f"[END] 共发送 {len(updates)} 条更新")
    else:
        logging.info("[END] 请求失败，未发送任何更新")

if __name__ == "__main__":
    main()        return []

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
