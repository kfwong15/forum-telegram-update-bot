import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FORUM_URL = os.getenv("FORUM_URL")

def fetch_forum():
    try:
        response = requests.get(FORUM_URL, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        send_telegram_message(f"❌ Failed to fetch forum content:\n{e}")
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status        try:
            print(f"🔄 Attempt {attempt} to fetch forum...")
            response = requests.get(FORUM_URL, headers=HEADERS, timeout=10)
            response.raise_for_status()
            print("✅ Forum fetched successfully.")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                send_telegram_message(f"❌ Bot failed to fetch forum:\n`{e}`")
                return None

if __name__ == "__main__":
    html = fetch_forum()
    if html:
        # You can add your parsing logic here
        send_telegram_message("✅ Forum content fetched successfully.")    response.raise_for_status()

if __name__ == "__main__":
    try:
        updates = fetch_forum_updates()
        if updates:
            message = "<b>📢 Forum Updates:</b>\n\n" + "\n\n".join(updates[:5])  # 最多发送5条
        else:
            message = "No new updates found."
        send_telegram_message(message)
    except Exception as e:
        error_message = f"❌ Bot failed: {str(e)}"
        print(error_message)
        send_telegram_message(error_message)
