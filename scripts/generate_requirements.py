#!/usr/bin/env python3
"""
从 pyproject.toml 生成 requirements.txt 文件
"""

import tomli
from pathlib import Path

def generate_requirements():
    """生成 requirements.txt 文件"""
    # 读取 pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        data = tomli.load(f)
    
    # 生成 requirements.txt
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    with open(requirements_path, "w") as f:
        f.write("# 从 pyproject.toml 自动生成\n")
        f.write("# 使用 'uv sync' 或 'pip install -r requirements.txt' 安装依赖\n\n")
        
        if "project" in data and "dependencies" in data["project"]:
            for dep in data["project"]["dependencies"]:
                f.write(f"{dep}\n")
    
    print(f"✅ 已生成: {requirements_path}")
    
    # 生成 requirements-dev.txt
    requirements_dev_path = Path(__file__).parent.parent / "requirements-dev.txt"
    with open(requirements_dev_path, "w") as f:
        f.write("# 从 pyproject.toml 自动生成 - 开发依赖\n")
        f.write("# 使用 'uv sync --dev' 或 'pip install -r requirements-dev.txt' 安装\n\n")
        
        # 包含所有依赖
        if "project" in data and "dependencies" in data["project"]:
            for dep in data["project"]["dependencies"]:
                f.write(f"{dep}\n")
        
        # 添加开发依赖
        if "project" in data and "optional-dependencies" in data["project"]:
            if "dev" in data["project"]["optional-dependencies"]:
                f.write("\n# 开发依赖\n")
                for dep in data["project"]["optional-dependencies"]["dev"]:
                    f.write(f"{dep}\n")
    
    print(f"✅ 已生成: {requirements_dev_path}")
    
    # 生成 requirements-docs.txt
    requirements_docs_path = Path(__file__).parent.parent / "requirements-docs.txt"
    with open(requirements_docs_path, "w") as f:
        f.write("# 从 pyproject.toml 自动生成 - 文档依赖\n")
        f.write("# 使用 'uv pip install -r requirements-docs.txt' 安装\n\n")
        
        if "project" in data and "optional-dependencies" in data["project"]:
            if "docs" in data["project"]["optional-dependencies"]:
                for dep in data["project"]["optional-dependencies"]["docs"]:
                    f.write(f"{dep}\n")
    
    print(f"✅ 已生成: {requirements_docs_path}")

if __name__ == "__main__":
    generate_requirements()