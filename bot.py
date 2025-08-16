import os
import requests
import feedparser

# 从环境变量获取 Telegram 凭证
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RSS_URL = "https://myvirtual.free.nf/forum/feed"

def fetch_rss_feed():
    """获取 RSS 订阅内容"""
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"❌ 获取 RSS 失败: {str(e)}")
        return None

def parse_rss_feed(feed_content):
    """解析 RSS 内容"""
    if not feed_content:
        return []
    
    try:
        feed = feedparser.parse(feed_content)
        return feed.entries[:5]  # 返回前5个帖子
    except Exception as e:
        print(f"❌ 解析 RSS 失败: {str(e)}")
        return []

def send_telegram_message(message):
    """发送纯文本消息到 Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Telegram 发送失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 启动论坛监控机器人")
    
    # 获取 RSS 内容
    rss_content = fetch_rss_feed()
    
    if not rss_content:
        print("⚠️ 未获取到 RSS 内容")
        return
    
    # 解析帖子
    posts = parse_rss_feed(rss_content)
    
    if not posts:
        print("ℹ️ 没有找到新帖子")
        return
    
    # 构建消息
    message = "📢 论坛最新帖子:\n\n"
    for i, post in enumerate(posts, 1):
        message += f"{i}. {post.title}\n链接: {post.link}\n\n"
    
    # 发送消息
    if send_telegram_message(message):
        print(f"✅ 成功发送 {len(posts)} 条帖子")
    else:
        print("❌ 消息发送失败")

if __name__ == "__main__":
    main()        if send_message(message):
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
