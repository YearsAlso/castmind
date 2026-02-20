#!/usr/bin/env python3
"""
处理 RSSHub 地址
rsshub://xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216
"""

import ssl
import feedparser
import requests
from urllib.parse import urlparse

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("🔗 处理 RSSHub 地址")
print("=" * 60)

# 用户提供的 RSSHub 地址
rsshub_url = "rsshub://xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216"

print(f"原始 RSSHub 地址: {rsshub_url}")
print()

# RSSHub 地址转换
# rsshub://xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216
# 转换为: https://rsshub.app/xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216

# 提取路径部分
if rsshub_url.startswith("rsshub://"):
    path = rsshub_url[9:]  # 去掉 "rsshub://"
    converted_url = f"https://rsshub.app/{path}"
else:
    converted_url = rsshub_url

print(f"转换后的 HTTP URL: {converted_url}")
print()

# 方法1: 直接使用 feedparser（可能不行）
print("方法1: 使用 feedparser 直接解析...")
try:
    feed = feedparser.parse(converted_url)
    
    if feed.bozo:
        print(f"❌ feedparser 解析错误: {feed.bozo_exception}")
        print(f"   状态: {feed.get('status', '未知')}")
    elif not feed.entries:
        print(f"⚠️  没有找到条目")
        if feed.feed.get('title'):
            print(f"   标题: {feed.feed.get('title')}")
    else:
        print(f"✅ feedparser 解析成功!")
        print(f"   标题: {feed.feed.get('title', '无标题')}")
        print(f"   描述: {feed.feed.get('description', '无描述')[:100]}...")
        print(f"   条目数: {len(feed.entries)}")
        if feed.entries:
            print(f"   最新一期: {feed.entries[0].title}")
            print(f"   发布时间: {feed.entries[0].get('published', '未知')}")
            
except Exception as e:
    print(f"❌ feedparser 异常: {e}")

print()

# 方法2: 使用 requests 获取原始内容，然后手动解析
print("方法2: 使用 requests 获取原始内容...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(converted_url, headers=headers, timeout=10, verify=False)
    
    print(f"   状态码: {response.status_code}")
    print(f"   内容类型: {response.headers.get('content-type', '未知')}")
    print(f"   内容长度: {len(response.text)} 字节")
    
    if response.status_code == 200:
        # 检查内容类型
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/rss+xml' in content_type or 'application/xml' in content_type or 'text/xml' in content_type:
            print(f"   ✅ 是 XML/RSS 内容")
            
            # 保存到文件查看
            with open('/tmp/rsshub_test.xml', 'w', encoding='utf-8') as f:
                f.write(response.text[:2000])  # 只保存前2000字符
            
            print(f"   📄 已保存到 /tmp/rsshub_test.xml")
            print(f"   前500字符: {response.text[:500]}")
            
        elif 'text/html' in content_type:
            print(f"   ⚠️  是 HTML 内容，不是 RSS")
            print(f"   可能原因: RSSHub 返回了错误页面")
            print(f"   前200字符: {response.text[:200]}")
            
        else:
            print(f"   ℹ️  未知内容类型: {content_type}")
            print(f"   前200字符: {response.text[:200]}")
            
    else:
        print(f"   ❌ HTTP 请求失败: {response.status_code}")
        
except Exception as e:
    print(f"❌ requests 异常: {e}")

print()

# 方法3: 尝试其他可能的 RSSHub 实例
print("方法3: 尝试其他 RSSHub 实例...")
rsshub_instances = [
    "https://rsshub.app",  # 官方实例
    "https://rsshub.rssforever.com",  # 备用实例1
    "https://rsshub.uneasy.win",  # 备用实例2
    "https://rsshub-instance.herokuapp.com",  # 备用实例3
]

for instance in rsshub_instances:
    test_url = f"{instance}/{path}"
    print(f"   测试: {test_url}")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=5, verify=False)
        if response.status_code == 200:
            print(f"      ✅ 可用 (状态码: {response.status_code})")
            # 检查是否是 RSS
            content_type = response.headers.get('content-type', '').lower()
            if 'xml' in content_type:
                print(f"      📄 是 XML 内容")
                converted_url = test_url  # 更新为可用的 URL
                break
            else:
                print(f"      ⚠️  不是 XML: {content_type}")
        else:
            print(f"      ❌ 不可用 (状态码: {response.status_code})")
    except Exception as e:
        print(f"      ❌ 错误: {e}")

print()

# 方法4: 尝试小宇宙的直接 API
print("方法4: 尝试小宇宙直接 API...")
podcast_id = "6013f9f58e2f7ee375cf4216"
xiaoyuzhou_api_url = f"https://www.xiaoyuzhoufm.com/apiv2/podcast/{podcast_id}"
print(f"   API URL: {xiaoyuzhou_api_url}")

try:
    response = requests.get(xiaoyuzhou_api_url, headers=headers, timeout=5, verify=False)
    if response.status_code == 200:
        print(f"   ✅ API 调用成功")
        data = response.json()
        if data.get('data'):
            podcast_data = data['data']
            print(f"      标题: {podcast_data.get('title', '未知')}")
            print(f"      描述: {podcast_data.get('description', '未知')[:100]}...")
            # 尝试从 API 数据中提取 RSS
            if podcast_data.get('rss_url'):
                print(f"      📡 找到 RSS: {podcast_data.get('rss_url')}")
                converted_url = podcast_data.get('rss_url')
    else:
        print(f"   ❌ API 调用失败: {response.status_code}")
except Exception as e:
    print(f"   ❌ API 异常: {e}")

print()

print("=" * 60)
print(f"💡 RSSHub 使用说明:")
print(f"   RSSHub 地址格式: rsshub://{path}")
print(f"   需要转换为: https://rsshub.app/{path}")
print(f"   但 RSSHub 实例可能不稳定或需要配置")

print(f"\n🎯 建议操作:")
print(f"   1. 先测试 RSSHub 链接在浏览器中是否工作")
print(f"   2. 如果浏览器能打开，检查返回的内容类型")
print(f"   3. 可能需要配置 RSSHub 或使用其他实例")

print(f"\n🚀 如果找到可用的 RSS 地址:")
print(f"   1. 更新数据库:")
print(f"      sqlite3 data/castmind.db \"UPDATE podcasts SET rss_url='{converted_url}', enabled=1 WHERE name='知行小酒馆';\"")
print(f"   2. 测试处理:")
print(f"      python real_process_podcast.py '知行小酒馆' 1")

print(f"\n📝 知行小酒馆信息:")
print(f"   节目ID: 6013f9f58e2f7ee375cf4216")
print(f"   平台: 小宇宙")
print(f"   RSSHub路径: xiaoyuzhou/podcast/6013f9f58e2f7ee375cf4216")

print(f"\n🔧 调试建议:")
print(f"   1. 在浏览器中打开: {converted_url}")
print(f"   2. 查看页面源代码")
print(f"   3. 检查是否是有效的 RSS/XML")
print(f"   4. 如果不是，可能需要配置 RSSHub 路由")