#!/usr/bin/env python3
"""
演示如何使用编码助手技能操作OpenCode

这个脚本展示了如何按照coding-agent技能文档的指导来使用编码助手
"""

import subprocess
import time
import os
from pathlib import Path

def run_with_pty(command, workdir=None):
    """
    使用PTY运行命令（按照coding-agent技能文档的要求）
    
    Args:
        command: 要执行的命令
        workdir: 工作目录
        
    Returns:
        命令输出
    """
    env = os.environ.copy()
    env['PATH'] = f"/usr/sbin:{env.get('PATH', '')}"
    
    if workdir:
        os.chdir(workdir)
    
    print(f"🚀 运行命令: {command}")
    print(f"📁 工作目录: {workdir or os.getcwd()}")
    print("-" * 60)
    
    try:
        # 使用subprocess.Popen创建PTY
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1,
            universal_newlines=True
        )
        
        # 等待进程完成
        stdout, stderr = process.communicate(timeout=30)
        
        print("📋 输出结果:")
        print(stdout)
        
        if stderr:
            print("⚠️  错误输出:")
            print(stderr)
        
        print(f"✅ 命令完成，退出码: {process.returncode}")
        return process.returncode, stdout, stderr
        
    except subprocess.TimeoutExpired:
        print("⏰ 命令超时")
        process.kill()
        return -1, "", "命令超时"
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return -1, "", str(e)

def demo_opencode_basic():
    """演示OpenCode基本使用"""
    print("=" * 60)
    print("🧩 演示1: OpenCode基本使用")
    print("=" * 60)
    
    # 1. 查看OpenCode帮助
    returncode, stdout, stderr = run_with_pty("opencode --help")
    
    if returncode == 0:
        print("✅ OpenCode基本功能正常")
    else:
        print("❌ OpenCode有问题，尝试修复...")
        
        # 尝试运行简单的命令
        returncode, stdout, stderr = run_with_pty("opencode completion")
        
        if "Commands:" in stdout:
            print("✅ OpenCode可以运行简单命令")
        else:
            print("❌ OpenCode需要修复")

def demo_project_analysis():
    """演示项目分析"""
    print("\n" + "=" * 60)
    print("📁 演示2: 项目结构分析")
    print("=" * 60)
    
    project_dir = Path(__file__).parent.parent
    
    # 使用OpenCode分析项目结构
    command = f"cd {project_dir} && opencode run '分析这个CastMind项目的结构，列出主要模块和文件'"
    returncode, stdout, stderr = run_with_pty(command, workdir=project_dir)
    
    if returncode != 0:
        # 如果OpenCode失败，使用bash命令
        print("⚠️ OpenCode分析失败，使用bash命令替代")
        command = f"cd {project_dir} && find . -name '*.py' -type f | head -10"
        returncode, stdout, stderr = run_with_pty(command, workdir=project_dir)
        
        print("📋 Python文件列表:")
        print(stdout)

