#!/usr/bin/env python3
"""
CastMind 订阅自动迁移脚本
自动从 podcast-ai-system 迁移播客订阅到 CastMind
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime


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
        
        cursor.execute("SELECT name, rss_url, enabled FROM podcast_subscriptions")
        subscriptions = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ 找到 {len(subscriptions)} 个播客订阅")
        return subscriptions
        
    except Exception as e:
        print(f"❌ 读取数据库失败: {e}")
        return []


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
        
        return podcast_count
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return 0


def create_cli_import_commands(subscriptions):
    """创建 CLI 导入命令"""
    print("\n📝 创建 CLI 导入命令...")
    
    commands = []
    for name, rss_url, enabled in subscriptions:
        if enabled:
            cmd = f'python castmind.py subscribe --name "{name}" --url "{rss_url}"'
            commands.append(cmd)
    
    commands_file = Path(__file__).parent / "import_commands.sh"
    with open(commands_file, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# CastMind 订阅导入命令\n")
        f.write("# 自动生成的导入命令\n\n")
        for cmd in commands:
            f.write(f"{cmd}\n")
    
    # 设置执行权限
    os.chmod(commands_file, 0o755)
    
    print(f"✅ CLI 导入命令创建完成: {commands_file}")
    return commands_file


def create_subscriptions_json(subscriptions):
    """创建订阅 JSON 文件"""
    print("\n📄 创建订阅 JSON 文件...")
    
    subscriptions_data = []
    for name, rss_url, enabled in subscriptions:
        subscriptions_data.append({
            "name": name,
            "rss_url": rss_url,
            "enabled": bool(enabled),
            "tags": get_tags_for_podcast(name)
        })
    
    json_file = Path(__file__).parent / "subscriptions.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(subscriptions_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 订阅 JSON 文件创建完成: {json_file}")
    return json_file


def get_tags_for_podcast(name):
    """根据播客名称获取标签"""
    tags_map = {
        "得到": ["知识付费", "学习", "商业"],
        "商业就是这样": ["商业", "案例", "分析"],
        "疯投圈": ["投资", "VC", "商业"],
        "硅谷101": ["科技", "硅谷", "创新"],
        "贝望录": ["营销", "品牌", "消费者"],
        "创业内幕": ["创业", "投资", "故事"],
        "高能量": ["商业思维", "决策", "方法论"],
        "乱翻书": ["互联网", "产品", "运营"]
    }
    
    return tags_map.get(name, ["播客"])


def show_next_steps(db_path, commands_file, json_file):
    """显示下一步操作"""
    print("\n🚀 下一步操作")
    print("=" * 60)
    
    print("\n1. 查看数据库:")
    print(f"   sqlite3 {db_path} \"SELECT name, rss_url FROM podcasts;\"")
    
    print("\n2. 运行导入命令:")
    print(f"   bash {commands_file}")
    
    print("\n3. 查看系统状态:")
    print("   python castmind.py status")
    
    print("\n4. 处理播客:")
    print("   python castmind.py process --name \"得到\" --limit 1")
    
    print("\n5. 查看订阅数据:")
    print(f"   cat {json_file}")
    
    print("\n💡 提示:")
    print("   - 确保已配置 API Key (config/.env)")
    print("   - 首次处理建议从少量开始")
    print("   - 可以分批处理避免 API 限制")


def main():
    """主函数"""
    print("📡 CastMind 播客订阅自动迁移")
    print("=" * 60)
    
    # 1. 获取旧订阅
    subscriptions = get_old_subscriptions()
    if not subscriptions:
        print("❌ 没有找到可迁移的订阅")
        return
    
    # 2. 显示找到的订阅
    print("\n📋 找到的播客订阅:")
    print("-" * 60)
    for name, rss_url, enabled in subscriptions:
        status = "✅ 启用" if enabled else "❌ 禁用"
        print(f"• {name} ({status})")
    
    # 3. 创建数据库
    db_path = create_castmind_database()
    if not db_path:
        return
    
    # 4. 迁移数据
    print("\n⏳ 开始自动迁移...")
    migrated_count = migrate_subscriptions(subscriptions, db_path)
    if migrated_count == 0:
        print("❌ 迁移失败")
        return
    
    # 5. 验证迁移
    verify_migration(db_path)
    
    # 6. 创建导入工具
    commands_file = create_cli_import_commands(subscriptions)
    json_file = create_subscriptions_json(subscriptions)
    
    # 7. 显示下一步
    show_next_steps(db_path, commands_file, json_file)
    
    print("\n" + "=" * 60)
    print("✅ 订阅自动迁移完成！")
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