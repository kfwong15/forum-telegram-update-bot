import os, re, pathlib, json
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "public"
DATA_DIR = REPO_ROOT / "data"
OUT_FILE = OUT_DIR / "asgaros.xml"
STATE_FILE = DATA_DIR / "asgaros_feed_state.json"

FORUM_URL = os.environ.get("FORUM_URL", "https://example.com/forum/").strip()
MAX_FORUMS = int(os.environ.get("MAX_FORUMS", "12"))
MAX_TOPICS_PER_FORUM = int(os.environ.get("MAX_TOPICS_PER_FORUM", "50"))
DUMP_HTML = os.environ.get("DUMP_HTML", "0") == "1"
PRINT_LINKS = os.environ.get("PRINT_LINKS", "0") == "1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AsgarosFeedBuilder/1.2; +github-actions)",
    "Accept-Language": "en-US,en;q=0.7,zh-CN;q=0.6"
}

def ensure_dirs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.text

def is_topic_href(href: str) -> bool:
    if not href:
        return False
    h = href.lower()
    if "view=topic" in h:
        return True
    if "/topic/" in h:
        return True
    # 兼容一些常见变体
    if "view=thread" in h or "/thread/" in h or "/threads/" in h:
        return True
    # 带 id/tid 参数且处于 forum 路径
    if ("?id=" in h or "?tid=" in h or "topic=" in h or "thread=" in h) and "/forum" in h:
        return True
    return False

def parse_topics(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    topics, seen = [], set()
    anchors = soup.find_all("a", href=True)
    if PRINT_LINKS:
        print(f"[debug] anchors on page: {len(anchors)}")
    for a in anchors:
        href = a["href"]
        text = a.get_text(strip=True) or ""
        if is_topic_href(href) and text:
            link = urljoin(base_url, href)
            guid = make_guid_from_href(href, link)
            if guid in seen:
                continue
            seen.add(guid)
            topics.append({"id": guid, "title": text, "link": link})
    return topics

def make_guid_from_href(href: str, abs_link: str) -> str:
    # 优先用 id / tid
    qs = parse_qs(urlparse(href).query)
    for key in ("id", "tid", "topic", "thread"):
        if key in qs and qs[key]:
            return f"topic-{qs[key][0]}"
    m = re.search(r"/topic/([^/?#]+)/?", href, flags=re.I)
    if m:
        return f"topic-slug:{m.group(1)}"
    return f"link:{abs_link}"

def parse_forum_links(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    links, seen = [], set()
    base_path = urlparse(base_url).path.rstrip("/")
    candidates = set([
        base_url,
        urljoin(base_url, "./?view=recent"),
        urljoin(base_url, "./?view=latest"),
        urljoin(base_url, "./recent/"),
        urljoin(base_url, "./latest/"),
    ])
    for a in soup.find_all("a", href=True):
        href = a["href"]
        abs_link = urljoin(base_url, href)
        p = urlparse(abs_link)
        # 版块页：view=forum&id 或 /forum/<slug>/ 但排除 /topic/
        is_forum_qs = ("view=forum" in href and "id=" in href)
        is_forum_path = ("/forum/" in p.path) and ("/topic/" not in p.path) and (p.path.rstrip("/") != base_path)
        if is_forum_qs or is_forum_path:
            candidates.add(abs_link)
    # 去重并限制
    for u in candidates:
        if u not in seen:
            seen.add(u)
            links.append(u)
    return links[:MAX_FORUMS]

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
        forums = parse_forum_links(index_html, FORUM_URL)
        print(f"[info] no topics on base; try {len(forums)} forum pages")
        all_items = {}
        for idx, forum_url in enumerate(forums, 1):
            try:
                html = fetch_html(forum_url)
                if DUMP_HTML:
                    (OUT_DIR / f"debug_forum_{idx}.html").write_text(html, encoding="utf-8")
                ts = parse_topics(html, forum_url)[:MAX_TOPICS_PER_FORUM]
                print(f"[info] {forum_url} -> topics: {len(ts)}")
                for it in ts:
                    all_items[it["id"]] = it
            except Exception as e:
                print(f"[warn] fail {forum_url}: {e}")
                continue
        items = list(all_items.values())

    OUT_FILE.write_text(build_rss(items), encoding="utf-8")
    STATE_FILE.write_text(json.dumps({"generated": True, "count": len(items)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(items)} items -> {OUT_FILE}")

if __name__ == "__main__":
    main()
