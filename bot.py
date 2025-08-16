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
    main()    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36"
        }
        response = requests.get(RSS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"RSS订阅获取失败: {e}")
        return None

def parse_rss_feed(feed_content):
    """解析RSS订阅内容"""
    if not feed_content:
        return []
    
    feed = feedparser.parse(feed_content)
    posts = []
    
    for entry in feed.entries:
        # 提取帖子ID (从链接中提取)
        post_id = entry.link.split("#")[-1] if "#" in entry.link else entry.link.split("/")[-1]
        
        # 提取标题和链接
        title = entry.title
        link = entry.link
        
        # 提取作者
        author = entry.author if "author" in entry else "未知作者"
        
        # 提取发布时间
        if "published_parsed" in entry:
            published_time = time.strftime("%Y-%m-%d %H:%M", entry.published_parsed)
        else:
            published_time = "未知时间"
        
        posts.append({
            "id": post_id,
            "title": title,
            "link": link,
            "author": author,
            "published": published_time
        })
    
    return posts

def send_telegram_message(message):
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # 使用HTML格式避免Markdown语法问题
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram消息发送成功")
        return True
    except requests.RequestException as e:
        print(f"❌ Telegram消息发送失败: {e}")
        return False

def main():
    """主函数"""
    # 获取已发送的帖子ID
    sent_post_ids = get_sent_post_ids()
    new_posts = []
    
    # 获取RSS内容
    rss_content = fetch_rss_feed()
    
    if rss_content:
        # 解析帖子
        posts = parse_rss_feed(rss_content)
        
        # 筛选新帖子
        for post in posts:
            if post["id"] not in sent_post_ids:
                new_posts.append(post)
                sent_post_ids.add(post["id"])
                save_post_id(post["id"])
    
    # 发送通知
    if new_posts:
        message = "<b>📢 论坛新帖通知</b>\n\n"
        for i, post in enumerate(new_posts, 1):
            message += (
                f"<b>{i}. {post['title']}</b>\n"
                f"👤 作者: {post['author']}\n"
                f"⏰ 时间: {post['published']}\n"
                f"🔗 链接: <a href='{post['link']}'>{post['link']}</a>\n\n"
            )
        
        # 发送消息
        if send_telegram_message(message):
            print(f"✅ 成功发送 {len(new_posts)} 条新帖通知")
        else:
            print("❌ 消息发送失败")
    else:
        print("ℹ️ 没有发现新帖子")

if __name__ == "__main__":
    main()    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36"
        }
        response = requests.get(RSS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"RSS订阅获取失败: {e}")
        return None

def parse_rss_feed(feed_content):
    """解析RSS订阅内容"""
    if not feed_content:
        return []
    
    feed = feedparser.parse(feed_content)
    posts = []
    
    for entry in feed.entries:
        # 提取帖子ID (从链接中提取)
        post_id = entry.link.split("#")[-1] if "#" in entry.link else entry.link.split("/")[-1]
        
        # 提取标题和链接
        title = entry.title
        link = entry.link
        
        # 提取作者
        author = entry.author if "author" in entry else "未知作者"
        
        # 提取发布时间
        if "published_parsed" in entry:
            published_time = time.strftime("%Y-%m-%d %H:%M", entry.published_parsed)
        else:
            published_time = "未知时间"
        
        posts.append({
            "id": post_id,
            "title": title,
            "link": link,
            "author": author,
            "published": published_time
        })
    
    return posts

def send_telegram_message(message):
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # 使用HTML格式避免Markdown语法问题
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram消息发送成功")
        return True
    except requests.RequestException as e:
        print(f"❌ Telegram消息发送失败: {e}")
        return False

def main():
    """主函数"""
    # 获取已发送的帖子ID
    sent_post_ids = get_sent_post_ids()
    new_posts = []
    
    # 获取RSS内容
    rss_content = fetch_rss_feed()
    
    if rss_content:
        # 解析帖子
        posts = parse_rss_feed(rss_content)
        
        # 筛选新帖子
        for post in posts:
            if post["id"] not in sent_post_ids:
                new_posts.append(post)
                sent_post_ids.add(post["id"])
                save_post_id(post["id"])
    
    # 发送通知
    if new_posts:
        message = "<b>📢 论坛新帖通知</b>\n\n"
        for i, post in enumerate(new_posts, 1):
            message += (
                f"<b>{i}. {post['title']}</b>\n"
                f"👤 作者: {post['author']}\n"
                f"⏰ 时间: {post['published']}\n"
                f"🔗 链接: {post['link']}\n\n"
            )
        
        # 发送消息
        if send_telegram_message(message):
            print(f"✅ 成功发送 {len(new_posts)} 条新帖通知")
        else:
            print("❌ 消息发送失败")
    else:
        print("ℹ️ 没有发现新帖子")

if __name__ == "__main__":
    main()            
        title = entry.title
        link = entry.link
        posts.append(f"• [{title}]({link})")
    
    return posts[:5]  # 最多返回5个帖子

def send_telegram_message(message):
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram消息发送失败: {e}")

def main():
    """主函数"""
    rss_content = fetch_rss_feed()
    
    if not rss_content:
        print("⚠️ 无法获取RSS订阅内容")
        return
    
    posts = parse_rss_feed(rss_content)
    
    if not posts:
        print("ℹ️ 没有新帖子")
        return
    
    message = "📢 最新论坛帖子：\n" + "\n".join(posts)
    send_telegram_message(message)

if __name__ == "__main__":
    main()            posts.append(f"• [{title}]({link})")
    
    return posts[:5]  # 只返回前5个帖子

def send_telegram_message(message):
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram消息发送失败: {e}")

def main():
    """主函数"""
    html = fetch_forum_html()
    
    if not html:
        print("⚠️ 无法获取论坛内容")
        return
    
    posts = parse_forum_posts(html)
    
    if not posts:
        send_telegram_message("⚠️ 没有找到任何帖子")
        return
    
    message = "📢 最新论坛帖子：\n" + "\n".join(posts)
    send_telegram_message(message)

if __name__ == "__main__":
    main()    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()  # 确保这行是文件的最后一行有效代码        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            send_telegram_message("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ 消息已发送到 Telegram")
    except requests.RequestException as e:
        print(f"❌ 发送 Telegram 消息失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            print("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息发送成功")
    except requests.RequestException as e:
        print(f"❌ Telegram 消息发送失败: {e}")

def main():
    html = fetch_forum_html()
    if html:
        posts = parse_forum_posts(html)
        if posts:
            message = "📢 最新论坛帖子：\n" + "\n".join(posts)
            send_telegram_message(message)
        else:
            print("⚠️ 没有找到任何帖子")
    else:
        print("⚠️ 无法获取论坛内容")

if __name__ == "__main__":
    main()
def send_telegram_message(message):
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram 消息已发送。")
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
