import requests
from bs4 import BeautifulSoup

def fetch_forum_updates():
    url = "https://myvirtual.free.nf/forum"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    updates = []
    for post in soup.select(".asgaros-post-title"):  # 根据实际 HTML 结构调整
        title = post.get_text(strip=True)
        link = post.find("a")["href"]
        updates.append(f"{title}\n{link}")
    return updates
