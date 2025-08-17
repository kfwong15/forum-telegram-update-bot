import os, re, pathlib, json
from urllib.parse import urljoin
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "public"
DATA_DIR = REPO_ROOT / "data"
OUT_FILE = OUT_DIR / "asgaros.xml"
STATE_FILE = DATA_DIR / "asgaros_feed_state.json"

FORUM_URL = os.environ.get("FORUM_URL", "https://myvirtual.free.nf/forum/").strip()

def ensure_dirs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AsgarosFeedBuilder/1.0)"}
    r = requests.get(url, headers=headers, timeout=25)
    r.raise_for_status()
    return r.text

def parse_topics(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    anchors = soup.find_all("a", href=True)
    topics_by_id = {}
    for a in anchors:
        href = a["href"]
        text = a.get_text(strip=True) or ""
        if not text:
            continue
        # 识别话题链接（尽量通用）：带 view=topic 或 /topic/ 风格
        if ("view=topic" in href and "id=" in href) or "/topic/" in href:
            m = re.search(r"[?&]id=(\d+)", href)
            if m:
                topic_id = m.group(1)
            else:
                # 用链接本身做 key，避免重复
                topic_id = "link:" + urljoin(base_url, href)
            if topic_id not in topics_by_id:
                topics_by_id[topic_id] = {
                    "id": topic_id,
                    "title": text,
                    "link": urljoin(base_url, href)
                }
    # 保持先出现在前；只取前 50 条
    return list(topics_by_id.values())[:50]

def esc_xml(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def build_rss(items):
    now = datetime.now(timezone.utc)
    rss = []
    rss.append('<?xml version="1.0" encoding="UTF-8"?>')
    rss.append('<rss version="2.0">')
    rss.append('<channel>')
    rss.append(f'<title>{esc_xml("Asgaros Forum Topics (Custom Feed)")}</title>')
    rss.append(f'<link>{esc_xml(FORUM_URL)}</link>')
    rss.append(f'<description>{esc_xml("Generated from forum HTML")}</description>')
    rss.append(f'<lastBuildDate>{now.strftime("%a, %d %b %Y %H:%M:%S %z")}</lastBuildDate>')
    for i, it in enumerate(items):
        pub = now
        rss.append('<item>')
        rss.append(f'<title>{esc_xml(it["title"])}</title>')
        rss.append(f'<link>{esc_xml(it["link"])}</link>')
        guid = it["id"] if it["id"].startswith("link:") else f"topic-{it['id']}"
        rss.append(f'<guid isPermaLink="false">{esc_xml(guid)}</guid>')
        rss.append(f'<pubDate>{pub.strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate>')
        rss.append('</item>')
    rss.append('</channel>')
    rss.append('</rss>')
    return "\n".join(rss)

def main():
    ensure_dirs()
    html = fetch_html(FORUM_URL)
    items = parse_topics(html, FORUM_URL)
    OUT_FILE.write_text(build_rss(items), encoding="utf-8")
    # 存个简单状态，便于将来扩展
    STATE_FILE.write_text(json.dumps({"generated": True, "count": len(items)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(items)} items -> {OUT_FILE}")

if __name__ == "__main__":
    main()
