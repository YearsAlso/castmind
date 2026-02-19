#!/usr/bin/env python3
"""
临时修复 SSL 证书问题
在代码中禁用 SSL 验证（仅用于测试）
"""

import ssl
import os
import sys
from pathlib import Path


def disable_ssl_verification():
    """禁用 SSL 验证"""
    print("🔧 禁用 SSL 证书验证...")
    
    # 创建不验证 SSL 的上下文
    ssl._create_default_https_context = ssl._create_unverified_context
    
    print("✅ SSL 验证已禁用（仅本次会话有效）")
    print("⚠️  警告：仅用于测试环境，生产环境请安装正确的 SSL 证书")
    
    return True


def test_rss_without_ssl():
    """测试禁用 SSL 后的 RSS 解析"""
    print("\n📡 测试 RSS 解析（禁用 SSL 后）...")
    
    import feedparser
    
    # 测试多个 RSS 链接
    test_rss_list = [
        ("得到", "https://feeds.fireside.fm/dedao/rss"),
        ("商业就是这样", "https://feeds.fireside.fm/shangyejiushizheyang/rss"),
        ("疯投圈", "https://feeds.fireside.fm/fengtouquan/rss"),
        ("硅谷101", "https://feeds.fireside.fm/guigu101/rss"),
        ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),  # HTTP
    ]
    
    working_rss = []
    
    for name, rss_url in test_rss_list:
        print(f"\n测试: {name}")
        print(f"URL: {rss_url}")
        
        try:
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                print(f"  ❌ 解析错误: {feed.bozo_exception}")
            elif not feed.entries:
                print(f"  ⚠️  没有找到条目")
                print(f"    状态: {feed.get('status', '未知')}")
                if feed.feed.get('title'):
                    print(f"    标题: {feed.feed.get('title')}")
            else:
                print(f"  ✅ 解析成功")
                print(f"    标题: {feed.feed.get('title', '无标题')}")
                print(f"    条目数: {len(feed.entries)}")
                if feed.entries:
                    print(f"    最新: {feed.entries[0].title[:50]}...")
                
                working_rss.append((name, rss_url))
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    return working_rss


def create_ssl_fix_wrapper():
    """创建 SSL 修复包装脚本"""
    print("\n📝 创建 SSL 修复包装脚本...")
    
    wrapper_content = '''#!/usr/bin/env python3
"""
CastMind SSL 修复包装脚本
在运行 CastMind 前自动修复 SSL 证书问题
"""

import ssl
import sys
import os

# 禁用 SSL 验证（临时解决方案）
ssl._create_default_https_context = ssl._create_unverified_context

print("🔧 SSL 证书验证已临时禁用")
print("⚠️  注意：仅用于测试环境")

# 导入并运行原始的 castmind.py
if __name__ == "__main__":
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 导入原始模块
    import castmind
    
    # 运行原始的主函数
    castmind.main()
'''
    
    wrapper_path = Path(__file__).parent / "castmind_ssl_fixed.py"
    with open(wrapper_path, "w", encoding="utf-8") as f:
        f.write(wrapper_content)
    
    # 设置执行权限
    os.chmod(wrapper_path, 0o755)
    
    print(f"✅ 包装脚本创建完成: {wrapper_path}")
    return wrapper_path


def create_patched_castmind():
    """创建修复 SSL 的 CastMind 版本"""
    print("\n🔧 创建修复 SSL 的 CastMind 版本...")
    
    # 读取原始 castmind.py
    original_path = Path(__file__).parent / "castmind.py"
    with open(original_path, "r", encoding="utf-8") as f:
        original_content = f.read()
    
    # 在文件开头添加 SSL 修复代码
    ssl_fix_code = """#!/usr/bin/env python3
\"\"\"
CastMind - 播客智能流系统（SSL 修复版）
临时禁用 SSL 证书验证以解决 RSS 解析问题
\"\"\"

import ssl
# 临时禁用 SSL 验证（仅测试环境）
ssl._create_default_https_context = ssl._create_unverified_context

"""
    
    # 创建修复版本
    patched_content = ssl_fix_code + original_content
    
    patched_path = Path(__file__).parent / "castmind_ssl_patched.py"
    with open(patched_path, "w", encoding="utf-8") as f:
        f.write(patched_content)
    
    # 设置执行权限
    os.chmod(patched_path, 0o755)
    
    print(f"✅ SSL 修复版本创建完成: {patched_path}")
    return patched_path


