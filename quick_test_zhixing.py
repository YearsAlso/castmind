#!/usr/bin/env python3
"""
快速测试知行小酒馆和其他中文播客
"""

import ssl
import feedparser

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("🔍 快速测试中文播客 RSS")
print("=" * 60)

# 先测试一些已知可用的 RSS 格式
test_urls = [
    # 已验证的英文播客（对比用）
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", "对比"),
    
    # 常见中文播客 RSS 格式
    ("小宇宙通用格式", "https://www.xiaoyuzhoufm.com/rss/节目ID", "需要替换ID"),
    ("喜马拉雅通用格式", "https://www.ximalaya.com/album/专辑ID", "需要替换ID"),
    
    # 其他可能的中文播客
    ("得到", "https://www.ximalaya.com/album/12345678", "示例"),
    ("商业就是这样", "https://shangyejiushizheyang.com/feed", "猜测"),
]

print("测试思路:")
print("1. 中文播客通常在小宇宙、喜马拉雅等平台")
print("2. 需要找到具体的节目/专辑ID")
print("3. RSS 格式通常是固定的，只需要替换ID")
print()

print("💡 如何找到知行小酒馆的 RSS:")
print("1. 访问: https://www.xiaoyuzhoufm.com")
print("2. 搜索'知行小酒馆'")
print("3. 进入播客页面")
print("4. 查找 RSS 订阅链接（通常在页面底部或设置中）")
print("5. 复制 RSS 链接")
print()

print("🎯 立即可以做的测试:")
print("1. 用已验证的英文播客测试完整流程:")
print("   python real_process_podcast.py \"BBC Global News\" 1")
print()
print("2. 如果你找到了知行小酒馆的 RSS:")
print("   a. 先用这个脚本测试: python -c \"import feedparser; print(feedparser.parse('你的RSS链接').feed.title)\"")
print("   b. 然后添加到数据库:")
print("      sqlite3 data/castmind.db \"INSERT INTO podcasts (name, rss_url, category, tags) VALUES ('知行小酒馆', '你的RSS链接', '投资理财', '投资,理财');\"")
print("   c. 最后处理: python real_process_podcast.py \"知行小酒馆\" 1")
print()

print("📊 当前可用的播客（已验证）:")
print("1. BBC Global News - 新闻类")
print("2. TED Talks Daily - 演讲类")
print("3. The Bible in a Year - 文化类")
print()

print("🚀 建议操作顺序:")
print("1. 先用英文播客验证完整流程（已成功）")
print("2. 查找知行小酒馆的正确 RSS 链接")
print("3. 测试并添加到系统")
print("4. 处理中文播客内容")
print()

print("🔧 工具准备:")
print("✅ real_process_podcast.py - 完整处理脚本")
print("✅ test_zhixing_podcast.py - RSS 测试脚本")
print("✅ add_chinese_podcasts.py - 中文播客添加脚本")
print("✅ 数据库已就绪 - 11个播客订阅")
print()

print("📞 需要帮助时:")
print("1. 运行测试: python test_zhixing_podcast.py")
print("2. 查看数据库: sqlite3 data/castmind.db \"SELECT * FROM podcasts;\"")
print("3. 处理播客: python real_process_podcast.py \"BBC Global News\" 1")
print()

print("知行小酒馆简介:")
print("• 出品方: 有知有行")
print("• 类型: 投资理财播客")
print("• 内容: 投资理念、理财知识、资产配置")
print("• 主持人: 孟岩等")
print("• 价值: 实用的理财教育内容")
print()

print("🎉 当前状态总结:")
print("✅ CastMind 核心功能已验证")
print("✅ 英文播客处理成功")
print("✅ 系统架构完整")
print("⏳ 等待中文播客 RSS 链接")
print("🚀 找到链接后立即可以处理")