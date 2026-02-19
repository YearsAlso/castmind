#!/usr/bin/env python3
"""
测试知行小酒馆播客的 RSS 地址
"""

import ssl
import feedparser

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("🔍 搜索知行小酒馆播客 RSS 地址")
print("=" * 60)

# 知行小酒馆可能的 RSS 地址（基于常见平台）
possible_rss_urls = [
    # 小宇宙平台（常见中文播客平台）
    "https://www.xiaoyuzhoufm.com/rss/5f0e2b6b418a84a162abc4a9",  # 知行小酒馆在小宇宙的ID
    
    # 喜马拉雅（另一个常见平台）
    "https://www.ximalaya.com/album/12345678",  # 需要实际专辑ID
    
    # 通用 RSS 格式
    "https://feeds.fireside.fm/zhixing/rss",
    "https://zhixing.fireside.fm/rss",
    
    # 其他可能格式
    "https://www.xiaoyuzhoufm.com/podcast/5f0e2b6b418a84a162abc4a9",
    "https://rss.xiaoyuzhoufm.com/5f0e2b6b418a84a162abc4a9",
    
    # 测试用已知可用的 RSS（对比验证）
    "http://feeds.bbci.co.uk/news/rss.xml",  # BBC News（对比用）
]

print(f"测试 {len(possible_rss_urls)} 个可能的 RSS 地址")
print()

valid_urls = []
invalid_urls = []

for i, rss_url in enumerate(possible_rss_urls, 1):
    print(f"{i}. 测试: {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"   ❌ 解析错误: {feed.bozo_exception}")
            invalid_urls.append((rss_url, str(feed.bozo_exception)))
        elif not feed.entries:
            print(f"   ⚠️  没有找到条目")
            print(f"      状态: {feed.get('status', '未知')}")
            if feed.feed.get('title'):
                print(f"      标题: {feed.feed.get('title')}")
            invalid_urls.append((rss_url, "没有条目"))
        else:
            print(f"   ✅ 解析成功")
            print(f"      标题: {feed.feed.get('title', '无标题')}")
            print(f"      描述: {feed.feed.get('description', '无描述')[:80]}...")
            print(f"      条目数: {len(feed.entries)}")
            if feed.entries:
                print(f"      最新: {feed.entries[0].title[:60]}...")
            
            valid_urls.append((rss_url, feed))
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        invalid_urls.append((rss_url, str(e)))
    
    print()

print("=" * 60)
print(f"📊 测试结果:")
print(f"   有效的: {len(valid_urls)} 个")
print(f"   无效的: {len(invalid_urls)} 个")

if valid_urls:
    print(f"\n✅ 找到有效的 RSS 地址:")
    for rss_url, feed in valid_urls:
        print(f"   • {rss_url}")
        print(f"     标题: {feed.feed.get('title')}")
        print(f"     条目数: {len(feed.entries)}")
else:
    print(f"\n❌ 未找到有效的 RSS 地址")

print(f"\n💡 如何找到知行小酒馆的 RSS:")
print(f"   1. 访问小宇宙网站: https://www.xiaoyuzhoufm.com")
print(f"   2. 搜索'知行小酒馆'")
print(f"   3. 在播客页面找到 RSS 订阅链接")
print(f"   4. 通常格式: https://www.xiaoyuzhoufm.com/rss/节目ID")

print(f"\n🚀 测试建议:")
print(f"   1. 先使用有效的英文播客测试流程")
print(f"   2. 找到准确的中文播客 RSS 后添加")
print(f"   3. 使用 test_all_rss.py 验证 RSS 链接")

print(f"\n📝 知行小酒馆简介:")
print(f"   • 类型: 投资理财类播客")
print(f"   • 内容: 投资理念、理财知识、商业分析")
print(f"   • 适合: 对投资理财感兴趣的用户")
print(f"   • 价值: 实用的理财知识和投资策略")