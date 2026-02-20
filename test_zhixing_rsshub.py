#!/usr/bin/env python3
"""
测试知行小酒馆的 RSSHub 地址
rsshub://xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216
"""

import ssl
import feedparser

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("🔍 测试知行小酒馆 RSSHub 地址")
print("=" * 60)

# 用户提供的地址
rsshub_url = "rsshub://xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216"

print(f"原始地址: {rsshub_url}")
print()

# RSSHub 地址需要转换为实际的 RSS 链接
# 格式: rsshub://xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216
# 转换为: https://rsshub.app/xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216

actual_rss_url = "https://rsshub.app/xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216"
print(f"转换后的 RSS 地址: {actual_rss_url}")
print()

# 测试这个 RSS 地址
print("📡 测试 RSS 解析...")
try:
    feed = feedparser.parse(actual_rss_url)
    
    if feed.bozo:
        print(f"❌ RSS 解析错误: {feed.bozo_exception}")
        
        # 尝试其他可能的格式
        print(f"\n💡 尝试其他可能的格式...")
        
        # 格式1: 直接的小宇宙 RSS
        test_url1 = "https://www.xiaoyuzhoufm.com/rss/6013f9f58e2f7ee375cf4216"
        print(f"测试格式1: {test_url1}")
        feed1 = feedparser.parse(test_url1)
        if feed1.bozo:
            print(f"   错误: {feed1.bozo_exception}")
        else:
            print(f"   成功! 标题: {feed1.feed.get('title', '无标题')}")
            print(f"   条目数: {len(feed1.entries)}")
            actual_rss_url = test_url1
        
        # 格式2: 另一种 RSSHub 格式
        test_url2 = "https://rsshub.app/xiaoyuzhoufm/podcast/6013f9f58e2f7ee375cf4216"
        print(f"\n测试格式2: {test_url2}")
        feed2 = feedparser.parse(test_url2)
        if feed2.bozo:
            print(f"   错误: {feed2.bozo_exception}")
        else:
            print(f"   成功! 标题: {feed2.feed.get('title', '无标题')}")
            print(f"   条目数: {len(feed2.entries)}")
            actual_rss_url = test_url2
            
    elif not feed.entries:
        print(f"⚠️  没有找到条目")
        print(f"   状态: {feed.get('status', '未知')}")
        if feed.feed.get('title'):
            print(f"   标题: {feed.feed.get('title')}")
    else:
        print(f"✅ RSS 解析成功!")
        print(f"   标题: {feed.feed.get('title', '无标题')}")
        print(f"   描述: {feed.feed.get('description', '无描述')[:100]}...")
        print(f"   条目数: {len(feed.entries)}")
        if feed.entries:
            print(f"   最新一期: {feed.entries[0].title}")
            print(f"   发布时间: {feed.entries[0].get('published', '未知')}")
        
except Exception as e:
    print(f"❌ 解析异常: {e}")

print(f"\n💡 RSSHub 说明:")
print(f"   RSSHub 是一个开源、易用、可扩展的 RSS 生成器")
print(f"   可以给任何奇奇怪怪的内容生成 RSS 订阅源")
print(f"   地址格式: rsshub://{rsshub_url.split('://')[1]}")

print(f"\n🚀 如果找到有效的 RSS 地址，可以:")
print(f"   1. 添加到数据库:")
print(f"      sqlite3 data/castmind.db \"INSERT INTO podcasts (name, rss_url, category, tags) VALUES ('知行小酒馆', '{actual_rss_url}', '投资理财', '投资,理财');\"")
print(f"   2. 测试处理:")
print(f"      python real_process_podcast.py '知行小酒馆' 1")

print(f"\n📝 知行小酒馆信息:")
print(f"   • 节目ID: 6013f9f58e2f7ee375cf4216")
print(f"   • 平台: 小宇宙")
print(f"   • 类型: 投资理财播客")
print(f"   • 主持人: 孟岩等")
print(f"   • 内容: 投资理念、理财知识、资产配置")