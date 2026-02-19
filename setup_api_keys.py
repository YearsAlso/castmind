#!/usr/bin/env python3
"""
CastMind API Key 配置助手
交互式设置所有需要的 API 密钥
"""

import os
import sys
from pathlib import Path
import json


def print_header():
    """打印标题"""
    print("=" * 60)
    print("🧠🌊 CastMind API Key 配置助手")
    print("=" * 60)
    print()


def get_input(prompt, default="", is_password=False):
    """获取用户输入"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if is_password:
        import getpass
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value.strip() or default


def create_env_file(config_dir):
    """创建 .env 文件"""
    env_file = config_dir / ".env"
    
    print("\n🔧 配置 API 密钥")
    print("-" * 40)
    
    # 读取现有的 .env.example 作为模板
    example_file = config_dir / ".env.example"
    env_content = []
    
    if example_file.exists():
        with open(example_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    env_content.append(line)
                elif "=" in line:
                    key = line.split("=")[0].strip()
                    
                    # 根据键名获取输入
                    if "API_KEY" in key:
                        service = key.replace("_API_KEY", "").replace("_", " ").title()
                        if key == "OPENAI_API_KEY":
                            value = get_input(f"请输入 {service} API Key", is_password=True)
                        else:
                            value = get_input(f"请输入 {service} API Key (可选)", is_password=True)
                        env_content.append(f"{key}={value}")
                    elif key == "DEFAULT_AI_MODEL":
                        value = get_input("默认 AI 模型", "deepseek")
                        env_content.append(f"{key}={value}")
                    elif key == "CASTMIND_ENV":
                        value = get_input("运行环境", "development")
                        env_content.append(f"{key}={value}")
                    elif key == "LOG_LEVEL":
                        value = get_input("日志级别", "INFO")
                        env_content.append(f"{key}={value}")
                    elif key == "DATA_PATH":
                        value = get_input("数据存储路径", "./data")
                        env_content.append(f"{key}={value}")
                    elif key == "DEFAULT_PODCAST_LIMIT":
                        value = get_input("默认处理最新几期播客", "5")
                        env_content.append(f"{key}={value}")
                    else:
                        # 保持默认值
                        env_content.append(line)
    
    # 写入 .env 文件
    with open(env_file, "w") as f:
        f.write("\n".join(env_content))
    
    print(f"\n✅ 已创建配置文件: {env_file}")
    return env_file


def check_api_keys(env_file):
    """检查 API 密钥配置"""
    print("\n🔍 检查 API 密钥配置")
    print("-" * 40)
    
    api_keys = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if "API_KEY" in key and value and value != "your-":
                    api_keys[key] = "✓ 已配置" if value and "your-" not in value else "✗ 未配置"
    
    for key, status in api_keys.items():
        print(f"  {key}: {status}")
    
    # 检查至少一个 AI 服务已配置
    configured = [k for k, v in api_keys.items() if "✓" in v]
    if configured:
        print(f"\n✅ 已配置 {len(configured)} 个 AI 服务")
        return True
    else:
        print("\n⚠️  警告: 未配置任何 AI 服务 API Key")
        print("   至少需要配置一个 AI 服务才能处理播客")
        return False


def test_openai_connection(api_key):
    """测试 OpenAI 连接"""
    print("\n🧪 测试 OpenAI 连接...")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # 简单的测试调用
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI 连接测试成功")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI 连接测试失败: {e}")
        return False


def test_deepseek_connection(api_key):
    """测试 DeepSeek 连接"""
    print("\n🧪 测试 DeepSeek 连接...")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ DeepSeek 连接测试成功")
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek 连接测试失败: {e}")
        return False


def test_configuration(config_dir):
    """测试整体配置"""
    print("\n🧪 测试 CastMind 配置...")
    
    try:
        # 临时添加 config 目录到路径
        sys.path.insert(0, str(config_dir.parent / "src"))
        
        from core.config import ConfigManager
        
        config = ConfigManager(str(config_dir))
        
        # 验证配置
        errors = config.validate_config()
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✅ 配置验证通过")
            
            # 显示配置摘要
            summary = config.get_summary()
            print("\n📋 配置摘要:")
            for key, value in summary.items():
                print(f"  {key}: {value}")
            
            return True
            
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False
    finally:
        # 清理路径
        if str(config_dir.parent / "src") in sys.path:
            sys.path.remove(str(config_dir.parent / "src"))


def show_next_steps(config_dir, has_openai_key, has_deepseek_key):
    """显示下一步操作"""
    print("\n🚀 下一步操作")
    print("=" * 60)
    
    print("\n1. 启动 CastMind:")
    print("   cd /Volumes/MxStore/Project/castmind")
    print("   python castmind.py")
    
    print("\n2. 添加播客订阅:")
    print("   python castmind.py add --url <播客RSS链接>")
    
    print("\n3. 处理播客:")
    print("   python castmind.py process --name <播客名称>")
    
    print("\n4. 查看帮助:")
    print("   python castmind.py --help")
    
    print("\n5. 查看状态:")
    print("   python castmind.py status")
    
    print("\n📝 支持的 AI 服务:")
    if has_openai_key:
        print("   ✅ OpenAI - 转录和总结")
    if has_deepseek_key:
        print("   ✅ DeepSeek - 总结和分析")
    
    print("\n💡 提示:")
    print("   - 确保至少配置了一个 AI 服务的 API Key")
    print("   - 首次使用建议从 DeepSeek 开始（成本较低）")
    print("   - 可以在 config/ai_models.json 中调整模型配置")


def main():
    """主函数"""
    print_header()
    
    # 检查 config 目录
    config_dir = Path(__file__).parent / "config"
    if not config_dir.exists():
        print(f"❌ 配置目录不存在: {config_dir}")
        print("   请确保在 CastMind 项目根目录运行此脚本")
        return
    
    # 检查是否已有 .env 文件
    env_file = config_dir / ".env"
    if env_file.exists():
        print(f"⚠️  已存在配置文件: {env_file}")
        overwrite = get_input("是否覆盖？(y/N)", "n").lower()
        if overwrite != "y":
            print("使用现有配置文件")
        else:
            env_file = create_env_file(config_dir)
    else:
        env_file = create_env_file(config_dir)
    
    # 检查 API 密钥
    if not check_api_keys(env_file):
        print("\n⚠️  请至少配置一个 AI 服务的 API Key")
        reconfigure = get_input("是否重新配置？(y/N)", "n").lower()
        if reconfigure == "y":
            env_file = create_env_file(config_dir)
            check_api_keys(env_file)
    
    # 读取 API 密钥进行测试
    api_keys = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if "API_KEY" in key and value and "your-" not in value:
                    api_keys[key] = value
    
    # 测试连接（可选）
    print("\n🧪 可选: 测试 API 连接")
    print("-" * 40)
    
    test_connections = get_input("是否测试 API 连接？(y/N)", "n").lower()
    
    has_openai_key = False
    has_deepseek_key = False
    
    if test_connections == "y":
        # 安装必要的包
        print("安装依赖包...")
        os.system("pip install openai > /dev/null 2>&1")
        
        if "OPENAI_API_KEY" in api_keys:
            has_openai_key = test_openai_connection(api_keys["OPENAI_API_KEY"])
        
        if "DEEPSEEK_API_KEY" in api_keys:
            has_deepseek_key = test_deepseek_connection(api_keys["DEEPSEEK_API_KEY"])
    
    # 测试整体配置
    test_configuration(config_dir)
    
    # 显示下一步操作
    show_next_steps(config_dir, "OPENAI_API_KEY" in api_keys, "DEEPSEEK_API_KEY" in api_keys)
    
    print("\n" + "=" * 60)
    print("✅ API Key 配置完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)