"""
数据库迁移脚本 - 阶段一扩展
添加 Task 表和扩展 Feed/Article 字段
"""

import sqlite3
import os
from pathlib import Path

# 获取 backend 目录的父目录（即项目根目录）
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "castmind.db"


def migrate():
    """执行数据库迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 检查并添加 feeds 表的新列
    feed_columns_to_add = [
        ("author", "VARCHAR(255)"),
        ("image_url", "VARCHAR(500)"),
        ("description", "TEXT"),
    ]

    print("=== 迁移 feeds 表 ===")
    for column_name, column_def in feed_columns_to_add:
        try:
            cursor.execute("PRAGMA table_info(feeds)")
            columns = [row[1] for row in cursor.fetchall()]

            if column_name not in columns:
                cursor.execute(
                    f"ALTER TABLE feeds ADD COLUMN {column_name} {column_def}"
                )
                print(f"✓ 添加列: feeds.{column_name}")
            else:
                print(f"  列已存在: feeds.{column_name}")
        except Exception as e:
            print(f"✗ 添加列 feeds.{column_name} 失败: {e}")

    # 2. 检查并添加 articles 表的新列
    article_columns_to_add = [
        ("author", "VARCHAR(255)"),
        ("audio_local_path", "VARCHAR(500)"),
        ("transcription_status", "VARCHAR(50) DEFAULT 'pending'"),
        ("analysis_status", "VARCHAR(50) DEFAULT 'pending'"),
    ]

    print("\n=== 迁移 articles 表 ===")
    for column_name, column_def in article_columns_to_add:
        try:
            cursor.execute("PRAGMA table_info(articles)")
            columns = [row[1] for row in cursor.fetchall()]

            if column_name not in columns:
                cursor.execute(
                    f"ALTER TABLE articles ADD COLUMN {column_name} {column_def}"
                )
                print(f"✓ 添加列: articles.{column_name}")
            else:
                print(f"  列已存在: articles.{column_name}")
        except Exception as e:
            print(f"✗ 添加列 articles.{column_name} 失败: {e}")

    # 3. 创建 tasks 表
    print("\n=== 创建 tasks 表 ===")
    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        )
        if cursor.fetchone():
            print("  tasks 表已存在")
        else:
            cursor.execute("""
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_id INTEGER,
                    article_id INTEGER,
                    task_type VARCHAR(50) NOT NULL,
                    task_name VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    result_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE SET NULL,
                    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE SET NULL
                )
            """)
            print("✓ 创建 tasks 表成功")
    except Exception as e:
        print(f"✗ 创建 tasks 表失败: {e}")

    conn.commit()
    conn.close()
    print("\n=== 迁移完成 ===")


if __name__ == "__main__":
    migrate()
