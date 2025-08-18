import os
import json
import re
import time
import pathlib
from html import unescape
from xml.etree import ElementTree as ET

import feedparser
import requests

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS_DIR = REPO_ROOT / "posts"
DATA_DIR = REPO_ROOT / "data"
SEEN_FILE = DATA_DIR / "seen_ids.json"
DEBUG_FEED_FILE = DATA_DIR / "feed_debug.xml"

FEED_URL = os.environ.get("FEED_URL")                      # 可为 URL 或本地文件路径（如 public/asgaros.xml）
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SAVE_MODE = os.environ.get("SAVE_MODE", "files")           # files | none
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GitHubActionsBot/1.0)",
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}


def ensure_dirs():
    if SAVE_MODE != "none":
        POSTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_seen():
    if SEEN_FILE.exists():
        return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    return {"ids": []}


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text, flags=re.U).strip().lower()
    return re.sub(r"[\s_-]+", "-", text)


def to_markdown(entry):
    title = entry.get("title", "Untitled")
    link = entry.get("link", "")
    body = ""
    if entry.get("content"):
        body = entry["content"][0].get("value", "")
    else:
        body = unescape(entry.get("summary", "") or "")
    published = entry.get("published") or entry.get("updated") or ""
    safe_title = title.replace('"', "'")
    lines = [
        "---",
        f'title: "{safe_title}"',
        f"link: {link}",
        f"published: {published}",
        "---",
        "",
        body,
    ]
    return "\n".join(lines)


def send_telegram(text):
    if os.environ.get("DISABLE_TELEGRAM") == "1":
        return
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        requests.post(url, data=payload, timeout=20)
    except Exception:
        pass


def manual_parse_items(xml_text):
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []
    def tn(t):
        return t.split("}", 1)[1] if "}" in t else t
    items = []
    for item in root.iter():
        if tn(item.tag).lower() == "item":
            data = {"title": "", "link": "", "guid": "", "id": "", "published": "", "summary": ""}
            for child in list(item):
                name = tn(child.tag).lower()
                text = (child.text or "").strip()
                if name == "title":
                    data["title"] = text
                elif name == "link":
                    data["link"] = text
                elif name == "guid":
                    data["guid"] = text
                elif name in ("pubdate", "updated", "date"):
                    data["published"] = text
                elif name == "description" and not data.get("summary"):
                    data["summary"] = text
            data["id"] = data["guid"] or data["link"] or data["title"]
            if data["id"]:
                items.append(data)
    return items


def fetch_feed_text(url_or_path: str) -> str:
    # 本地文件优先
    if os.path.exists(url_or_path):
        return pathlib.Path(url_or_path).read_text(encoding="utf-8", errors="ignore")
    # 远程 URL
    r = requests.get(url_or_path, headers=HEADERS, timeout=30)
    r.raise_for_status()
    try:
        DEBUG_FEED_FILE.write_text(r.text, encoding=r.encoding or "utf-8")
    except Exception:
        pass
    return r.text


def main():
    assert FEED_URL, "FEED_URL missing"
    ensure_dirs()
    seen = load_seen()
    seen_ids = set(seen.get("ids", []))

    print(f"[rss] FEED_URL={FEED_URL}")
    xml_text = fetch_feed_text(FEED_URL)

    feed = feedparser.parse(xml_text)
    entries = list(getattr(feed, "entries", []) or [])
    print(f"[rss] feedparser entries={len(entries)} bozo={getattr(feed, 'bozo', None)} status={getattr(feed, 'status', None)}")

    if len(entries) == 0 and ("<item" in xml_text.lower()):
        manual_items = manual_parse_items(xml_text)
        print(f"[rss] manual parsed items={len(manual_items)}")
        # 适配结构
        entries = []
        for m in manual_items:
            entries.append({
                "title": m.get("title", ""),
                "link": m.get("link", ""),
                "guid": m.get("guid", ""),
                "id": m.get("id", ""),
                "published": m.get("published", ""),
                "summary": m.get("summary", ""),
            })

    new_ids, new_entries = [], []
    for e in entries:
        entry_id = e.get("id") or e.get("guid") or e.get("link") or (e.get("title", "") + str(e.get("published_parsed")))
        if entry_id in seen_ids:
            continue
        new_ids.append(entry_id)
        new_entries.append(e)

    if not new_entries and os.environ.get("DEBUG_TOUCH_ON_EMPTY") == "1":
        (DATA_DIR / "last_run.txt").write_text(str(time.time()), encoding="utf-8")

    for e in reversed(new_entries):
        title = e.get("title", "Untitled")
        link = unescape(e.get("link", ""))  # 避免 &amp; 之类实体
        if SAVE_MODE != "none":
            tstruct = e.get("published_parsed") or e.get("updated_parsed") or time.gmtime()
            yyyy, mm, dd = tstruct.tm_year, f"{tstruct.tm_mon:02d}", f"{tstruct.tm_mday:02d}"
            filename = f"{yyyy}-{mm}-{dd}-{slugify(title)[:64]}.md"
            (POSTS_DIR / filename).write_text(to_markdown(e), encoding="utf-8")
        send_telegram(f"🆕 <b>{title}</b>\n{link}")

    seen["ids"] = (list(seen_ids) + new_ids)[-5000:]
    save_seen(seen)


if __name__ == "__main__":
    main()
