#!/usr/bin/env python3
"""
CastMind OpenAI 快速配置
专门设置 OpenAI API Key 和 URL
"""

import os
import sys
from pathlib import Path


def main():
    print("🧠🌊 CastMind OpenAI 快速配置")
    print("=" * 60)
    
    # 检查 config 目录
    config_dir = Path(__file__).parent / "config"
    if not config_dir.exists():
        print(f"❌ 配置目录不存在: {config_dir}")
        return
    
    # 读取现有的 .env 文件或创建新的
    env_file = config_dir / ".env"
    env_lines = []
    
    if env_file.exists():
        print(f"📁 读取现有配置文件: {env_file}")
        with open(env_file, "r") as f:
            env_lines = f.readlines()
    else:
        print("📝 创建新的配置文件")
        # 从 .env.example 复制基础配置
        example_file = config_dir / ".env.example"
        if example_file.exists():
            with open(example_file, "r") as f:
                env_lines = f.readlines()
    
    # 获取 OpenAI API Key
    print("\n🔑 配置 OpenAI API Key")
    print("-" * 40)
    
    openai_api_key = input("请输入 OpenAI API Key: ").strip()
    if not openai_api_key:
        print("❌ API Key 不能为空")
        return
    
    # 获取 OpenAI Base URL（可选）
    print("\n🌐 配置 OpenAI Base URL（可选）")
    print("-" * 40)
    print("提示: 如果你使用 OpenAI 官方服务，可以留空")
    print("      如果你使用其他兼容 OpenAI API 的服务，请输入 URL")
    print("      例如: https://api.openai.com/v1")
    print("            http://localhost:8080/v1")
    print("            https://api.deepseek.com/v1")
    
    openai_base_url = input("OpenAI Base URL（留空使用默认）: ").strip()
    
    # 更新或添加配置
    updated_lines = []
    openai_key_set = False
    openai_url_set = False
    
    for line in env_lines:
        stripped = line.strip()
        
        if stripped.startswith("OPENAI_API_KEY="):
            updated_lines.append(f"OPENAI_API_KEY={openai_api_key}\n")
            openai_key_set = True
        elif stripped.startswith("OPENAI_BASE_URL=") and openai_base_url:
            updated_lines.append(f"OPENAI_BASE_URL={openai_base_url}\n")
            openai_url_set = True
        elif stripped.startswith("# OPENAI_BASE_URL=") and openai_base_url:
            # 取消注释并设置
            updated_lines.append(f"OPENAI_BASE_URL={openai_base_url}\n")
            openai_url_set = True
        else:
            updated_lines.append(line)
    
    # 如果配置项不存在，添加它们
    if not openai_key_set:
        updated_lines.append(f"OPENAI_API_KEY={openai_api_key}\n")
    
    if openai_base_url and not openai_url_set:
        updated_lines.append(f"OPENAI_BASE_URL={openai_base_url}\n")
    
    # 设置默认 AI 模型为 openai
    default_model_set = False
    for i, line in enumerate(updated_lines):
        if line.strip().startswith("DEFAULT_AI_MODEL="):
            updated_lines[i] = "DEFAULT_AI_MODEL=openai\n"
            default_model_set = True
            break
    
    if not default_model_set:
        # 查找合适的位置插入
        inserted = False
        for i, line in enumerate(updated_lines):
            if "DEFAULT_PODCAST_LIMIT" in line:
                updated_lines.insert(i + 1, "DEFAULT_AI_MODEL=openai\n")
                inserted = True
                break
        
        if not inserted:
            updated_lines.append("DEFAULT_AI_MODEL=openai\n")
    
    # 写入文件
    with open(env_file, "w") as f:
        f.writelines(updated_lines)
    
    print(f"\n✅ 配置文件已更新: {env_file}")
    
    # 显示配置内容
    print("\n📋 当前 OpenAI 配置:")
    print("-" * 40)
    
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if "OPENAI" in line or "DEFAULT_AI_MODEL" in line:
                if line and not line.startswith("#"):
                    print(f"  {line}")
    
    # 创建测试脚本
    test_script = config_dir.parent / "test_openai_config.py"
    with open(test_script, "w") as f:
        f.write(f'''#!/usr/bin/env python3
"""
测试 OpenAI 配置
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config import ConfigManager

def main():
    print("🧪 测试 OpenAI 配置")
    print("=" * 60)
    
    config = ConfigManager("config")
    
    # 获取 OpenAI API Key
    api_key = config.get("OPENAI_API_KEY")
    base_url = config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if not api_key or api_key.startswith("sk-your-"):
        print("❌ OpenAI API Key 未配置或使用默认值")
        return
    
    print(f"✅ OpenAI API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ OpenAI Base URL: {base_url}")
    
    # 测试连接
    print("\\n🧪 测试 OpenAI 连接...")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url if base_url != "https://api.openai.com/v1" else None
        )
        
        # 简单的测试调用
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{{"role": "user", "content": "Hello, test!"}}],
            max_tokens=5
        )
        
        print(f"✅ 连接测试成功")
        print(f"   模型: gpt-3.5-turbo")
        print(f"   响应: {{response.choices[0].message.content}}")
        
    except Exception as e:
        print(f"❌ 连接测试失败: {{e}}")
        print("\\n💡 可能的原因:")
        print("   1. API Key 无效")
        print("   2. 网络连接问题")
        print("   3. Base URL 不正确")
        print("   4. 服务不可用")
        
        if "Incorrect API key" in str(e):
            print("\\n🔑 请检查 API Key 是否正确")
        elif "connect" in str(e).lower():
            print("\\n🌐 请检查网络连接和 Base URL")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n❌ 用户中断")
    except Exception as e:
        print(f"\\n❌ 错误: {{e}}")
''')
    
    print(f"\n📝 已创建测试脚本: {test_script}")
    
    # 显示下一步操作
    print("\n🚀 下一步操作")
    print("=" * 60)
    
    print("\n1. 测试 OpenAI 配置:")
    print(f"   python {test_script}")
    
    print("\n2. 安装 OpenAI Python 包（如果未安装）:")
    print("   pip install openai")
    
    print("\n3. 启动 CastMind:")
    print("   python castmind.py")
    
    print("\n4. 添加播客订阅:")
    print("   python castmind.py add --url <播客RSS链接>")
    
    print("\n5. 处理播客（使用 OpenAI）:")
    print("   python castmind.py process --name <播客名称> --model openai")
    
    print("\n💡 提示:")
    print("   - 确保 OpenAI API Key 有足够的额度")
    print("   - 首次使用建议先测试配置")
    print("   - 可以在 config/ai_models.json 中调整 OpenAI 模型设置")
    
    print("\n" + "=" * 60)
    print("✅ OpenAI 配置完成！")
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