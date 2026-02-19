#!/usr/bin/env python3
"""
测试所有 RSS 链接的有效性
"""

import ssl
import feedparser
from pathlib import Path
import sqlite3

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("📡 测试所有 RSS 链接有效性")
print("=" * 60)

# 从数据库获取 RSS 链接
db_path = Path(__file__).parent / "data" / "castmind.db"
if not db_path.exists():
    print(f"❌ 数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name, rss_url FROM podcasts ORDER BY name")
podcasts = cursor.fetchall()
conn.close()

print(f"找到 {len(podcasts)} 个播客订阅")
print()

working_count = 0
problematic_count = 0

for name, rss_url in podcasts:
    print(f"测试: {name}")
    print(f"URL: {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"  ❌ 解析错误: {feed.bozo_exception}")
            problematic_count += 1
        elif not feed.entries:
            print(f"  ⚠️  没有找到条目")
            print(f"    状态: {feed.get('status', '未知')}")
            if feed.feed.get('title'):
                print(f"    标题: {feed.feed.get('title')}")
            problematic_count += 1
        else:
            print(f"  ✅ 解析成功")
            print(f"    标题: {feed.feed.get('title', '无标题')}")
            print(f"    条目数: {len(feed.entries)}")
            if feed.entries:
                print(f"    最新: {feed.entries[0].title[:60]}...")
            working_count += 1
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        problematic_count += 1
    
    print()

print("=" * 60)
print(f"📊 测试结果:")
print(f"   可用的: {working_count} 个")
print(f"   有问题的: {problematic_count} 个")
print(f"   总计: {len(podcasts)} 个")

if working_count == 0:
    print("\n⚠️  所有 RSS 链接都有问题")
    print("   可能原因:")
    print("   1. RSS 链接已失效")
    print("   2. 需要特殊处理（如认证）")
    print("   3. 网络连接问题")
    print("   4. RSS 格式不标准")
    
    print("\n💡 建议:")
    print("   1. 更新 RSS 链接")
    print("   2. 使用其他播客源测试")
    print("   3. 检查网络连接")

print("\n" + "=" * 60)
print("🚀 下一步:")
print("   1. 如果 RSS 有问题，需要更新链接")
print("   2. 可以使用测试用的 RSS 先验证流程")
print("   3. 或者使用本地测试文件")