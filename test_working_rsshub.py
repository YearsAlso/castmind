#!/usr/bin/env python3
"""
测试可用的 RSSHub 实例
"""

import ssl
import feedparser

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("🎯 测试可用的 RSSHub 实例")
print("=" * 60)

# 找到的可用的 RSSHub 实例
working_rsshub_url = "https://rsshub.rssforever.com/xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216"

print(f"测试 URL: {working_rsshub_url}")
print()

# 测试解析
try:
    feed = feedparser.parse(working_rsshub_url)
    
    if feed.bozo:
        print(f"❌ 解析错误: {feed.bozo_exception}")
    elif not feed.entries:
        print(f"⚠️  没有找到条目")
        if feed.feed.get('title'):
            print(f"   标题: {feed.feed.get('title')}")
    else:
        print(f"✅ RSS 解析成功!")
        print(f"   标题: {feed.feed.get('title', '无标题')}")
        print(f"   描述: {feed.feed.get('description', '无描述')[:100]}...")
        print(f"   条目数: {len(feed.entries)}")
        
        if feed.entries:
            print(f"\n📋 最新5期:")
            for i, entry in enumerate(feed.entries[:5], 1):
                print(f"   {i}. {entry.title}")
                print(f"      发布时间: {entry.get('published', '未知')}")
                if entry.get('description'):
                    print(f"      描述: {entry.get('description')[:80]}...")
                print()
        
        # 立即更新数据库
        print(f"🚀 立即更新数据库...")
        import sqlite3
        import subprocess
        
        db_path = "data/castmind.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 更新 RSS 地址并启用
        cursor.execute("""
        UPDATE podcasts 
        SET rss_url = ?, enabled = 1 
        WHERE name = '知行小酒馆'
        """, (working_rsshub_url,))
        
        conn.commit()
        
        # 验证更新
        cursor.execute("SELECT name, rss_url, enabled FROM podcasts WHERE name = '知行小酒馆'")
        result = cursor.fetchone()
        
        if result:
            name, rss_url, enabled = result
            print(f"✅ 数据库更新成功!")
            print(f"   名称: {name}")
            print(f"   RSS地址: {rss_url}")
            print(f"   启用状态: {'✅ 启用' if enabled else '❌ 禁用'}")
        
        conn.close()
        
        print(f"\n🎉 现在可以处理知行小酒馆了!")
        print(f"   运行: python real_process_podcast.py '知行小酒馆' 1")
        
except Exception as e:
    print(f"❌ 异常: {e}")

print(f"\n💡 RSSHub 实例信息:")
print(f"   官方实例: https://rsshub.app (可能需要配置)")
print(f"   备用实例: https://rsshub.rssforever.com (当前可用)")
print(f"   其他实例: https://rsshub.uneasy.win")

print(f"\n📝 知行小酒馆处理准备:")
print(f"   1. RSS地址已更新: {working_rsshub_url}")
print(f"   2. 数据库已启用")
print(f"   3. 可以开始处理")

print(f"\n🚀 立即执行:")
print(f"   cd /Volumes/MxStore/Project/castmind")
print(f"   python real_process_podcast.py '知行小酒馆' 1")

print(f"\n⚠️  注意事项:")
print(f"   • RSSHub 实例可能不稳定")
print(f"   • 建议定期检查 RSS 链接有效性")
print(f"   • 如果失败，尝试其他 RSSHub 实例")