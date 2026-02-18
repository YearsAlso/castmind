#!/bin/bash
# OpenCode使用示例脚本
# 演示如何正确使用coding-agent技能中的opencode功能

set -e

PROJECT_DIR="/Users/mengxiang/Project/castmind"
export PATH="/usr/sbin:$PATH"

echo "🧩 OpenCode使用示例"
echo "========================"

# 示例1：查看OpenCode基本信息
echo "1. 查看OpenCode基本信息"
echo "------------------------"
opencode --help 2>&1 | head -20
echo

# 示例2：分析项目结构（简单命令）
echo "2. 分析项目结构"
echo "------------------------"
echo "项目目录: $PROJECT_DIR"
cd "$PROJECT_DIR"
find . -name "*.py" -type f | head -5 | while read file; do
    echo "  - $file"
done
echo

# 示例3：创建任务文件
echo "3. 创建OpenCode任务"
echo "------------------------"
TASK_FILE="$PROJECT_DIR/task_help_system.txt"
cat > "$TASK_FILE" << 'EOF'
任务：为CastMind创建一个命令行帮助系统

要求：
1. 创建一个help_system.py模块
2. 显示所有可用命令
3. 显示命令示例
4. 支持彩色输出
5. 集成到主程序castmind.py中

命令列表：
- start: 启动系统
- subscribe: 订阅播客
- process: 处理播客
- status: 系统状态
- config: 配置信息
- test: 运行测试
EOF

echo "任务文件已创建: $TASK_FILE"
cat "$TASK_FILE"
echo

# 示例4：演示如何调用OpenCode
echo "4. OpenCode调用示例"
echo "------------------------"
cat << 'EOF'
# 方法1：直接命令行（可能遇到证书问题）
PATH=/usr/sbin:$PATH opencode run "查看task_help_system.txt，创建帮助系统"

# 方法2：使用exec工具（推荐）
exec pty:true workdir:"$PROJECT_DIR" command:"PATH=/usr/sbin:$PATH opencode run '创建帮助系统'"

# 方法3：后台运行
exec pty:true workdir:"$PROJECT_DIR" background:true command:"PATH=/usr/sbin:$PATH opencode run '复杂任务...'"
EOF
echo

# 示例5：手动创建帮助系统（如果OpenCode失败）
echo "5. 手动创建帮助系统示例"
echo "------------------------"
HELP_FILE="$PROJECT_DIR/src/core/help_system.py"
cat > "$HELP_FILE" << 'EOF'
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
EOF

echo "帮助系统已创建: $HELP_FILE"
echo "文件内容预览:"
head -30 "$HELP_FILE"
echo "..."
echo

# 示例6：更新主程序
echo "6. 更新主程序集成帮助系统"
echo "------------------------"
# 备份原文件
cp "$PROJECT_DIR/castmind.py" "$PROJECT_DIR/castmind.py.backup"

# 创建更新脚本
UPDATE_SCRIPT="$PROJECT_DIR/scripts/update_help_integration.py"
cat > "$UPDATE_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
更新castmind.py集成帮助系统
"""

import re

def update_castmind_py():
    """更新castmind.py文件"""
    file_path = "castmind.py"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # 在import部分添加帮助系统导入
    if "from src.core.help_system import HelpSystem" not in content:
        # 找到最后一个import语句
        import_pattern = r'(^import .*|^from .* import .*)'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        
        if imports:
            last_import = imports[-1]
            new_import = last_import + "\nfrom src.core.help_system import HelpSystem"
            content = content.replace(last_import, new_import)
    
    # 在帮助命令处理部分添加帮助系统调用
    help_pattern = r'if args\.command == "help" or args\.command == "--help":'
    if help_pattern in content:
        # 已经存在帮助处理
        pass
    else:
        # 添加帮助处理
        main_pattern = r'def main\(\):'
        if main_pattern in content:
            # 在main函数中添加帮助处理
            main_content = '''def main():
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
    
    # 添加子命令
    # ... 现有代码 ...
    
    args = parser.parse_args()
    
    # 处理帮助命令
    if args.command == "help" or args.command == "--help" or not args.command:
        HelpSystem.show_all_commands()
        return
    
    # ... 其他命令处理 ...
'''
            # 这里简化处理，实际需要更精确的替换
            print("需要手动更新castmind.py集成帮助系统")
    
    # 保存更新
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"✅ 已更新: {file_path}")

if __name__ == "__main__":
    update_castmind_py()
EOF

chmod +x "$UPDATE_SCRIPT"
echo "更新脚本已创建: $UPDATE_SCRIPT"
echo

# 清理
echo "7. 清理临时文件"
echo "------------------------"
rm -f "$TASK_FILE"
echo "✅ 临时文件已清理"
echo

echo "🎉 OpenCode使用示例完成！"
echo "========================"
echo
echo "📝 总结："
echo "1. OpenCode需要正确的PATH设置（包含/usr/sbin）"
echo "2. 使用exec工具时，pty:true参数是必须的"
echo "3. 指定正确的工作目录很重要"
echo "4. 如果OpenCode遇到问题，可以手动实现功能"
echo "5. 复杂的任务可以先创建任务描述文件"