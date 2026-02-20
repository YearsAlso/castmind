#!/usr/bin/env python3
"""
CastMind 订阅迁移脚本
从 podcast-ai-system 迁移播客订阅到 CastMind
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime


def print_header():
    """打印标题"""
    print("📡 CastMind 播客订阅迁移工具")
    print("=" * 60)
    print()


def get_old_subscriptions():
    """从旧系统获取订阅"""
    print("🔍 从 podcast-ai-system 获取订阅数据...")
    
    old_db_path = Path("/Volumes/MxStore/Project/podcast-ai-system/data/podcasts.db")
    
    if not old_db_path.exists():
        print(f"❌ 旧数据库不存在: {old_db_path}")
        return []
    
    try:
        conn = sqlite3.connect(old_db_path)
        cursor = conn.cursor()
        
        # 获取所有订阅
        cursor.execute("SELECT name, rss_url, enabled FROM podcast_subscriptions")
        subscriptions = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ 找到 {len(subscriptions)} 个播客订阅")
        return subscriptions
        
    except Exception as e:
        print(f"❌ 读取数据库失败: {e}")
        return []


def display_subscriptions(subscriptions):
    """显示订阅列表"""
    print("\n📋 找到的播客订阅:")
    print("-" * 60)
    
    for i, (name, rss_url, enabled) in enumerate(subscriptions, 1):
        status = "✅ 启用" if enabled else "❌ 禁用"
        print(f"{i:2d}. {name}")
        print(f"    RSS: {rss_url}")
        print(f"    状态: {status}")
        print()


def create_castmind_database():
    """创建 CastMind 数据库"""
    print("🗄️  创建 CastMind 数据库...")
    
    castmind_data_dir = Path(__file__).parent / "data"
    castmind_data_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = castmind_data_dir / "castmind.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建播客表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rss_url TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            tags TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, rss_url)
        )
        """)
        
        # 创建节目表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            podcast_id INTEGER,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            published_date DATETIME,
            downloaded BOOLEAN DEFAULT 0,
            transcribed BOOLEAN DEFAULT 0,
            summarized BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (podcast_id) REFERENCES podcasts (id)
        )
        """)
        
        # 创建处理记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER,
            status TEXT,
            transcript_path TEXT,
            summary_path TEXT,
            note_path TEXT,
            started_at DATETIME,
            completed_at DATETIME,
            error_message TEXT,
            FOREIGN KEY (episode_id) REFERENCES episodes (id)
        )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✅ 数据库创建完成: {db_path}")
        return db_path
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return None


def migrate_subscriptions(subscriptions, db_path):
    """迁移订阅到新数据库"""
    print("\n🚚 迁移订阅到 CastMind...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        migrated_count = 0
        skipped_count = 0
        
        for name, rss_url, enabled in subscriptions:
            # 检查是否已存在
            cursor.execute("SELECT id FROM podcasts WHERE name = ? OR rss_url = ?", 
                          (name, rss_url))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⚠️  跳过已存在的播客: {name}")
                skipped_count += 1
                continue
            
            # 插入新订阅
            cursor.execute("""
            INSERT INTO podcasts (name, rss_url, enabled, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """, (name, rss_url, enabled))
            
            print(f"✅ 迁移: {name}")
            migrated_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 迁移完成:")
        print(f"   成功迁移: {migrated_count} 个")
        print(f"   跳过重复: {skipped_count} 个")
        print(f"   总计: {len(subscriptions)} 个")
        
        return migrated_count
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return 0


def create_import_script(db_path):
    """创建导入脚本"""
    print("\n📝 创建导入脚本...")
    
    script_content = '''#!/usr/bin/env python3
"""
CastMind 订阅导入脚本
使用 CastMind CLI 命令导入订阅
"""

import subprocess
import sys
from pathlib import Path

def import_subscriptions():
    """导入订阅"""
    print("📡 使用 CastMind CLI 导入订阅")
    print("=" * 60)
    
    # 订阅列表（从旧数据库导出）
    subscriptions = [
        ("得到", "https://feeds.fireside.fm/dedao/rss"),
        ("商业就是这样", "https://feeds.fireside.fm/shangyejiushizheyang/rss"),
        ("疯投圈", "https://feeds.fireside.fm/fengtouquan/rss"),
        ("硅谷101", "https://feeds.fireside.fm/guigu101/rss"),
        ("贝望录", "https://feeds.fireside.fm/beiwanglu/rss"),
        ("创业内幕", "https://feeds.fireside.fm/chuangyeneimu/rss"),
        ("高能量", "https://feeds.fireside.fm/gaonengliang/rss"),
        ("乱翻书", "https://feeds.fireside.fm/luanfanshu/rss"),
    ]
    
    print(f"找到 {len(subscriptions)} 个播客订阅")
    print()
    
    imported_count = 0
    failed_count = 0
    
    for name, rss_url in subscriptions:
        print(f"导入: {name}")
        print(f"  RSS: {rss_url}")
        
        try:
            # 使用 CastMind CLI 命令
            cmd = [
                sys.executable, "castmind.py", "subscribe",
                "--name", name,
                "--url", rss_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ 导入成功")
                imported_count += 1
            else:
                print(f"  ❌ 导入失败: {result.stderr}")
                failed_count += 1
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            failed_count += 1
        
        print()
    
    print("=" * 60)
    print(f"导入完成:")
    print(f"  成功: {imported_count} 个")
    print(f"  失败: {failed_count} 个")
    print(f"  总计: {len(subscriptions)} 个")
    
    if failed_count == 0:
        print("✅ 所有订阅导入成功！")
    else:
        print("⚠️  部分订阅导入失败，请检查日志")

if __name__ == "__main__":
    import_subscriptions()
'''
    
    script_path = Path(__file__).parent / "import_subscriptions.py"
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 导入脚本创建完成: {script_path}")
    return script_path


def create_batch_file(subscriptions):
    """创建批量导入文件"""
    print("\n📋 创建批量导入文件...")
    
    batch_content = """# CastMind 批量导入文件
# 格式: 名称,RSS链接,标签（可选）

得到,https://feeds.fireside.fm/dedao/rss,知识付费,学习
商业就是这样,https://feeds.fireside.fm/shangyejiushizheyang/rss,商业,案例
疯投圈,https://feeds.fireside.fm/fengtouquan/rss,投资,VC
硅谷101,https://feeds.fireside.fm/guigu101/rss,科技,硅谷
贝望录,https://feeds.fireside.fm/beiwanglu/rss,营销,品牌
创业内幕,https://feeds.fireside.fm/chuangyeneimu/rss,创业,投资
高能量,https://feeds.fireside.fm/gaonengliang/rss,商业思维,决策
乱翻书,https://feeds.fireside.fm/luanfanshu/rss,互联网,产品
"""
    
    batch_path = Path(__file__).parent / "subscriptions_batch.csv"
    with open(batch_path, "w") as f:
        f.write(batch_content)
    
    print(f"✅ 批量导入文件创建完成: {batch_path}")
    return batch_path


def verify_migration(db_path):
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 统计播客数量
        cursor.execute("SELECT COUNT(*) FROM podcasts")
        podcast_count = cursor.fetchone()[0]
        
        # 获取播客列表
        cursor.execute("SELECT name, rss_url, enabled FROM podcasts ORDER BY name")
        podcasts = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ CastMind 数据库中有 {podcast_count} 个播客订阅")
        print()
        print("📋 当前订阅列表:")
        print("-" * 60)
        
        for name, rss_url, enabled in podcasts:
            status = "✅ 启用" if enabled else "❌ 禁用"
            print(f"• {name}")
            print(f"  状态: {status}")
            print(f"  RSS: {rss_url}")
            print()
        
        return podcast_count
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return 0


def show_next_steps(db_path, import_script_path, batch_file_path):
    """显示下一步操作"""
    print("\n🚀 下一步操作")
    print("=" * 60)
    
    print("\n1. 查看迁移结果:")
    print(f"   sqlite3 {db_path} \"SELECT name, rss_url FROM podcasts;\"")
    
    print("\n2. 使用导入脚本（推荐）:")
    print(f"   python {import_script_path}")
    
    print("\n3. 手动添加订阅:")
    print("   python castmind.py subscribe --name \"得到\" --url \"https://feeds.fireside.fm/dedao/rss\"")
    
    print("\n4. 查看系统状态:")
    print("   python castmind.py status")
    
    print("\n5. 处理播客:")
    print("   python castmind.py process --name \"得到\" --limit 1")
    
    print("\n6. 使用批量文件:")
    print(f"   # 编辑 {batch_file_path} 添加更多订阅")
    print("   # 然后使用批量导入功能")
    
    print("\n💡 提示:")
    print("   - 确保已配置 API Key (config/.env)")
    print("   - 首次处理建议从少量开始")
    print("   - 可以分批处理避免 API 限制")


def main():
    """主函数"""
    print_header()
    
    # 1. 获取旧订阅
    subscriptions = get_old_subscriptions()
    if not subscriptions:
        print("❌ 没有找到可迁移的订阅")
        return
    
    # 2. 显示订阅
    display_subscriptions(subscriptions)
    
    # 3. 确认迁移
    print("⚠️  确认迁移以上订阅到 CastMind？")
    confirm = input("   输入 'y' 继续，其他键取消: ").strip().lower()
    
    if confirm != 'y':
        print("❌ 迁移取消")
        return
    
    # 4. 创建数据库
    db_path = create_castmind_database()
    if not db_path:
        return
    
    # 5. 迁移数据
    migrated_count = migrate_subscriptions(subscriptions, db_path)
    if migrated_count == 0:
        print("❌ 迁移失败")
        return
    
    # 6. 创建导入工具
    import_script_path = create_import_script(db_path)
    batch_file_path = create_batch_file(subscriptions)
    
    # 7. 验证迁移
    verify_migration(db_path)
    
    # 8. 显示下一步
    show_next_steps(db_path, import_script_path, batch_file_path)
    
    print("\n" + "=" * 60)
    print("✅ 订阅迁移完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)