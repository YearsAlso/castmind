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
