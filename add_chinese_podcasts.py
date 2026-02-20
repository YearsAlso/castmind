#!/usr/bin/env python3
"""
添加优质中文播客到 CastMind
包含知行小酒馆和其他推荐的中文播客
"""

import ssl
import sqlite3
import feedparser
from pathlib import Path
import sys

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("📡 添加优质中文播客到 CastMind")
print("=" * 60)
print("包含知行小酒馆和其他推荐的中文播客")
print("=" * 60)

# 优质中文播客列表（需要验证的 RSS）
chinese_podcasts = [
    # 投资理财类
    {
        "name": "知行小酒馆",
        "rss_url": "https://www.xiaoyuzhoufm.com/rss/5f0e2b6b418a84a162abc4a9",  # 需要验证
        "category": "投资理财",
        "tags": "投资,理财,商业,金融",
        "description": "有知有行出品，投资理财知识分享"
    },
    {
        "name": "疯投圈",
        "rss_url": "https://fengtouquan.com/feed",  # 常见格式
        "category": "投资",
        "tags": "投资,VC,商业,科技",
        "description": "投资视角看商业，VC行业洞察"
    },
    
    # 商业分析类
    {
        "name": "商业就是这样",
        "rss_url": "https://shangyejiushizheyang.com/feed",  # 常见格式
        "category": "商业分析",
        "tags": "商业,案例,分析,经济",
        "description": "第一财经出品，真实商业案例解析"
    },
    
    # 科技互联网类
    {
        "name": "硅谷101",
        "rss_url": "https://guigu101.com/feed",  # 常见格式
        "category": "科技",
        "tags": "科技,硅谷,创新,创业",
        "description": "硅谷科技公司动态，技术创新商业应用"
    },
    {
        "name": "乱翻书",
        "rss_url": "https://luanfanshu.com/feed",  # 常见格式
        "category": "互联网",
        "tags": "互联网,产品,运营,分析",
        "description": "互联网行业分析，产品思维，运营策略"
    },
    
    # 文化生活类
    {
        "name": "故事FM",
        "rss_url": "https://storyfm.cn/feed",  # 常见格式
        "category": "文化",
        "tags": "故事,人文,生活,真实",
        "description": "亲历者自述的真实故事"
    },
    {
        "name": "日谈公园",
        "rss_url": "https://ritangongyuan.com/feed",  # 常见格式
        "category": "文化",
        "tags": "文化,生活,访谈,娱乐",
        "description": "文化访谈类播客，轻松有趣"
    },
    
    # 已验证的英文播客（备用）
    {
        "name": "BBC Global News (已验证)",
        "rss_url": "http://feeds.bbci.co.uk/news/rss.xml",
        "category": "新闻",
        "tags": "新闻,国际,英文,已验证",
        "description": "BBC全球新闻，英文内容，已验证可用"
    },
    {
        "name": "TED Talks Daily (已验证)",
        "rss_url": "https://feeds.feedburner.com/TedTalks_audio",
        "category": "演讲",
        "tags": "演讲,知识,英文,已验证",
        "description": "TED每日演讲，英文内容，已验证可用"
    },
]

print(f"准备测试 {len(chinese_podcasts)} 个中文播客")
print()

# 测试 RSS 链接
print("🔍 测试 RSS 链接有效性...")
valid_podcasts = []
need_verification = []

