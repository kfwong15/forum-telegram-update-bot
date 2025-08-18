import os
import json
import time
import pathlib
from html import unescape
from xml.etree import ElementTree as ET
import requests


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
SEEN_FILE = DATA_DIR / "seen_ids_fb.json"
DEBUG_FEED_FILE = DATA_DIR / "feed_debug_fb.xml"


FEED_URL = os.environ.get("FEED_URL")  # URL 或本地路径，如 /workspace/public/asgaros.xml
FB_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN") or os.environ.get("FACEBOOK_ACCESS_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FBShareBot/1.0)",
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_seen() -> dict:
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"ids": []}
    return {"ids": []}


def save_seen(seen: dict) -> None:
    SEEN_FILE.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")


def manual_parse_items(xml_text: str):
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []

    def tn(t: str) -> str:
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
    if os.path.exists(url_or_path):
        return pathlib.Path(url_or_path).read_text(encoding="utf-8", errors="ignore")
    r = requests.get(url_or_path, headers=HEADERS, timeout=30)
    r.raise_for_status()
    try:
        DEBUG_FEED_FILE.write_text(r.text, encoding=r.encoding or "utf-8")
    except Exception:
        pass
    return r.text


def send_facebook_page_post(message: str, link: str = "") -> None:
    if os.environ.get("DISABLE_FACEBOOK") == "1":
        return
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        return
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {"message": message}
    if link:
        payload["link"] = link
    try:
        requests.post(url, params={"access_token": FB_ACCESS_TOKEN}, data=payload, timeout=30)
    except Exception:
        pass


def main() -> None:
    assert FEED_URL, "FEED_URL missing"
    ensure_dirs()
    seen = load_seen()
    seen_ids = set(seen.get("ids", []))

    print(f"[fb] FEED_URL={FEED_URL}")
    xml_text = fetch_feed_text(FEED_URL)

    # 使用手动解析，避免 feedparser 在 Python 3.13 上的兼容性问题
    manual_items = manual_parse_items(xml_text)
    print(f"[fb] manual parsed items={len(manual_items)}")
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
        (DATA_DIR / "last_run_fb.txt").write_text(str(time.time()), encoding="utf-8")

    # oldest first
    for e in reversed(new_entries):
        title = e.get("title", "Untitled")
        link = unescape(e.get("link", ""))
        send_facebook_page_post(f"🆕 {title}\n{link}", link)

    seen["ids"] = (list(seen_ids) + new_ids)[-5000:]
    save_seen(seen)


if __name__ == "__main__":
    main()

