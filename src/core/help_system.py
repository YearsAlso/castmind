#!/usr/bin/env python3
"""
CastMind - 命令行帮助系统
"""

from typing import Dict, List
import sys

class HelpSystem:
    """帮助系统"""
    
    COMMANDS = {
        "start": {
            "description": "启动CastMind系统",
            "usage": "castmind.py start [--reload]",
            "examples": [
                "castmind.py start",
                "castmind.py start --reload"
            ]
        },
        "subscribe": {
            "description": "订阅播客",
            "usage": "castmind.py subscribe --name NAME --url URL",
            "examples": [
                "castmind.py subscribe --name '商业思维' --url 'https://example.com/rss'"
            ]
        },
        "process": {
            "description": "处理播客",
            "usage": "castmind.py process --name NAME [--limit N]",
            "examples": [
                "castmind.py process --name '商业思维'",
                "castmind.py process --name '商业思维' --limit 3"
            ]
        },
        "status": {
            "description": "显示系统状态",
            "usage": "castmind.py status [--detailed]",
            "examples": [
                "castmind.py status",
                "castmind.py status --detailed"
            ]
        },
        "config": {
            "description": "显示配置信息",
            "usage": "castmind.py config [--validate]",
            "examples": [
                "castmind.py config",
                "castmind.py config --validate"
            ]
        },
        "test": {
            "description": "运行测试",
            "usage": "castmind.py test [--coverage]",
            "examples": [
                "castmind.py test",
                "castmind.py test --coverage"
            ]
        }
    }
    
    @classmethod
    def show_help(cls, command: str = None):
        """显示帮助信息"""
        if command:
            if command in cls.COMMANDS:
                cmd_info = cls.COMMANDS[command]
                print(f"\n📖 命令: {command}")
                print("=" * 50)
                print(f"描述: {cmd_info['description']}")
                print(f"用法: {cmd_info['usage']}")
                print("\n示例:")
                for example in cmd_info['examples']:
                    print(f"  $ {example}")
            else:
                print(f"❌ 未知命令: {command}")
                cls.show_all_commands()
        else:
            cls.show_all_commands()
    
    @classmethod
    def show_all_commands(cls):
        """显示所有命令"""
        print("🧠🌊 CastMind - 播客智能流系统")
        print("=" * 50)
        print("\n可用命令:")
        print("-" * 30)
        
        for cmd, info in cls.COMMANDS.items():
            print(f"  {cmd:12} - {info['description']}")
        
        print("\n使用 'castmind.py <命令> --help' 查看详细帮助")
        print("或 'castmind.py help <命令>' 查看特定命令帮助")
    
    @classmethod
    def validate_command(cls, args: List[str]) -> bool:
        """验证命令参数"""
        if not args:
            return False
        
        command = args[0]
        if command not in cls.COMMANDS:
            print(f"❌ 错误: 未知命令 '{command}'")
            cls.show_all_commands()
            return False
        
        return True


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        HelpSystem.show_help(command)
    else:
        HelpSystem.show_all_commands()


if __name__ == "__main__":
    main()