def test_castmind_with_ssl_fix(patched_script):
    """测试修复 SSL 后的 CastMind"""
    print("\n🧪 测试修复 SSL 后的 CastMind...")
    
    import subprocess
    
    commands = [
        ("查看帮助", [sys.executable, patched_script, "--help"]),
        ("查看状态", [sys.executable, patched_script, "status"]),
    ]
    
    for cmd_name, cmd_args in commands:
        print(f"\n测试: {cmd_name}")
        print(f"命令: {' '.join(cmd_args)}")
        
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"  ✅ 命令执行成功")
                # 显示部分输出
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines[:5]):
                    if line.strip():
                        print(f"    {line[:60]}...")
            else:
                print(f"  ❌ 命令执行失败")
                if result.stderr:
                    print(f"    错误: {result.stderr[:100]}...")
                    
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    return True


def show_usage_instructions(working_rss, patched_script):
    """显示使用说明"""
    print("\n🚀 使用说明")
    print("=" * 60)
    
    print("\n1. 使用修复 SSL 的版本:")
    print(f"   python {patched_script} --help")
    print(f"   python {patched_script} status")
    print(f"   python {patched_script} process --name \"得到\" --limit 1")
    
    print("\n2. 可用的 RSS 链接:")
    if working_rss:
        for name, rss_url in working_rss:
            print(f"   • {name}: {rss_url}")
    else:
        print("   ⚠️  未找到可用的 RSS 链接")
        print("   可能需要检查网络连接或 RSS 链接有效性")
    
    print("\n3. 测试 RSS 解析:")
    print("   python -c \"import feedparser; print(feedparser.parse('https://feeds.fireside.fm/dedao/rss').feed.title)\"")
    
    print("\n4. 永久解决方案:")
    print("   安装正确的 SSL 证书:")
    print("   python3 -m pip install --upgrade certifi")
    print("   或运行: /Applications/Python\\ 3.12/Install\\ Certificates.command")
    
    print("\n5. 注意事项:")
    print("   • 此临时方案仅用于测试环境")
    print("   • 生产环境请安装正确的 SSL 证书")
    print("   • 禁用 SSL 验证可能存在安全风险")
    
    print("\n💡 快速开始:")
    print(f"   cd /Volumes/MxStore/Project/castmind")
    print(f"   python {patched_script} process --name \"得到\" --limit 1 --verbose")


def main():
    """主函数"""
    print("🔧 SSL 证书问题临时修复")
    print("=" * 60)
    print("⚠️  注意：此方案仅用于测试环境")
    print("    生产环境请安装正确的 SSL 证书")
    print("=" * 60)
    
    # 1. 禁用 SSL 验证
    disable_ssl_verification()
    
    # 2. 测试 RSS 解析
    working_rss = test_rss_without_ssl()
    
    # 3. 创建修复版本
    patched_script = create_patched_castmind()
    
    # 4. 测试修复版本
    test_castmind_with_ssl_fix(patched_script)
    
    # 5. 显示使用说明
    show_usage_instructions(working_rss, patched_script)
    
    print("\n" + "=" * 60)
    print("✅ SSL 临时修复完成！")
    print("=" * 60)
    print("\n现在可以使用修复 SSL 的版本运行 CastMind:")
    print(f"python {patched_script} process --name \"得到\" --limit 1")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)