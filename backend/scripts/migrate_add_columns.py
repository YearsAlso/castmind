"""
数据库迁移脚本 - 添加新字段
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
        ("key_points", "TEXT"),
        ("business_insights", "TEXT"),
        ("technical_points", "TEXT"),
        ("action_items", "TEXT"),
    ]

    for column_name, column_type in columns_to_add:
        try:
            # 检查列是否存在
            cursor.execute(f"PRAGMA table_info(articles)")
            columns = [row[1] for row in cursor.fetchall()]

            if column_name not in columns:
                cursor.execute(
                    f"ALTER TABLE articles ADD COLUMN {column_name} {column_type}"
                )
                print(f"添加列: {column_name}")
            else:
                print(f"列已存在: {column_name}")
        except Exception as e:
            print(f"添加列 {column_name} 失败: {e}")

    conn.commit()
    conn.close()
    print("数据库迁移完成")


if __name__ == "__main__":
    migrate()
