#!/usr/bin/env python3
"""
CastMind API Key 测试脚本
测试配置的 API Key 是否有效
"""

import os
import sys
from pathlib import Path
from openai import OpenAI


def load_env_config():
    """加载环境配置"""
    print("🔧 加载环境配置...")
    
    env_file = Path(__file__).parent / "config" / ".env"
    if not env_file.exists():
        print(f"❌ .env 文件不存在: {env_file}")
        return None
    
    config = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    
    print(f"✅ 加载配置完成，找到 {len(config)} 个配置项")
    return config


def test_openai_api(config):
    """测试 OpenAI API"""
    print("\n🔑 测试 OpenAI API...")
    
    api_key = config.get("OPENAI_API_KEY")
    base_url = config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    default_model = config.get("DEFAULT_AI_MODEL", "openai")
    
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY 配置")
        return False
    
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Base URL: {base_url}")
    print(f"   默认模型: {default_model}")
    
    try:
        # 创建客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("   🚀 测试 API 连接...")
        
        # 尝试一个简单的调用
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个测试助手"},
                {"role": "user", "content": "请回复'测试成功'"}
            ],
            max_tokens=10,
            timeout=10
        )
        
        if response.choices and response.choices[0].message.content:
            print(f"   ✅ API 测试成功!")
            print(f"   响应: {response.choices[0].message.content}")
            return True
        else:
            print("   ❌ API 响应异常")
            return False
            
    except Exception as e:
        print(f"   ❌ API 测试失败: {e}")
        return False


def test_deepseek_api(config):
    """测试 DeepSeek API"""
    print("\n🔍 测试 DeepSeek API...")
    
    api_key = config.get("DEEPSEEK_API_KEY") or config.get("OPENAI_API_KEY")
    base_url = config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if not api_key:
        print("❌ 未找到 API Key 配置")
        return False
    
    # 检查是否配置为 DeepSeek
    if "deepseek.com" not in base_url:
        print(f"   ℹ️  Base URL 不是 DeepSeek: {base_url}")
        print("   如果要测试 DeepSeek，请设置 OPENAI_BASE_URL=https://api.deepseek.com")
        return False
    
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Base URL: {base_url}")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("   🚀 测试 DeepSeek 连接...")
        
        # DeepSeek 支持的模型
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个测试助手"},
                {"role": "user", "content": "请用中文回复'DeepSeek测试成功'"}
            ],
            max_tokens=10,
            timeout=10
        )
        
        if response.choices and response.choices[0].message.content:
            print(f"   ✅ DeepSeek API 测试成功!")
            print(f"   响应: {response.choices[0].message.content}")
            return True
        else:
            print("   ❌ DeepSeek API 响应异常")
            return False
            
    except Exception as e:
        print(f"   ❌ DeepSeek API 测试失败: {e}")
        return False


def test_database():
    """测试数据库"""
    print("\n🗄️  测试数据库...")
    
    db_file = Path(__file__).parent / "data" / "castmind.db"
    
    if not db_file.exists():
        print(f"❌ 数据库文件不存在: {db_file}")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 检查播客表
        cursor.execute("SELECT COUNT(*) FROM podcasts")
        podcast_count = cursor.fetchone()[0]
        
        # 获取播客列表
        cursor.execute("SELECT name, rss_url FROM podcasts ORDER BY name")
        podcasts = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ 数据库连接正常")
        print(f"   播客数量: {podcast_count} 个")
        
        if podcasts:
            print("\n📋 当前订阅的播客:")
            for name, rss_url in podcasts:
                print(f"   • {name}")
                print(f"     {rss_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False


def test_rss_parsing():
    """测试 RSS 解析"""
    print("\n📡 测试 RSS 解析...")
    
    try:
        import feedparser
        
        # 测试一个简单的 RSS
        test_rss = "https://rss.art19.com/the-daily"
        print(f"   测试 RSS: {test_rss}")
        
        feed = feedparser.parse(test_rss)
        
        if feed.entries:
            print(f"   ✅ RSS 解析成功")
            print(f"   找到 {len(feed.entries)} 个条目")
            print(f"   最新标题: {feed.entries[0].title[:50]}...")
            return True
        else:
            print("   ❌ RSS 解析失败，没有找到条目")
            return False
            
    except Exception as e:
        print(f"   ❌ RSS 解析测试失败: {e}")
        return False


def test_full_workflow():
    """测试完整工作流"""
    print("\n🔧 测试完整工作流...")
    
    # 检查必要的目录
    directories = ["data/transcripts", "data/summaries", "data/notes", "logs"]
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ 目录检查: {directory}")
    
    # 检查配置文件
    config_files = ["config/.env", "config/ai_models.json", "config/workflows.json"]
    for config_file in config_files:
        file_path = Path(__file__).parent / config_file
        if file_path.exists():
            print(f"   ✅ 配置文件: {config_file}")
        else:
            print(f"   ❌ 配置文件缺失: {config_file}")
    
    return True


def show_next_steps(config):
    """显示下一步操作"""
    print("\n🚀 下一步操作")
    print("=" * 60)
    
    api_key = config.get("OPENAI_API_KEY", "")
    base_url = config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    default_model = config.get("DEFAULT_AI_MODEL", "openai")
    
    print(f"当前配置:")
    print(f"  API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"  Base URL: {base_url}")
    print(f"  默认模型: {default_model}")
    print()
    
    print("1. 测试处理单个播客:")
    print("   python castmind.py process --name \"得到\" --limit 1 --verbose")
    print()
    
    print("2. 查看系统状态:")
    print("   python castmind.py status")
    print()
    
    print("3. 查看所有播客:")
    print("   sqlite3 data/castmind.db \"SELECT name, rss_url FROM podcasts;\"")
    print()
    
    print("4. 运行快速开始向导:")
    print("   ./quick_start.sh")
    print()
    
    print("5. 查看日志:")
    print("   tail -f logs/castmind.log")
    print()
    
    print("💡 提示:")
    print("   - 首次处理建议从少量开始")
    print("   - 可以监控日志了解处理进度")
    print("   - 如果遇到 API 限制，可以分批处理")


def main():
    """主函数"""
    print("🧪 CastMind API Key 测试")
    print("=" * 60)
    
    # 加载配置
    config = load_env_config()
    if not config:
        return
    
    # 运行测试
    tests = []
    
    # 测试 OpenAI API
    if config.get("OPENAI_API_KEY"):
        tests.append(("OpenAI API", test_openai_api(config)))
    
    # 测试 DeepSeek API（如果配置了）
    if "deepseek.com" in config.get("OPENAI_BASE_URL", ""):
        tests.append(("DeepSeek API", test_deepseek_api(config)))
    
    # 测试数据库
    tests.append(("数据库", test_database()))
    
    # 测试 RSS 解析
    tests.append(("RSS 解析", test_rss_parsing()))
    
    # 测试完整工作流
    tests.append(("工作流配置", test_full_workflow()))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("-" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, test_result in tests:
        status = "✅ 通过" if test_result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if test_result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！可以开始使用 CastMind")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试未通过")
    
    # 显示下一步
    show_next_steps(config)
    
    print("\n" + "=" * 60)
    print("💡 需要更多帮助？")
    print("   查看 RSS_配置指南.md 获取详细说明")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)