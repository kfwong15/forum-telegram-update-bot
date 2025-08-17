import os, re, pathlib, json
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "public"
DATA_DIR = REPO_ROOT / "data"
OUT_FILE = OUT_DIR / "asgaros.xml"
STATE_FILE = DATA_DIR / "asgaros_feed_state.json"

FORUM_URL = os.environ.get("FORUM_URL", "https://example.com/forum/").strip()
MAX_FORUMS = int(os.environ.get("MAX_FORUMS", "6"))
MAX_TOPICS_PER_FORUM = int(os.environ.get("MAX_TOPICS_PER_FORUM", "30"))
DUMP_HTML = os.environ.get("DUMP_HTML", "0") == "1"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AsgarosFeedBuilder/1.1)"}

def ensure_dirs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.text

def parse_topics(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    topics = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True) or ""
        if not text:
            continue
        if ("view=topic" in href and "id=" in href) or "/topic/" in href:
            link = urljoin(base_url, href)
            guid = re.search(r"[?&]id=(\d+)", href)
            guid_val = f"topic-{guid.group(1)}" if guid else f"link:{link}"
            if guid_val in seen:
                continue
            seen.add(guid_val)
            topics.append({"id": guid_val, "title": text, "link": link})
    return topics

def parse_forum_links(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    links = []
    seen = set()
    base_path = urlparse(base_url).path.rstrip("/")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True) or ""
        if not text:
            continue
        abs_link = urljoin(base_url, href)
        p = urlparse(abs_link)
        # 版块页：包含 view=forum&id= 或者 /forum/<something>/（但排除 /forum/ 自身与 /topic/）
        is_forum_qs = ("view=forum" in href and "id=" in href)
        is_forum_path = ("/forum/" in p.path) and ("/topic/" not in p.path) and (p.path.rstrip("/") != base_path)
        if is_forum_qs or is_forum_path:
            if abs_link not in seen:
                seen.add(abs_link)
                links.append(abs_link)
    return links

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
    for it in items:
        rss.append('<item>')
        rss.append(f'<title>{esc_xml(it["title"])}</title>')
        rss.append(f'<link>{esc_xml(it["link"])}</link>')
        rss.append(f'<guid isPermaLink="false">{esc_xml(it["id"])}</guid>')
        rss.append(f'<pubDate>{now.strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate>')
        rss.append('</item>')
    rss.append('</channel>')
    rss.append('</rss>')
    return "\n".join(rss)

def main():
    ensure_dirs()
    index_html = fetch_html(FORUM_URL)
    if DUMP_HTML:
        (OUT_DIR / "debug_index.html").write_text(index_html, encoding="utf-8")

    items = parse_topics(index_html, FORUM_URL)

    if not items:
        forums = parse_forum_links(index_html, FORUM_URL)[:MAX_FORUMS]
        all_items = {}
        for idx, forum_url in enumerate(forums, 1):
            try:
                html = fetch_html(forum_url)
                if DUMP_HTML:
                    (OUT_DIR / f"debug_forum_{idx}.html").write_text(html, encoding="utf-8")
                ts = parse_topics(html, forum_url)[:MAX_TOPICS_PER_FORUM]
                for it in ts:
                    all_items[it["id"]] = it
            except Exception:
                continue
        items = list(all_items.values())

    OUT_FILE.write_text(build_rss(items), encoding="utf-8")
    STATE_FILE.write_text(json.dumps({"generated": True, "count": len(items)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(items)} items -> {OUT_FILE}")

if __name__ == "__main__":
    main()
