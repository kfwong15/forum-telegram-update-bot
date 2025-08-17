import os, json, re, time, pathlib
from html import unescape
import feedparser, requests

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS_DIR = REPO_ROOT / "posts"
DATA_DIR = REPO_ROOT / "data"
SEEN_FILE = DATA_DIR / "seen_ids.json"

FEED_URL = os.environ.get("FEED_URL")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ensure_dirs():
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
		body
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
		"disable_web_page_preview": False
	}
	try:
		requests.post(url, data=payload, timeout=20)
		except Exception:
		pass

def main():
	assert FEED_URL, "FEED_URL missing"
	ensure_dirs()
	seen = load_seen()
	seen_ids = set(seen.get("ids", []))

	print(f"[rss] FEED_URL={FEED_URL}")
	feed = feedparser.parse(FEED_URL, request_headers={"User-Agent": "Mozilla/5.0 (compatible; GitHubActionsBot/1.0)"})
	entries = getattr(feed, "entries", [])
	print(f"[rss] entries={len(entries)}")

	new_ids, new_entries = [], []
	for e in entries:
		entry_id = e.get("id") or e.get("guid") or e.get("link") or (e.get("title","") + str(e.get("published_parsed")))
		if entry_id in seen_ids:
			continue
		new_ids.append(entry_id)
		new_entries.append(e)

	if not new_entries and os.environ.get("DEBUG_TOUCH_ON_EMPTY") == "1":
		(DATA_DIR / "last_run.txt").write_text(str(time.time()), encoding="utf-8")

	# 老→新顺序推送
	for e in reversed(new_entries):
		title = e.get("title", "Untitled")
		link = e.get("link", "")
		tstruct = e.get("published_parsed") or e.get("updated_parsed") or time.gmtime()
		yyyy, mm, dd = tstruct.tm_year, f"{tstruct.tm_mon:02d}", f"{tstruct.tm_mday:02d}"
		filename = f"{yyyy}-{mm}-{dd}-{slugify(title)[:64]}.md"
		(POSTS_DIR / filename).write_text(to_markdown(e), encoding="utf-8")

		msg = f"🆕 <b>{title}</b>\n{link}"
		send_telegram(msg)

	seen["ids"] = (list(seen_ids) + new_ids)[-5000:]
	save_seen(seen)

if __name__ == "__main__":
	main()
