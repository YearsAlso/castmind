#!/usr/bin/env python3
"""
全面查找知行小酒馆的有效 RSS 地址
"""

import ssl
import feedparser
import requests
from urllib.parse import urlparse

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("🎯 全面查找知行小酒馆的有效 RSS 地址")
print("=" * 60)

# 知行小酒馆的节目ID
podcast_id = "6013f9f58e2f7ee375cf4216"

# 所有可能的 RSS 格式
possible_formats = [
    # RSSHub 格式
    (f"https://rsshub.app/xiaoyuzhou/podcast/{podcast_id}", "RSSHub 标准格式"),
    (f"https://rsshub.app/xiaoyuzhoufm/podcast/{podcast_id}", "RSSHub 完整格式"),
    
    # 小宇宙官方格式
    (f"https://www.xiaoyuzhoufm.com/rss/{podcast_id}", "小宇宙 RSS 格式"),
    (f"https://rss.xiaoyuzhoufm.com/{podcast_id}", "小宇宙 RSS 子域名"),
    (f"https://feed.xiaoyuzhoufm.com/{podcast_id}", "小宇宙 Feed 格式"),
    
    # 通用播客格式
    (f"https://xiaoyuzhoufm.com/podcast/{podcast_id}/feed", "通用 Feed 格式"),
    (f"https://xiaoyuzhoufm.com/feed/{podcast_id}", "Feed 目录格式"),
    
    # XML 格式
    (f"https://www.xiaoyuzhoufm.com/podcast/{podcast_id}.xml", "XML 文件格式"),
    (f"https://www.xiaoyuzhoufm.com/feed/{podcast_id}.xml", "XML Feed 格式"),
    
    # JSON 格式（有些平台用 JSON）
    (f"https://www.xiaoyuzhoufm.com/api/podcast/{podcast_id}/feed", "API JSON 格式"),
    
    # 测试用已知有效的 RSS（对比）
    ("http://feeds.bbci.co.uk/news/rss.xml", "BBC News (对比用)"),
]

print(f"测试 {len(possible_formats)} 种可能的 RSS 格式")
print(f"节目ID: {podcast_id}")
print()

valid_urls = []
need_inspection = []

for i, (url, description) in enumerate(possible_formats, 1):
    print(f"{i}. {description}")
    print(f"   URL: {url}")
    
    try:
        # 先尝试直接解析
        feed = feedparser.parse(url)
        
        if feed.bozo:
            error_msg = str(feed.bozo_exception)
            print(f"   ❌ 解析错误: {error_msg[:80]}...")
            
            # 检查是否是 HTML 页面（可能需要提取 RSS 链接）
            if "text/html" in error_msg:
                print(f"   💡 可能是 HTML 页面，尝试提取 RSS 链接...")
                need_inspection.append((url, description, "可能是HTML页面"))
            elif "syntax error" in error_msg:
                print(f"   💡 语法错误，可能是格式问题")
                need_inspection.append((url, description, "语法错误"))
            else:
                need_inspection.append((url, description, error_msg))
                
        elif not feed.entries:
            print(f"   ⚠️  没有找到条目")
            if feed.feed.get('title'):
                print(f"       标题: {feed.feed.get('title')}")
            need_inspection.append((url, description, "没有条目"))
        else:
            print(f"   ✅ 解析成功!")
            print(f"       标题: {feed.feed.get('title', '无标题')}")
            print(f"       条目数: {len(feed.entries)}")
            if feed.entries:
                print(f"       最新: {feed.entries[0].title[:60]}...")
            valid_urls.append((url, description, feed))
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        need_inspection.append((url, description, str(e)))
    
    print()

print("=" * 60)
print(f"📊 测试结果:")
print(f"   有效的: {len(valid_urls)} 个")
print(f"   需要检查: {len(need_inspection)} 个")

if valid_urls:
    print(f"\n🎉 找到有效的 RSS 地址:")
    for url, description, feed in valid_urls:
        print(f"   • {description}")
        print(f"     地址: {url}")
        print(f"     标题: {feed.feed.get('title')}")
        print(f"     条目数: {len(feed.entries)}")
        
        # 立即添加到数据库
        print(f"   🚀 立即添加到数据库:")
        print(f"      sqlite3 data/castmind.db \"UPDATE podcasts SET rss_url='{url}', enabled=1 WHERE name='知行小酒馆';\"")
else:
    print(f"\n❌ 未找到有效的 RSS 地址")

if need_inspection:
    print(f"\n🔍 需要进一步检查的地址:")
    for url, description, reason in need_inspection[:5]:  # 只显示前5个
        print(f"   • {description}")
        print(f"     地址: {url}")
        print(f"     原因: {reason}")

print(f"\n💡 下一步建议:")

if valid_urls:
    print(f"   1. 更新数据库中的 RSS 地址")
    print(f"   2. 启用播客订阅")
    print(f"   3. 测试处理流程")
    print(f"   4. 开始自动化处理")
else:
    print(f"   1. 手动访问小宇宙网站查找 RSS")
    print(f"   2. 检查播客页面源代码")
    print(f"   3. 使用浏览器开发者工具")
    print(f"   4. 查找 <link rel=\"alternate\" type=\"application/rss+xml\"> 标签")

print(f"\n🔧 手动查找 RSS 的方法:")
print(f"   1. 访问: https://www.xiaoyuzhoufm.com/podcast/{podcast_id}")
print(f"   2. 右键查看页面源代码")
print(f"   3. 搜索 'rss' 或 'feed'")
print(f"   4. 查找类似这样的链接:")
print(f"      <link rel=\"alternate\" type=\"application/rss+xml\" href=\"...\">")
print(f"   5. 复制 href 中的链接")

print(f"\n📝 知行小酒馆数据库状态:")
print(f"   名称: 知行小酒馆")
print(f"   当前RSS: https://rsshub.app/xiaoyuzhou/podcast/{podcast_id}")
print(f"   状态: 已添加但禁用（等待有效RSS）")
print(f"   分类: 投资理财")
print(f"   标签: 投资,理财,商业,金融")

print(f"\n🚀 立即操作:")
print(f"   1. 查看数据库: sqlite3 data/castmind.db \"SELECT name, rss_url, enabled FROM podcasts WHERE name='知行小酒馆';\"")
print(f"   2. 如果找到有效RSS: sqlite3 data/castmind.db \"UPDATE podcasts SET rss_url='新地址', enabled=1 WHERE name='知行小酒馆';\"")
print(f"   3. 测试处理: python real_process_podcast.py '知行小酒馆' 1")

print(f"\n🎯 当前重点:")
print(f"   ✅ 知行小酒馆已添加到数据库")
print(f"   ⏳ 等待正确的 RSS 链接")
print(f"   🚀 找到后立即可以处理")