for podcast in chinese_podcasts:
    name = podcast["name"]
    rss_url = podcast["rss_url"]
    
    print(f"\n测试: {name}")
    print(f"URL: {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"  ❌ 解析错误")
            # 检查是否是常见格式问题
            if "text/html" in str(feed.bozo_exception):
                print(f"     可能是网页链接，不是 RSS 链接")
                need_verification.append(podcast)
            else:
                print(f"     错误: {feed.bozo_exception}")
        elif not feed.entries:
            print(f"  ⚠️  没有找到条目")
            need_verification.append(podcast)
        else:
            print(f"  ✅ 解析成功")
            print(f"     标题: {feed.feed.get('title', '无标题')}")
            print(f"     条目数: {len(feed.entries)}")
            valid_podcasts.append(podcast)
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        need_verification.append(podcast)

print(f"\n📊 测试结果:")
print(f"   有效的: {len(valid_podcasts)} 个")
print(f"   需要验证: {len(need_verification)} 个")

if valid_podcasts:
    print(f"\n✅ 可以直接添加的播客:")
    for podcast in valid_podcasts:
        print(f"   • {podcast['name']} ({podcast['category']})")

if need_verification:
    print(f"\n⚠️  需要手动验证的播客:")
    for podcast in need_verification:
        print(f"   • {podcast['name']}")
        print(f"     可能原因: RSS 链接需要更新")
        print(f"     建议: 访问播客官网查找正确的 RSS 链接")

# 连接数据库
print("\n🗄️  连接数据库...")
db_path = Path(__file__).parent / "data" / "castmind.db"

if not db_path.exists():
    print(f"❌ 数据库文件不存在: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 添加有效播客
print("\n📝 添加有效播客到数据库...")
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

# 显示当前所有订阅
print("\n📋 当前所有播客订阅:")
cursor.execute("""
SELECT name, category, tags, enabled 
FROM podcasts 
ORDER BY category, name
""")

all_podcasts = cursor.fetchall()

categories = {}
for name, category, tags, enabled in all_podcasts:
    if category not in categories:
        categories[category] = []
    status = "✅" if enabled else "❌"
    categories[category].append((name, tags, status))

total_count = 0
for category, items in categories.items():
    print(f"\n{category} ({len(items)}个):")
    for name, tags, status in items:
        print(f"  {status} {name}")
        if tags:
            print(f"     标签: {tags}")
    total_count += len(items)

print(f"\n📊 总计: {total_count} 个播客订阅")

conn.close()

print("\n" + "=" * 60)
if added_count > 0:
    print(f"✅ 添加完成！成功添加 {added_count} 个新播客")
else:
    print("ℹ️  没有添加新播客（可能已存在或需要验证）")
print("=" * 60)

print(f"\n💡 关于知行小酒馆:")
print(f"   知行小酒馆是一个优质的投资理财播客，但需要正确的 RSS 链接。")
print(f"   建议手动查找:")
print(f"   1. 访问小宇宙网站: https://www.xiaoyuzhoufm.com")
print(f"   2. 搜索'知行小酒馆'")
print(f"   3. 在播客页面找到 RSS 订阅链接")
print(f"   4. 使用找到的链接更新数据库")

print(f"\n🚀 立即可以执行的操作:")
print(f"   1. 处理已验证的英文播客:")
print(f"      python real_process_podcast.py \"BBC Global News (已验证)\" 1")
print(f"      python real_process_podcast.py \"TED Talks Daily (已验证)\" 1")
print(f"   2. 查找中文播客 RSS:")
print(f"      访问播客官网或播客平台")
print(f"      查找 RSS 订阅链接")
print(f"      使用 test_zhixing_podcast.py 测试")
print(f"   3. 更新数据库:")
print(f"      sqlite3 data/castmind.db")
print(f"      UPDATE podcasts SET rss_url='新链接' WHERE name='知行小酒馆';")

print(f"\n📝 中文播客查找技巧:")
print(f"   • 小宇宙平台: 播客页面通常有 RSS 链接")
print(f"   • 喜马拉雅: 专辑页面可能有 RSS")
print(f"   • 播客官网: 很多播客在官网提供 RSS")
print(f"   • 搜索引擎: 搜索'播客名称 RSS'")

print(f"\n🎯 推荐处理顺序:")
print(f"   1. 先用已验证的英文播客建立流程")
print(f"   2. 再查找和添加优质中文播客")
print(f"   3. 最后建立自动化处理系统")