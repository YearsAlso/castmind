#!/usr/bin/env python3
"""
测试 DeepSeek 可用的模型
"""

from openai import OpenAI
import os
from pathlib import Path

# 加载配置
env_file = Path(__file__).parent / "config" / ".env"
config = {}
with open(env_file, "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

api_key = config.get("OPENAI_API_KEY")
base_url = config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

print("🔍 测试 DeepSeek 模型")
print("=" * 60)
print(f"Base URL: {base_url}")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 测试不同的模型名称
test_models = [
    "deepseek-chat",
    "deepseek-coder",
    "gpt-3.5-turbo",
    "gpt-4",
    "text-davinci-003",
]

for model in test_models:
    print(f"\n测试模型: {model}")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个测试助手"},
                {"role": "user", "content": "请回复'测试成功'"}
            ],
            max_tokens=10,
            timeout=5
        )
        
        if response.choices and response.choices[0].message.content:
            print(f"  ✅ 模型可用: {response.choices[0].message.content}")
        else:
            print(f"  ❌ 模型响应异常")
            
    except Exception as e:
        print(f"  ❌ 模型不可用: {e}")

print("\n" + "=" * 60)
print("💡 DeepSeek 模型参考:")
print("   官方文档: https://platform.deepseek.com/api-docs/")
print("   常用模型: deepseek-chat, deepseek-coder")
print("   注意: DeepSeek 不支持 OpenAI 的所有模型")