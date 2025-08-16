import requests
from bs4 import BeautifulSoup
import logging
import os

# === 日志设置 ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === 环境变量配置 ===
FORUM_URL = os.getenv("FORUM_URL", "https://myvirtual.free.nf/forum")
LOGIN_URL = FORUM_URL + "/index.php?action=login"
USERNAME = os.getenv("FORUM_USERNAME")
PASSWORD = os.getenv("FORUM_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === 登录函数 ===
def login():
    session = requests.Session()
    payload = {
        "user": USERNAME,
        "pass": PASSWORD,
        "submit": "Login"
    }

    try:
        response = session.post(LOGIN_URL, data=payload, timeout=10)
        response.raise_for_status()
        if "logout" in response.text.lower():
            logging.info("[LOGIN] 登录成功")
            return session
        else:
            logging.error("[LOGIN] 登录失败，未检测到登出标志")
            return None
    except Exception as e:
        logging.error(f"[LOGIN] 登录异常: {e}")
        return None

# === 抓取帖子函数 ===
def scrape_posts(session):
    try:
        response = session.get(FORUM_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        posts = []
        for topic in soup.select(".forum-topic-title a")[:5]:  # 根据实际结构调整
            title = topic.text.strip()
            link = topic["href"]
            full_link = link if link.startswith("http") else FORUM_URL + "/" + link
            posts.append(f"📝 {title}\n🔗 {full_link}")

        logging.info(f"[SCRAPE] 抓取到 {len(posts)} 条帖子")
        return posts
    except Exception as e:
        logging.error(f"[SCRAPE] 抓取失败: {e}")
        return []

# === 推送到 Telegram ===
def send_to_telegram(messages):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("[TELEGRAM] 缺少 Token 或 Chat ID")
        return

    for msg in messages:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "disable_web_page_preview": True
        }
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logging.info("[TELEGRAM] 推送成功")
        except Exception as e:
            logging.error(f"[TELEGRAM] 推送失败: {e}")

# === 主流程 ===
def main():
    logging.info("[START] 脚本启动")
    session = login()
    if session:
        posts = scrape_posts(session)
        if posts:
            send_to_telegram(posts)
        else:
            logging.warning("[SCRAPE] 没有新帖子")
    else:
        logging.error("[LOGIN] 无法建立会话")

if __name__ == "__main__":
    main()
# 抓取帖子
def scrape_posts(session):
    try:
        response = session.get(FORUM_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.select(".asgaros-post .content")  # 根据你的论坛结构调整选择器
        extracted = [post.get_text(strip=True) for post in posts]
        logging.info(f"[SCRAPE] 抓取到 {len(extracted)} 条帖子")
        return extracted
    except Exception as e:
        logging.error(f"[SCRAPE] 抓取失败: {e}")
        return []

# 推送到 Telegram
def send_to_telegram(posts):
    for post in posts:
        try:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": post
            }
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logging.info("[TELEGRAM] 推送成功")
            else:
                logging.warning(f"[TELEGRAM] 推送失败: {response.text}")
        except Exception as e:
            logging.error(f"[TELEGRAM] 推送异常: {e}")

# 主流程
if __name__ == "__main__":
    session = login()
    if session:
        posts = scrape_posts(session)
        if posts:
            send_to_telegram(posts)
        else:
            print("No posts found or login failed.")
            logging.error("[SCRAPE] 抓取失败或无内容")
    else:
        print("Login failed.")
        logging.error("[LOGIN] 无法建立会话")        print(f"Login failed: {e}")
        return []

    # Step 4: Access forum main page after login
    try:
        forum_page = session.get(FORUM_URL, timeout=10)
        forum_page.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching forum after login: {e}")
        return []

    soup = BeautifulSoup(forum_page.text, "html.parser")
    posts = []

    for topic in soup.select(".forum-topic-title a")[:5]:
        title = topic.text.strip()
        link = topic["href"]
        full_link = link if link.startswith("http") else FORUM_URL + "/" + link
        posts.append(f"🛡️ {title}\n🔗 {full_link}")

    return posts

def send_to_telegram(messages):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram credentials.")
        return

    for msg in messages:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "disable_web_page_preview": True
        }
        try:
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"Error sending to Telegram: {e}")

if __name__ == "__main__":
    posts = login_and_fetch()
    if posts:
        send_to_telegram(posts)
    else:
        print("No posts found or login failed.")        logging.error(f"[SCRAPE] 抓取失败: {e}")
        return []

# === Cache Handling ===
def load_last_sent():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

def save_last_sent(updates):
    with open(CACHE_FILE, "w") as f:
        json.dump(updates, f)

# === Telegram Push ===
def send_to_telegram(updates):
    last_sent = load_last_sent()
    new_updates = [u for u in updates if u not in last_sent]

    if not new_updates:
        logging.info("[SEND] 没有新内容可发送")
        return

    for update in new_updates:
        message = f"🆕 {update['title']}\n🔗 {update['link']}"
        url = f"{TELEGRAM_API}/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": True
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            res.raise_for_status()
            logging.info(f"[SEND] 已发送: {update['title']}")
        except Exception as e:
            logging.error(f"[SEND] 发送失败: {e}")

    save_last_sent(updates)

# === Main Entry ===
def main():
    updates = fetch_forum_updates()
    send_to_telegram(updates)

if __name__ == "__main__":
    main()        logging.info("[SEND] 没有新内容可发送")
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
