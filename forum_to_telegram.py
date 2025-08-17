import requests
from bs4 import BeautifulSoup

# 配置
FORUM_URL = "https://myvirtual.free.nf/forum"
LOGIN_URL = "https://myvirtual.free.nf/wp-login.php"
USERNAME = "kfwong9191"
PASSWORD = "kfwong9191"
TELEGRAM_TOKEN = "8473515668:AAEyz0zSKadGgUVv-YV_-pXCy-CWM9WvqjM"
TELEGRAM_CHAT_ID = "-1002826643319"

def login_to_forum():
    session = requests.Session()
    payload = {
        "log": USERNAME,
        "pwd": PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": FORUM_URL,
        "testcookie": "1"
    }
    session.post(LOGIN_URL, data=payload)
    return session

def get_latest_posts(session):
    res = session.get(FORUM_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    posts = []

    for item in soup.select(".thread-title a")[:5]:  # 抓最新5条
        title = item.text.strip()
        link = item["href"]
        if not link.startswith("http"):
            link = FORUM_URL + link
        posts.append((title, link))
    return posts

def send_to_telegram(title, link):
    msg = f"🆕 {title}\n🔗 {link}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    session = login_to_forum()
    posts = get_latest_posts(session)
    for title, link in posts:
        send_to_telegram(title, link)
