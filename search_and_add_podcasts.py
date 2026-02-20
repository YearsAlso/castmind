#!/usr/bin/env python3
"""
搜索并添加优质中文播客到 CastMind
基于常见的中文播客推荐
"""

import ssl
import sqlite3
import feedparser
from pathlib import Path
from datetime import datetime
import sys

# 禁用 SSL 验证（临时方案）
ssl._create_default_https_context = ssl._create_unverified_context

print("🔍 搜索优质中文播客")
print("=" * 60)
print("基于常见推荐和验证的 RSS 链接")
print("=" * 60)


def get_recommended_podcasts():
    """获取推荐的中文播客列表"""
    print("\n📋 推荐的中文播客列表")
    print("-" * 60)
    
    # 基于常见推荐的中文播客
    recommended_podcasts = [
        # 知识类播客
        {
            "name": "得到·李翔知识内参",
            "rss_url": "https://feeds.fireside.fm/lixiang/rss",
            "category": "知识付费",
            "tags": "知识,商业,学习",
            "description": "得到APP出品，商业知识精选"
        },
        {
            "name": "商业就是这样",
            "rss_url": "https://feeds.fireside.fm/shangyejiushizheyang/rss",
            "category": "商业分析",
            "tags": "商业,案例,分析",
            "description": "第一财经出品，真实商业案例解析"
        },
        {
            "name": "疯投圈",
            "rss_url": "https://feeds.fireside.fm/fengtouquan/rss",
            "category": "投资",
            "tags": "投资,VC,商业",
            "description": "投资视角看商业，VC行业洞察"
        },
        
        # 科技类播客
        {
            "name": "硅谷101",
            "rss_url": "https://feeds.fireside.fm/guigu101/rss",
            "category": "科技",
            "tags": "科技,硅谷,创新",
            "description": "硅谷科技公司动态，技术创新商业应用"
        },
        {
            "name": "乱翻书",
            "rss_url": "https://feeds.fireside.fm/luanfanshu/rss",
            "category": "互联网",
            "tags": "互联网,产品,运营",
            "description": "互联网行业分析，产品思维，运营策略"
        },
        
        # 商业思维类
        {
            "name": "高能量",
            "rss_url": "https://feeds.fireside.fm/gaonengliang/rss",
            "category": "商业思维",
            "tags": "商业思维,决策,方法论",
            "description": "商业思维训练，决策方法论"
        },
        {
            "name": "贝望录",
            "rss_url": "https://feeds.fireside.fm/beiwanglu/rss",
            "category": "营销",
            "tags": "营销,品牌,消费者",
            "description": "市场营销、品牌建设、消费者洞察"
        },
        
        # 创业类
        {
            "name": "创业内幕",
            "rss_url": "https://feeds.fireside.fm/chuangyeneimu/rss",
            "category": "创业",
            "tags": "创业,投资,故事",
            "description": "创业公司故事，投资逻辑，创业经验"
        },
        
        # 文化类
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
        
        # 英文播客（测试用）
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
        }
    ]
    
    print(f"找到 {len(recommended_podcasts)} 个推荐播客")
    print("分类覆盖: 知识付费, 商业分析, 投资, 科技, 互联网, 营销, 创业, 文化, 新闻")
    
    return recommended_podcasts


def test_rss_urls(podcasts):
    """测试 RSS 链接有效性"""
    print("\n🔍 测试 RSS 链接有效性")
    print("-" * 60)
    
    valid_podcasts = []
    invalid_podcasts = []
    
    for podcast in podcasts:
        name = podcast["name"]
        rss_url = podcast["rss_url"]
        
        print(f"\n测试: {name}")
        print(f"URL: {rss_url}")
        
        try:
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                print(f"  ❌ 解析错误: {feed.bozo_exception}")
                podcast["status"] = "invalid"
                podcast["error"] = str(feed.bozo_exception)
                invalid_podcasts.append(podcast)
            elif not feed.entries:
                print(f"  ⚠️  没有找到条目")
                podcast["status"] = "no_entries"
                invalid_podcasts.append(podcast)
            else:
                print(f"  ✅ 解析成功")
                print(f"    标题: {feed.feed.get('title', '无标题')}")
                print(f"    条目数: {len(feed.entries)}")
                if feed.entries:
                    print(f"    最新: {feed.entries[0].title[:50]}...")
                
                podcast["status"] = "valid"
                podcast["feed_title"] = feed.feed.get('title', '')
                podcast["entry_count"] = len(feed.entries)
                valid_podcasts.append(podcast)
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            podcast["status"] = "error"
            podcast["error"] = str(e)
            invalid_podcasts.append(podcast)
    
    print(f"\n📊 测试结果:")
    print(f"   有效的: {len(valid_podcasts)} 个")
    print(f"   无效的: {len(invalid_podcasts)} 个")
    print(f"   总计: {len(podcasts)} 个")
    
    return valid_podcasts, invalid_podcasts


