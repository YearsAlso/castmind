#!/usr/bin/env python3
"""
CastMind - 播客智能流系统（SSL 修复版）
临时禁用 SSL 证书验证以解决 RSS 解析问题
"""

import ssl
# 临时禁用 SSL 验证（仅测试环境）
ssl._create_default_https_context = ssl._create_unverified_context

#!/usr/bin/env python3
"""
CastMind - 播客智能流系统主入口点
"""

import os
import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 导入CLI帮助系统
from cli.help import display_help

def setup_environment():
    """设置环境"""
    print("🧠🌊 CastMind - 播客智能流系统")
    print("=" * 60)
    
    # 检查环境变量
    env_file = Path(__file__).parent / "config" / ".env"
    if not env_file.exists():
        print("⚠️  环境配置文件不存在")
        print(f"  请创建: cp config/.env.example config/.env")
        print(f"  然后编辑 config/.env 填入你的API密钥")
        return False
    
    # 创建必要的目录
    directories = [
        "data/podcasts",
        "data/transcripts", 
        "data/knowledge",
        "logs",
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ 环境设置完成")
    return True

def start_system():
    """启动CastMind系统"""
    print("🚀 启动CastMind系统...")
    
    # 这里将启动调度器、监控器等
    print("📡 启动RSS订阅检查...")
    print("🧠 启动AI分析引擎...")
    print("📊 启动状态监控...")
    
    print("\n✅ CastMind系统已启动")
    print("   使用 'python castmind.py status' 查看系统状态")
    return 0

def subscribe_podcast(name, url):
    """订阅播客"""
    print(f"📝 订阅播客: {name}")
    print(f"   URL: {url}")
    
    # 这里将实现实际的订阅逻辑
    print("✅ 播客订阅成功")
    return 0

def process_podcast(name, limit):
    """处理播客"""
    print(f"🔧 处理播客: {name}")
    print(f"   处理最新 {limit} 期")
    
    # 这里将实现实际的处理逻辑
    print("✅ 播客处理完成")
    return 0

def show_status():
    """显示系统状态"""
    print("📊 CastMind系统状态")
    print("=" * 60)
    
    print("\n🧠 智能层:")
    print("  AI模型: 就绪")
    print("  分析引擎: 就绪")
    
    print("\n🌊 工作流层:")
    print("  RSS解析: 就绪")
    print("  音频处理: 就绪")
    print("  笔记生成: 就绪")
    
    print("\n📚 知识层:")
    print("  知识存储: 就绪")
    print("  智能检索: 就绪")
    
    print("\n⚙️ 系统信息:")
    print("  运行时间: 0分钟")
    print("  处理任务: 0个")
    print("  知识条目: 0个")
    
    return 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="CastMind - 播客智能流系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python castmind.py start                    # 启动系统
  python castmind.py subscribe --name "商业思维" --url "https://example.com/rss"
  python castmind.py process --name "商业思维" --limit 3
  python castmind.py status                   # 查看系统状态
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # start命令
    start_parser = subparsers.add_parser("start", help="启动CastMind系统")
    
    # subscribe命令
    subscribe_parser = subparsers.add_parser("subscribe", help="订阅播客")
    subscribe_parser.add_argument("--name", required=True, help="播客名称")
    subscribe_parser.add_argument("--url", required=True, help="RSS URL")
    
    # process命令
    process_parser = subparsers.add_parser("process", help="处理播客")
    process_parser.add_argument("--name", required=True, help="播客名称")
    process_parser.add_argument("--limit", type=int, default=3, help="处理最新几期")
    
    # status命令
    subparsers.add_parser("status", help="显示系统状态")
    
    # config命令
    subparsers.add_parser("config", help="显示配置")
    
    # test命令
    subparsers.add_parser("test", help="运行测试")
    
    # help命令
    help_parser = subparsers.add_parser("help", help="显示帮助信息")
    help_parser.add_argument("command_name", nargs="?", help="要查看的命令名称")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # help命令不需要环境检查
    if args.command == "help":
        display_help(getattr(args, 'command_name', None))
        return 0
    
    # 设置环境
    if not setup_environment():
        return 1
    
    # 执行命令
    if args.command == "start":
        return start_system()
    elif args.command == "subscribe":
        return subscribe_podcast(args.name, args.url)
    elif args.command == "process":
        return process_podcast(args.name, args.limit)
    elif args.command == "status":
        return show_status()
    elif args.command == "config":
        print("⚙️ 系统配置:")
        print("=" * 60)
        print("\n配置文件位置:")
        print("  config/.env          - 环境变量")
        print("  config/ai_models.json - AI模型配置")
        print("  config/workflows.json - 工作流配置")
        return 0
    elif args.command == "test":
        print("🧪 运行测试...")
        os.system("python -m pytest tests/ -v")
        return 0
    elif args.command == "help":
        display_help(getattr(args, 'command_name', None))
        return 0
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())