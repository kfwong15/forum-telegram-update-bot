import os
import requests
import feedparser

# 环境变量配置
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RSS_URL = "https://myvirtual.free.nf/forum/feed"

def send_message(text):
    """发送纯文本消息到Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, json=data, timeout=10)
        return True
    except:
        return False

def main():
    """主函数"""
    try:
        # 获取RSS内容
        feed = feedparser.parse(RSS_URL)
        
        # 检查是否有帖子
        if not feed.entries:
            print("没有找到任何帖子")
            return
        
        # 创建消息文本
        message = "论坛最新帖子：\n\n"
        for i, post in enumerate(feed.entries[:5], 1):
            message += f"{i}. {post.title}\n链接: {post.link}\n\n"
        
        # 发送消息
        if send_message(message):
            print("消息发送成功")
        else:
            print("消息发送失败")
    except Exception as e:
        print(f"程序出错: {str(e)}")

if __name__ == "__main__":
    main()        print("✅ Telegram 消息已发送。")
    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram 消息发送失败：\n{e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        message = "📢 最新论坛帖子：\n" + "\n".join(posts)
        send_telegram_message(message)

if __name__ == "__main__":
    main()    if html:
        # ✅ 你可以在这里添加 BeautifulSoup 解析逻辑
        send_telegram_message("✅ Forum content fetched successfully.")

if __name__ == "__main__":
    main()                send_telegram_message(f"❌ Bot failed to fetch forum:\n`{e}`")
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
