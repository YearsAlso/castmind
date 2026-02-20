#!/usr/bin/env python3
"""
更新数据库表结构
添加 category 和 description 字段
"""

import sqlite3
from pathlib import Path

print("🔧 更新数据库表结构")
print("=" * 60)

db_path = Path(__file__).parent / "data" / "castmind.db"

if not db_path.exists():
    print(f"❌ 数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("当前表结构:")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='podcasts'")
table_sql = cursor.fetchone()[0]
print(table_sql)

print("\n📝 更新表结构...")

try:
    # 创建新表
    cursor.execute("""
    CREATE TABLE podcasts_new (
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
    
    # 复制数据
    cursor.execute("""
    INSERT INTO podcasts_new (id, name, rss_url, enabled, tags, created_at, updated_at)
    SELECT id, name, rss_url, enabled, tags, created_at, updated_at
    FROM podcasts
    """)
    
    # 删除旧表
    cursor.execute("DROP TABLE podcasts")
    
    # 重命名新表
    cursor.execute("ALTER TABLE podcasts_new RENAME TO podcasts")
    
    conn.commit()
    
    print("✅ 表结构更新成功")
    
    # 显示更新后的结构
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='podcasts'")
    new_table_sql = cursor.fetchone()[0]
    print("\n更新后的表结构:")
    print(new_table_sql)
    
    # 显示当前数据
    print("\n📋 当前播客数据:")
    cursor.execute("SELECT name, rss_url, enabled FROM podcasts")
    podcasts = cursor.fetchall()
    
    for name, rss_url, enabled in podcasts:
        status = "✅ 启用" if enabled else "❌ 禁用"
        print(f"• {name} ({status})")
        print(f"  RSS: {rss_url[:50]}...")
    
    print(f"\n📊 总计: {len(podcasts)} 个播客订阅")
    
except Exception as e:
    print(f"❌ 更新失败: {e}")
    conn.rollback()

conn.close()

print("\n" + "=" * 60)
print("✅ 数据库更新完成")
print("=" * 60)