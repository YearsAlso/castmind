#!/usr/bin/env python3
"""
测试简单的 RSS 链接
"""

import feedparser

# 测试多个 RSS 链接
test_rss_list = [
    ("BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("TED Talks", "https://feeds.feedburner.com/TedTalks_audio"),
    ("得到", "https://feeds.fireside.fm/dedao/rss"),
    ("商业就是这样", "https://feeds.fireside.fm/shangyejiushizheyang/rss"),
    ("测试 RSS", "https://feeds.fireside.fm/the-daily/rss"),
]

print("📡 测试 RSS 链接")
print("=" * 60)

for name, rss_url in test_rss_list:
    print(f"\n测试: {name}")
    print(f"URL: {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"  ❌ 解析错误: {feed.bozo_exception}")
        elif not feed.entries:
            print(f"  ⚠️  没有找到条目")
        else:
            print(f"  ✅ 解析成功")
            print(f"    标题: {feed.feed.get('title', '无标题')}")
            print(f"    条目数: {len(feed.entries)}")
            if feed.entries:
                print(f"    最新: {feed.entries[0].title[:50]}...")
    
    except Exception as e:
        print(f"  ❌ 异常: {e}")

print("\n" + "=" * 60)
print("💡 建议:")
print("1. 如果所有 RSS 都失败，可能是网络问题")
print("2. 可以尝试使用代理或更换网络")
print("3. 或者使用本地的测试 RSS 文件")