def connect_database():
    """连接数据库"""
    print("\n🗄️  连接数据库...")
    
    db_path = Path(__file__).parent / "data" / "castmind.db"
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        print("   正在创建数据库...")
        
        # 创建数据库目录
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建播客表
        cursor.execute("""
        CREATE TABLE podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rss_url TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            tags TEXT,
            category TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, rss_url)
        )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✅ 数据库创建完成: {db_path}")
    
    conn = sqlite3.connect(db_path)
    print(f"✅ 数据库连接成功: {db_path}")
    
    return conn


def add_podcasts_to_database(conn, podcasts):
    """添加播客到数据库"""
    print("\n📝 添加播客到数据库...")
    
    cursor = conn.cursor()
    
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    for podcast in podcasts:
        name = podcast["name"]
        rss_url = podcast["rss_url"]
        category = podcast.get("category", "")
        tags = podcast.get("tags", "")
        description = podcast.get("description", "")
        
        # 检查是否已存在
        cursor.execute("SELECT id FROM podcasts WHERE name = ? OR rss_url = ?", 
                      (name, rss_url))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  跳过已存在的播客: {name}")
            skipped_count += 1
            continue
        
        try:
            # 插入新订阅
            cursor.execute("""
            INSERT INTO podcasts (name, rss_url, enabled, tags, category, description, created_at, updated_at)
            VALUES (?, ?, 1, ?, ?, ?, datetime('now'), datetime('now'))
            """, (name, rss_url, tags, category, description))
            
            print(f"✅ 添加: {name}")
            print(f"   分类: {category}")
            print(f"   标签: {tags}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ 添加失败: {name} - {e}")
            error_count += 1
    
    conn.commit()
    
    print(f"\n📊 添加结果:")
    print(f"   成功添加: {added_count} 个")
    print(f"   跳过重复: {skipped_count} 个")
    print(f"   添加失败: {error_count} 个")
    print(f"   总计处理: {len(podcasts)} 个")
    
    return added_count


def show_current_subscriptions(conn):
    """显示当前订阅"""
    print("\n📋 当前数据库中的播客订阅")
    print("-" * 60)
    
    cursor = conn.cursor()
    cursor.execute("""
    SELECT name, rss_url, category, tags, enabled 
    FROM podcasts 
    ORDER BY category, name
    """)
    
    podcasts = cursor.fetchall()
    
    if not podcasts:
        print("   暂无订阅")
        return
    
    # 按分类分组显示
    categories = {}
    for name, rss_url, category, tags, enabled in podcasts:
        if category not in categories:
            categories[category] = []
        categories[category].append((name, rss_url, tags, enabled))
    
    for category, items in categories.items():
        print(f"\n{category} ({len(items)}个):")
        for name, rss_url, tags, enabled in items:
            status = "✅" if enabled else "❌"
            print(f"  {status} {name}")
            print(f"     标签: {tags}")
            print(f"     RSS: {rss_url[:50]}...")
    
    print(f"\n📊 总计: {len(podcasts)} 个播客订阅")


def create_import_script(valid_podcasts):
    """创建导入脚本"""
    print("\n📝 创建导入脚本...")
    
    script_content = '''#!/usr/bin/env python3
"""
CastMind 播客导入脚本
自动添加验证有效的播客订阅
"""

import ssl
import subprocess
import sys

# 禁用 SSL 验证（临时方案）
ssl._create_default_https_context = ssl._create_unverified_context

print("📡 CastMind 播客自动导入")
print("=" * 60)

# 有效播客列表
valid_podcasts = [
'''
    
    for podcast in valid_podcasts:
        name = podcast["name"]
        rss_url = podcast["rss_url"]
        category = podcast.get("category", "")
        tags = podcast.get("tags", "")
        
        script_content += f'    ("{name}", "{rss_url}", "{category}", "{tags}"),\n'
    
    script_content += ''']

print(f"找到 {len(valid_podcasts)} 个有效播客")
print()

imported_count = 0
failed_count = 0

for name, rss_url, category, tags in valid_podcasts:
    print(f"导入: {name}")
    print(f"  分类: {category}")
    print(f"  标签: {tags}")
    print(f"  RSS: {rss_url}")
    
    try:
        # 使用 CastMind CLI 命令
        cmd = [
            sys.executable, "castmind_ssl_patched.py", "subscribe",
            "--name", name,
            "--url", rss_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ 导入成功")
            imported_count += 1
        else:
            print(f"  ❌ 导入失败: {result.stderr[:100]}...")
            failed_count += 1
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        failed_count += 1
    
    print()

print("=" * 60)
print(f"导入完成:")
print(f"  成功: {imported_count} 个")
print(f"  失败: {failed_count} 个")
print(f"  总计: {len(valid_podcasts)} 个")

if failed_count == 0:
    print("✅ 所有播客导入成功！")
else:
    print("⚠️  部分播客导入失败，请检查日志")

print("\n🚀 下一步:")
print("   运行: python castmind_ssl_patched.py status")
print("   运行: python castmind_ssl_patched.py process --name \\"播客名称\\" --limit 1")
'''

    script_path = Path(__file__).parent / "import_valid_podcasts.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 设置执行权限
    import os
    os.chmod(script_path, 0o755)
    
    print(f"✅ 导入脚本创建完成: {script_path}")
    return script_path


def show_next_steps(valid_count, invalid_count, import_script_path):
    """显示下一步操作"""
    print("\n🚀 下一步操作")
    print("=" * 60)
    
    print(f"\n📊 搜索结果:")
    print(f"   有效播客: {valid_count} 个")
    print(f"   无效链接: {invalid_count} 个")
    
    if valid_count > 0:
        print(f"\n1. 运行导入脚本:")
        print(f"   python {import_script_path}")
        
        print(f"\n2. 查看当前订阅:")
        print("   sqlite3 data/castmind.db \"SELECT name, category FROM podcasts;\"")
        
        print(f"\n3. 开始处理播客:")
        print("   python castmind_ssl_patched.py process-all --limit 1")
        
        print(f"\n4. 查看系统状态:")
        print("   python castmind_ssl_patched.py status")
    
    print(f"\n5. 手动添加播客:")
    print("   python castmind_ssl_patched.py subscribe --name \"播客名称\" --url \"RSS链接\"")
    
    print(f"\n6. 测试 RSS 链接:")
    print("   python test_all_rss.py")
    
    print(f"\n💡 建议:")
    print("   • 从少量播客开始测试")
    print("   • 分批处理避免 API 限制")
    print("   • 监控处理进度和日志")
    
    print(f"\n📚 推荐分类:")
    print("   • 知识付费: 得到系列")
    print("   • 商业分析: 商业就是这样、疯投圈")
    print("   • 科技互联网: 硅谷101、乱翻书")
    print("   • 创业投资: 创业内幕")
    print("   • 文化生活: 故事FM、日谈公园")


def main():
    """主函数"""
    # 1. 获取推荐播客
    recommended_podcasts = get_recommended_podcasts()
    
    # 2. 测试 RSS 链接
    valid_podcasts, invalid_podcasts = test_rss_urls(recommended_podcasts)
    
    if not valid_podcasts:
        print("\n❌ 没有找到有效的 RSS 链接")
        print("   可能需要更新 RSS 链接或检查网络")
        return
    
    # 3. 连接数据库
    conn = connect_database()
    
    # 4. 添加有效播客到数据库
    added_count = add_podcasts_to_database(conn, valid_podcasts)
    
    # 5. 显示当前订阅
    show_current_subscriptions(conn)
    
    # 6. 创建导入脚本
    import_script_path = create_import_script(valid_podcasts)
    
    # 7. 显示下一步
    show_next_steps(len(valid_podcasts), len(invalid_podcasts), import_script_path)
    
    # 关闭数据库连接
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 播客搜索和添加完成！")
    print("=" * 60)
    
    if added_count > 0:
        print(f"\n🎉 成功添加 {added_count} 个优质播客到 CastMind！")