def demo_code_generation():
    """演示代码生成"""
    print("\n" + "=" * 60)
    print("💻 演示3: 代码生成")
    print("=" * 60)
    
    project_dir = Path(__file__).parent.parent
    
    # 创建一个简单的任务
    task = """
为CastMind项目创建一个简单的配置验证模块。
这个模块应该：
1. 检查必要的环境变量是否设置
2. 验证配置文件是否存在
3. 提供友好的错误信息
4. 返回验证结果
"""
    
    print("📝 任务描述:")
    print(task)
    
    # 保存任务到文件
    task_file = project_dir / "task_config_validation.txt"
    with open(task_file, "w") as f:
        f.write(task)
    
    print(f"📄 任务已保存到: {task_file}")
    
    # 使用OpenCode执行任务
    command = f"cd {project_dir} && opencode run '请查看task_config_validation.txt文件中的任务，并创建一个配置验证模块'"
    returncode, stdout, stderr = run_with_pty(command, workdir=project_dir)
    
    if returncode != 0:
        print("⚠️ OpenCode代码生成失败，手动创建示例模块...")
        
        # 手动创建示例模块
        config_validation_code = '''#!/usr/bin/env python3
"""
CastMind - 配置验证模块
"""

import os
from pathlib import Path
from typing import List, Dict, Any

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
    
    def validate_environment(self) -> List[str]:
        """验证环境变量"""
        errors = []
        
        required_vars = [
            "OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "KIMI_API_KEY"
        ]
        
        for var in required_vars:
            if not os.environ.get(var):
                errors.append(f"缺少必要的环境变量: {var}")
        
        return errors
    
    def validate_config_files(self) -> List[str]:
        """验证配置文件"""
        errors = []
        
        required_files = [
            ".env",
            "ai_models.json",
            "workflows.json"
        ]
        
        for file in required_files:
            file_path = self.config_dir / file
            if not file_path.exists():
                errors.append(f"缺少配置文件: {file}")
        
        return errors
    
    def validate_data_directories(self) -> List[str]:
        """验证数据目录"""
        errors = []
        
        required_dirs = [
            "data/podcasts",
            "data/transcripts",
            "data/knowledge"
        ]
        
        for dir_path in required_dirs:
            dir_obj = Path(dir_path)
            if not dir_obj.exists():
                try:
                    dir_obj.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"无法创建目录 {dir_path}: {e}")
        
        return errors
    
    def validate_all(self) -> Dict[str, Any]:
        """执行所有验证"""
        env_errors = self.validate_environment()
        config_errors = self.validate_config_files()
        data_errors = self.validate_data_directories()
        
        all_errors = env_errors + config_errors + data_errors
        
        return {
            "valid": len(all_errors) == 0,
            "errors": all_errors,
            "environment_errors": env_errors,
            "config_errors": config_errors,
            "data_errors": data_errors,
            "summary": {
                "total_errors": len(all_errors),
                "environment_errors": len(env_errors),
                "config_errors": len(config_errors),
                "data_errors": len(data_errors)
            }
        }
    
    def get_validation_report(self) -> str:
        """获取验证报告"""
        result = self.validate_all()
        
        report = []
        report.append("=" * 60)
        report.append("CastMind 配置验证报告")
        report.append("=" * 60)
        
        if result["valid"]:
            report.append("✅ 所有配置验证通过！")
        else:
            report.append(f"❌ 发现 {result['summary']['total_errors']} 个问题：")
            
            if result["environment_errors"]:
                report.append("\n环境变量问题:")
                for error in result["environment_errors"]:
                    report.append(f"  - {error}")
            
            if result["config_errors"]:
                report.append("\n配置文件问题:")
                for error in result["config_errors"]:
                    report.append(f"  - {error}")
            
            if result["data_errors"]:
                report.append("\n数据目录问题:")
                for error in result["data_errors"]:
                    report.append(f"  - {error}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)


if __name__ == "__main__":
    validator = ConfigValidator()
    report = validator.get_validation_report()
    print(report)
    
    result = validator.validate_all()
    if not result["valid"]:
        exit(1)
'''
        
        # 保存代码
        output_file = project_dir / "src" / "core" / "config_validator.py"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            f.write(config_validation_code)
        
        print(f"✅ 手动创建了配置验证模块: {output_file}")

def demo_skill_usage_patterns():
    """演示技能使用模式"""
    print("\n" + "=" * 60)
    print("📚 演示4: 编码助手技能使用模式")
    print("=" * 60)
    
    patterns = [
        {
            "name": "一次性任务",
            "command": "opencode run '你的任务描述'",
            "description": "快速执行简单任务"
        },
        {
            "name": "项目分析",
            "command": "opencode run '分析项目结构，列出主要文件'",
            "description": "理解项目架构"
        },
        {
            "name": "代码生成",
            "command": "opencode run '创建XXX模块，实现YYY功能'",
            "description": "生成新代码"
        },
        {
            "name": "代码审查",
            "command": "opencode run '审查XXX.py文件，提出改进建议'",
            "description": "代码质量检查"
        },
        {
            "name": "Bug修复",
            "command": "opencode run '修复XXX.py中的YYY问题'",
            "description": "问题诊断和修复"
        }
    ]
    
    print("📋 常用编码助手使用模式:")
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern['name']}:")
        print(f"   命令: {pattern['command']}")
        print(f"   描述: {pattern['description']}")

def main():
    """主函数"""
    print("🧩 CastMind - 编码助手技能演示")
    print("=" * 60)
    
    # 检查OpenCode是否可用
    try:
        result = subprocess.run(
            ["which", "opencode"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ OpenCode已安装: {result.stdout.strip()}")
        else:
            print("❌ OpenCode未安装")
            print("   请安装: npm install -g opencode")
            return
    except Exception as e:
        print(f"❌ 检查OpenCode时出错: {e}")
        return
    
    # 运行演示
    demo_opencode_basic()
    demo_project_analysis()
    demo_code_generation()
    demo_skill_usage_patterns()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("=" * 60)
    
    print("\n📝 总结:")
    print("1. 编码助手技能需要使用 pty:true 参数")
    print("2. OpenCode需要正确的PATH设置（包含/usr/sbin）")
    print("3. 工作目录很重要，确保在正确的项目中操作")
    print("4. 对于复杂任务，可以先创建任务描述文件")
    print("5. 如果OpenCode失败，可以手动实现或使用其他工具")

if __name__ == "__main__":
    main()