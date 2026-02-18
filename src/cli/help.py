#!/usr/bin/env python3
"""
CastMind命令行帮助系统
"""

import sys
from typing import Dict, List, Optional


class CastMindHelp:
    """CastMind命令行帮助系统"""
    
    def __init__(self):
        self.commands = {
            "start": {
                "description": "启动CastMind系统",
                "usage": "python castmind.py start",
                "examples": [
                    "python castmind.py start"
                ],
                "details": "启动CastMind播客智能流系统的所有组件，包括RSS订阅检查、AI分析引擎和状态监控。"
            },
            "subscribe": {
                "description": "订阅新播客",
                "usage": "python castmind.py subscribe --name <播客名称> --url <RSS地址>",
                "examples": [
                    "python castmind.py subscribe --name \"商业思维\" --url \"https://example.com/rss\"",
                    "python castmind.py subscribe --name \"科技前沿\" --url \"https://tech.example.com/feed.xml\""
                ],
                "details": "添加新的播客RSS源到CastMind系统，系统将自动监控该播客的更新。"
            },
            "process": {
                "description": "处理指定播客",
                "usage": "python castmind.py process --name <播客名称> [--limit <期数>]",
                "examples": [
                    "python castmind.py process --name \"商业思维\"",
                    "python castmind.py process --name \"科技前沿\" --limit 5"
                ],
                "details": "处理指定播客的最新内容，包括音频转录、内容分析和知识提取。"
            },
            "status": {
                "description": "显示系统状态",
                "usage": "python castmind.py status",
                "examples": [
                    "python castmind.py status"
                ],
                "details": "查看CastMind系统的运行状态，包括各组件状态、处理任务统计等信息。"
            },
            "config": {
                "description": "显示配置信息",
                "usage": "python castmind.py config",
                "examples": [
                    "python castmind.py config"
                ],
                "details": "显示CastMind系统的配置文件位置和当前配置状态。"
            },
            "test": {
                "description": "运行系统测试",
                "usage": "python castmind.py test",
                "examples": [
                    "python castmind.py test"
                ],
                "details": "运行CastMind系统的单元测试和集成测试，验证系统功能正常。"
            },
            "help": {
                "description": "显示帮助信息",
                "usage": "python castmind.py help [命令名称]",
                "examples": [
                    "python castmind.py help",
                    "python castmind.py help subscribe",
                    "python castmind.py help process"
                ],
                "details": "显示CastMind系统命令的帮助信息，可以查看所有命令或特定命令的详细说明。"
            }
        }
        
        self.sections = {
            "getting-started": {
                "title": "快速开始",
                "content": [
                    "1. 配置环境: cp config/.env.example config/.env",
                    "2. 编辑配置: 填入你的API密钥",
                    "3. 启动系统: python castmind.py start",
                    "4. 订阅播客: python castmind.py subscribe --name <名称> --url <RSS>",
                    "5. 查看状态: python castmind.py status"
                ]
            },
            "examples": {
                "title": "使用示例",
                "content": [
                    "# 订阅播客",
                    "python castmind.py subscribe --name \"商业思维\" --url \"https://example.com/rss\"",
                    "",
                    "# 处理最新3期内容",
                    "python castmind.py process --name \"商业思维\" --limit 3",
                    "",
                    "# 查看系统状态",
                    "python castmind.py status",
                    "",
                    "# 运行测试",
                    "python castmind.py test"
                ]
            }
        }
    
    def show_command_help(self, command: Optional[str] = None) -> None:
        """显示命令帮助信息"""
        if command is None:
            self.show_overview()
            return
        
        if command not in self.commands:
            print(f"❌ 未知命令: {command}")
            print(f"使用 'python castmind.py help' 查看所有可用命令")
            return
        
        cmd_info = self.commands[command]
        
        print(f"📖 命令: {command}")
        print("=" * 60)
        print(f"📝 描述: {cmd_info['description']}")
        print(f"🔧 用法: {cmd_info['usage']}")
        
        print("\n💡 示例:")
        for example in cmd_info['examples']:
            print(f"   {example}")
        
        print(f"\n📋 详细说明:")
        print(f"   {cmd_info['details']}")
        
        # 显示相关命令
        related_commands = self._get_related_commands(command)
        if related_commands:
            print(f"\n🔗 相关命令:")
            for related_cmd in related_commands:
                print(f"   {related_cmd} - {self.commands[related_cmd]['description']}")
    
    def show_overview(self) -> None:
        """显示系统概览帮助"""
        print("🧠🌊 CastMind - 播客智能流系统")
        print("=" * 60)
        print("CastMind是一个智能播客处理系统，能够自动订阅、转录、分析和存储播客内容。")
        print()
        
        # 显示可用命令
        print("📋 可用命令:")
        print("-" * 40)
        for cmd, info in self.commands.items():
            if cmd != "help":
                print(f"  {cmd:<12} - {info['description']}")
        
        # 显示快速开始
        print("\n🚀 快速开始:")
        print("-" * 40)
        for step in self.sections["getting-started"]["content"]:
            print(f"  {step}")
        
        print(f"\n💡 获取帮助:")
        print(f"  python castmind.py help           # 显示所有命令")
        print(f"  python castmind.py help <命令>     # 显示特定命令帮助")
        
        print(f"\n📖 更多信息:")
        print(f"  查看 README.md 获取详细文档")
        print(f"  查看 docs/ 目录获取技术文档")
    
    def show_examples(self) -> None:
        """显示使用示例"""
        print("📖 CastMind 使用示例")
        print("=" * 60)
        
        for example in self.sections["examples"]["content"]:
            print(example)
    
    def _get_related_commands(self, command: str) -> List[str]:
        """获取相关命令"""
        related_map = {
            "start": ["status", "config"],
            "subscribe": ["process", "status"],
            "process": ["subscribe", "status"],
            "status": ["start", "config"],
            "config": ["start"],
            "test": ["start", "status"]
        }
        return related_map.get(command, [])
    
    def format_command_list(self) -> str:
        """格式化命令列表为字符串"""
        lines = ["可用命令:"]
        for cmd, info in self.commands.items():
            if cmd != "help":
                lines.append(f"  {cmd:<12} - {info['description']}")
        return "\n".join(lines)


def display_help(command: Optional[str] = None) -> None:
    """显示帮助信息的便捷函数"""
    help_system = CastMindHelp()
    help_system.show_command_help(command)


def main() -> None:
    """帮助系统主函数（独立运行时使用）"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CastMind帮助系统")
    parser.add_argument("command", nargs="?", help="要查看的命令名称")
    parser.add_argument("--examples", action="store_true", help="显示使用示例")
    
    args = parser.parse_args()
    
    help_system = CastMindHelp()
    
    if args.examples:
        help_system.show_examples()
    else:
        help_system.show_command_help(args.command)


if __name__ == "__main__":
    main()