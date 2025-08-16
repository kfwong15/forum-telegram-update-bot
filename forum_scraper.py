import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# 论坛地址
FORUM_URL = "https://myvirtual.free.nf/forum"

# Telegram 配置
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 模拟浏览器请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0 Safari/537.36"
}

# 创建带重试机制的 Session
def create_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# 获取论坛内容
def fetch_forum_updates():
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
