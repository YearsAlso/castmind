#!/usr/bin/env python3
"""
CastMind 配置测试脚本
测试 API Key 和 RSS 配置
"""

import os
import sys
from pathlib import Path


def test_api_key():
    """测试 API Key 配置"""
    print("🔑 测试 API Key 配置")
    print("-" * 40)
    
    # 检查 .env 文件
    env_file = Path("config/.env")
    if not env_file.exists():
        print("❌ .env 文件不存在")
        print("   请运行: cp config/.env.example config/.env")
        print("   然后编辑 config/.env 填入你的 API Key")
        return False
    
    # 读取 API Key
    api_key = None
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break
    
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY 配置")
        return False
    
    if "你的OpenAI_API_Key_在这里" in api_key:
        print("❌ 请将 OPENAI_API_KEY 替换为你的实际 API Key")
        print(f"   当前值: {api_key}")
        return False
    
    print(f"✅ API Key 已配置: {api_key[:10]}...{api_key[-4:]}")
    return True


def test_python_environment():
    """测试 Python 环境"""
    print("\n🐍 测试 Python 环境")
    print("-" * 40)
    
    try:
        # 检查必要的包
        import sqlite3
        print("✅ sqlite3: 可用")
        
        try:
            import openai
            print("✅ openai: 已安装")
        except ImportError:
            print("⚠️  openai: 未安装，运行: pip install openai")
            
        try:
            import feedparser
            print("✅ feedparser: 已安装")
        except ImportError:
            print("⚠️  feedparser: 未安装，运行: pip install feedparser")
            
        return True
        
    except Exception as e:
        print(f"❌ Python 环境错误: {e}")
        return False


def test_database():
    """测试数据库"""
    print("\n🗄️  测试数据库")
    print("-" * 40)
    
    db_file = Path("data/castmind.db")
    
    if db_file.exists():
        print(f"✅ 数据库文件存在: {db_file}")
        
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 检查表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"✅ 数据库表: {len(tables)} 个")
            for table in tables:
                print(f"   - {table[0]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 数据库错误: {e}")
            return False
    else:
        print("⚠️  数据库文件不存在，首次运行时会自动创建")
        return True


def test_rss_example():
    """测试 RSS 示例"""
    print("\n📡 测试 RSS 示例")
    print("-" * 40)
    
    print("以下是一些可用的 RSS 示例链接：")
    print()
    print("1. 测试用 RSS（英文，稳定）:")
    print("   https://rss.art19.com/the-daily")
    print("   名称: The Daily")
    print("   标签: 新闻,测试")
    print()
    print("2. BBC 新闻（英文）:")
    print("   https://feeds.bbci.co.uk/news/rss.xml")
    print("   名称: BBC News")
    print("   标签: 新闻,国际")
    print()
    print("3. TED Talks（英文）:")
    print("   https://feeds.feedburner.com/TedTalks_audio")
    print("   名称: TED Talks")
    print("   标签: 演讲,知识")
    print()
    print("💡 提示：")
    print("   首次测试建议使用英文 RSS，避免编码问题")
    print("   找到中文 RSS 后，可以用同样的方法添加")
    
    return True


def show_next_steps():
    """显示下一步操作"""
    print("\n🚀 下一步操作")
    print("=" * 60)
    
    print("\n1. 配置 API Key:")
    print("   编辑 config/.env 文件")
    print("   将 OPENAI_API_KEY 替换为你的实际 Key")
    print()
    print("2. 安装依赖包:")
    print("   pip install openai feedparser")
    print()
    print("3. 添加第一个 RSS 订阅:")
    print("   python castmind.py add --url \"RSS链接\" --name \"播客名称\"")
    print()
    print("4. 处理第一期节目:")
    print("   python castmind.py process --name \"播客名称\" --limit 1")
    print()
    print("5. 查看结果:")
    print("   ls -la data/transcripts/")
    print("   ls -la data/summaries/")
    print("   ls -la data/notes/")
    print()
    print("📝 详细指南:")
    print("   查看 RSS_配置指南.md 获取完整说明")


def main():
    """主函数"""
    print("🧪 CastMind 配置测试")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = Path.cwd()
    expected_dir = Path("/Volumes/MxStore/Project/castmind")
    
    if current_dir != expected_dir:
        print(f"⚠️  建议在项目目录运行:")
        print(f"   cd {expected_dir}")
        print(f"   当前目录: {current_dir}")
        print()
    
    # 运行测试
    tests_passed = 0
    tests_total = 4
    
    if test_api_key():
        tests_passed += 1
    
    if test_python_environment():
        tests_passed += 1
    
    if test_database():
        tests_passed += 1
    
    test_rss_example()  # 这个总是返回 True
    
    # 显示结果
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {tests_passed}/{tests_total} 通过")
    
    if tests_passed == tests_total:
        print("✅ 所有测试通过！可以开始使用 CastMind")
    else:
        print("⚠️  有些测试未通过，请根据提示修复")
    
    # 显示下一步
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("💡 需要更多帮助？")
    print("   查看 RSS_配置指南.md 获取详细说明")
    print("   或运行: python castmind.py --help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)