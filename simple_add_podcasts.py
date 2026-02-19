#!/usr/bin/env python3
"""
简单添加优质播客到 CastMind
使用已验证的 RSS 链接
"""

import ssl
import sqlite3
import feedparser
from pathlib import Path
import sys

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("📡 添加优质播客到 CastMind")
print("=" * 60)

# 已验证的 RSS 链接（从之前的测试中）
verified_podcasts = [
    # 英文播客（已验证可用）
    {
        "name": "BBC Global News",
        "rss_url": "http://feeds.bbci.co.uk/news/rss.xml",
        "category": "新闻",
        "tags": "新闻,国际,英文",
        "description": "BBC全球新闻，英文内容"
    },
    {
        "name": "TED Talks Daily",
        "rss_url": "https://feeds.feedburner.com/TedTalks_audio",
        "category": "演讲",
        "tags": "演讲,知识,英文",
        "description": "TED每日演讲，英文内容"
    },
    {
        "name": "The Bible in a Year",
        "rss_url": "https://feeds.fireside.fm/bibleinayear/rss",
        "category": "文化",
        "tags": "文化,宗教,英文",
        "description": "圣经一年通，英文内容"
    },
    
    # 中文播客（常见推荐）
    {
        "name": "故事FM",
        "rss_url": "https://feeds.fireside.fm/gushifm/rss",
        "category": "文化",
        "tags": "故事,人文,生活",
        "description": "亲历者自述的真实故事"
    },
    {
        "name": "日谈公园",
        "rss_url": "https://feeds.fireside.fm/ritangongyuan/rss",
        "category": "文化",
        "tags": "文化,生活,访谈",
        "description": "文化访谈类播客，轻松有趣"
    },
]

print(f"准备添加 {len(verified_podcasts)} 个播客")
print()

# 测试 RSS 链接
print("🔍 测试 RSS 链接...")
valid_podcasts = []

for podcast in verified_podcasts:
    name = podcast["name"]
    rss_url = podcast["rss_url"]
    
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
            valid_podcasts.append(podcast)
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")

print(f"\n📊 测试结果: {len(valid_podcasts)}/{len(verified_podcasts)} 个有效")

if not valid_podcasts:
    print("❌ 没有有效的 RSS 链接")
    sys.exit(1)

# 连接数据库
print("\n🗄️  连接数据库...")
db_path = Path(__file__).parent / "data" / "castmind.db"

if not db_path.exists():
    print(f"❌ 数据库文件不存在: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 添加播客
print("\n📝 添加播客到数据库...")
added_count = 0

for podcast in valid_podcasts:
    name = podcast["name"]
    rss_url = podcast["rss_url"]
    category = podcast["category"]
    tags = podcast["tags"]
    description = podcast["description"]
    
    # 检查是否已存在
    cursor.execute("SELECT id FROM podcasts WHERE name = ? OR rss_url = ?", 
                  (name, rss_url))
    existing = cursor.fetchone()
    
    if existing:
        print(f"⚠️  跳过已存在的播客: {name}")
        continue
    
    try:
        cursor.execute("""
        INSERT INTO podcasts (name, rss_url, enabled, tags, category, description)
        VALUES (?, ?, 1, ?, ?, ?)
        """, (name, rss_url, tags, category, description))
        
        print(f"✅ 添加: {name}")
        print(f"   分类: {category}")
        print(f"   标签: {tags}")
        added_count += 1
        
    except Exception as e:
        print(f"❌ 添加失败: {name} - {e}")

conn.commit()

# 显示当前订阅
print("\n📋 当前所有订阅:")
cursor.execute("SELECT name, category, tags FROM podcasts ORDER BY category, name")
all_podcasts = cursor.fetchall()

categories = {}
for name, category, tags in all_podcasts:
    if category not in categories:
        categories[category] = []
    categories[category].append((name, tags))

total_count = 0
for category, items in categories.items():
    print(f"\n{category} ({len(items)}个):")
    for name, tags in items:
        print(f"  • {name}")
        print(f"    标签: {tags}")
    total_count += len(items)

print(f"\n📊 总计: {total_count} 个播客订阅")

conn.close()

print("\n" + "=" * 60)
print(f"✅ 添加完成！成功添加 {added_count} 个新播客")
print("=" * 60)

print("\n🚀 下一步操作:")
print("1. 查看系统状态:")
print("   python castmind_ssl_patched.py status")
print()
print("2. 开始处理播客:")
print("   python castmind_ssl_patched.py process --name \"BBC Global News\" --limit 1")
print()
print("3. 批量处理所有播客:")
print("   python castmind_ssl_patched.py process-all --limit 1")
print()
print("4. 查看生成的文件:")
print("   ls -la data/transcripts/")
print("   ls -la data/summaries/")
print("   ls -la data/notes/")
print()
print("💡 提示:")
print("   • 从英文播客开始测试（RSS 更稳定）")
print("   • 分批处理避免 API 限制")
print("   • 监控日志了解处理进度")