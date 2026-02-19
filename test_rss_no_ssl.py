#!/usr/bin/env python3
"""
测试 RSS 链接（不验证 SSL）
"""

import feedparser
import ssl

# 创建不验证 SSL 的上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 测试多个 RSS 链接
test_rss_list = [
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),  # 使用 HTTP
    ("得到", "https://feeds.fireside.fm/dedao/rss"),
    ("商业就是这样", "https://feeds.fireside.fm/shangyejiushizheyang/rss"),
    ("简单测试", "http://example.com/rss"),  # 测试用
]

print("📡 测试 RSS 链接（不验证 SSL）")
print("=" * 60)

for name, rss_url in test_rss_list:
    print(f"\n测试: {name}")
    print(f"URL: {rss_url}")
    
    try:
        # 使用自定义的 SSL 上下文
        feed = feedparser.parse(rss_url, ssl_verify=False)
        
        if feed.bozo:
            print(f"  ❌ 解析错误: {feed.bozo_exception}")
        elif not feed.entries:
            print(f"  ⚠️  没有找到条目")
            print(f"    状态: {feed.get('status', '未知')}")
            print(f"    标题: {feed.feed.get('title', '无标题')}")
        else:
            print(f"  ✅ 解析成功")
            print(f"    标题: {feed.feed.get('title', '无标题')}")
            print(f"    条目数: {len(feed.entries)}")
            if feed.entries:
                print(f"    最新: {feed.entries[0].title[:50]}...")
    
    except Exception as e:
        print(f"  ❌ 异常: {e}")

print("\n" + "=" * 60)
print("💡 解决方案:")
print("1. 安装 SSL 证书: /Applications/Python\\ 3.12/Install\\ Certificates.command")
print("2. 或者使用 HTTP 链接（如果支持）")
print("3. 或者在代码中禁用 SSL 验证（不推荐生产环境）")