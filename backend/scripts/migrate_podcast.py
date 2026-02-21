"""
数据库迁移脚本 - 添加播客相关字段
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "castmind.db")


def migrate():
    """执行数据库迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 检查并添加缺失的列
    columns_to_add = [
        ("feed_type", "VARCHAR(50) DEFAULT 'rss'"),
        ("is_podcast", "BOOLEAN DEFAULT 0"),
        ("audio_url", "VARCHAR(500)"),
        ("audio_type", "VARCHAR(50)"),
        ("audio_duration", "INTEGER"),
        ("audio_size", "INTEGER"),
        ("podcast_description", "TEXT"),
        ("transcript", "TEXT"),
        ("podcast_summary", "TEXT"),
        ("chapters", "TEXT"),
    ]

    for column_name, column_def in columns_to_add:
        try:
            # 检查列是否存在
            cursor.execute(f"PRAGMA table_info(articles)")
            columns = [row[1] for row in cursor.fetchall()]

            if column_name not in columns:
                cursor.execute(
                    f"ALTER TABLE articles ADD COLUMN {column_name} {column_def}"
                )
                print(f"添加列: {column_name}")
            else:
                print(f"列已存在: {column_name}")
        except Exception as e:
            print(f"添加列 {column_name} 失败: {e}")

    # 为 feeds 表添加 feed_type 列
    try:
        cursor.execute("PRAGMA table_info(feeds)")
        feed_columns = [row[1] for row in cursor.fetchall()]

        if "feed_type" not in feed_columns:
            cursor.execute(
                "ALTER TABLE feeds ADD COLUMN feed_type VARCHAR(50) DEFAULT 'rss'"
            )
            print("添加列: feed_type")
    except Exception as e:
        print(f"添加列 feed_type 失败: {e}")

    conn.commit()
    conn.close()
    print("数据库迁移完成")


if __name__ == "__main__":
    migrate()
