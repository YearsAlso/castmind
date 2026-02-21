#!/usr/bin/env python3
"""
数据库迁移脚本 - 为现有数据库添加新字段
"""

import os
import sys
import sqlite3
from pathlib import Path


def migrate_existing_database():
    """为现有数据库添加新字段"""
    print("🔧 迁移现有数据库 - 添加文章分析字段")
    print("=" * 50)

    # 数据库路径
    db_path = "data/castmind.db"

    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查现有字段
        cursor.execute("PRAGMA table_info(articles)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"📊 当前 articles 表字段: {', '.join(columns)}")

        # 需要添加的字段
        fields_to_add = [
            ("key_points", "TEXT"),
            ("business_insights", "TEXT"),
            ("technical_points", "TEXT"),
            ("action_items", "TEXT"),
        ]

        added_fields = []
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                print(f"➕ 添加字段: {field_name}")
                cursor.execute(
                    f"ALTER TABLE articles ADD COLUMN {field_name} {field_type}"
                )
                added_fields.append(field_name)
            else:
                print(f"✅ 字段已存在: {field_name}")

        if added_fields:
            print(
                f"🎉 成功添加 {len(added_fields)} 个新字段: {', '.join(added_fields)}"
            )
        else:
            print("ℹ️ 所有字段都已存在，无需迁移")

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False


def main():
    """主函数"""
    # 切换到项目目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    print(f"📁 工作目录: {project_dir}")

    # 执行迁移
    success = migrate_existing_database()

    if success:
        print("\n" + "=" * 50)
        print("✅ 数据库迁移完成!")
        print("=" * 50)
        print("\n🚀 现在可以启动 CastMind 服务:")
        print("   python main.py")
    else:
        print("\n❌ 迁移过程中出现问题")
        sys.exit(1)


if __name__ == "__main__":
    main()
