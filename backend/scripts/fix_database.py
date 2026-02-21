#!/usr/bin/env python3
"""
修复 CastMind 数据库初始化问题
"""

import os
import sys
import sqlite3
from pathlib import Path


def fix_database():
    """修复数据库问题"""
    print("🔧 修复 CastMind 数据库问题")
    print("=" * 50)

    # 数据库路径
    db_path = "data/castmind.db"
    db_dir = Path("data")

    print(f"📁 数据库路径: {db_path}")

    # 1. 确保数据目录存在
    if not db_dir.exists():
        print(f"📂 创建数据目录: {db_dir}")
        db_dir.mkdir(parents=True, exist_ok=True)

    # 2. 检查数据库文件
    if Path(db_path).exists():
        print(f"✅ 数据库文件已存在: {db_path}")

        # 检查表结构
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 检查 feeds 表
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='feeds'"
            )
            if cursor.fetchone():
                print("✅ feeds 表存在")
            else:
                print("❌ feeds 表不存在，将创建")

            # 检查 articles 表
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='articles'"
            )
            if cursor.fetchone():
                print("✅ articles 表存在")
            else:
                print("❌ articles 表不存在，将创建")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"❌ 检查数据库时出错: {e}")
    else:
        print(f"📝 数据库文件不存在，将创建: {db_path}")

    # 3. 直接使用 SQLite 创建表（绕过 SQLAlchemy 问题）
    print("\n🛠️ 直接创建数据库表...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建 feeds 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT '未分类',
                interval INTEGER DEFAULT 3600,
                status TEXT DEFAULT 'active',
                last_fetch TIMESTAMP,
                article_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 创建 feeds 表")

        # 创建 articles 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                content TEXT,
                summary TEXT,
                published_at TIMESTAMP,
                read_status BOOLEAN DEFAULT 0,
                processed_status BOOLEAN DEFAULT 0,
                keywords TEXT,
                sentiment TEXT,
                key_points TEXT,
                business_insights TEXT,
                technical_points TEXT,
                action_items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE
            )
        """)
        print("✅ 创建 articles 表")

        # 创建索引
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_articles_feed_id ON articles(feed_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_articles_read_status ON articles(read_status)"
        )
        print("✅ 创建索引")

        conn.commit()

        # 验证表创建
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📊 数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        print("\n🎉 数据库修复完成!")

    except Exception as e:
        print(f"❌ 创建表时出错: {e}")
        return False

    # 4. 创建日志目录
    logs_dir = db_dir / "logs"
    if not logs_dir.exists():
        print(f"\n📂 创建日志目录: {logs_dir}")
        logs_dir.mkdir(exist_ok=True)

    # 5. 测试 SQLAlchemy 连接
    print("\n🔗 测试 SQLAlchemy 连接...")
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(f"sqlite:///{db_path}")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result]
            print(f"✅ SQLAlchemy 连接成功，表数量: {len(tables)}")

        return True

    except Exception as e:
        print(f"❌ SQLAlchemy 连接测试失败: {e}")
        return False


def main():
    """主函数"""
    # 切换到项目目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    print(f"📁 工作目录: {project_dir}")

    # 修复数据库
    success = fix_database()

    if success:
        print("\n" + "=" * 50)
        print("✅ 所有修复完成!")
        print("=" * 50)
        print("\n🚀 现在可以启动 CastMind 服务:")
        print("   python main.py")
        print("\n或使用:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ 修复过程中出现问题")
        sys.exit(1)


if __name__ == "__main__":
    main()
