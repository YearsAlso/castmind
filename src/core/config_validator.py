#!/usr/bin/env python3
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
                report.append("环境变量问题: ")
                for error in result["environment_errors"]:
                    report.append(f"  - {error}")

                if result["config_errors"]:
                    report.append("配置文件问题: ")
                for error in result["config_errors"]:
                    report.append(f"  - {error}")

                if result["data_errors"]:
                    report.append("数据目录问题: ")
                for error in result["data_errors"]:
                    report.append(f"  - {error}")

                report.append("" + " = " * 60)
        return "".join(report)

if __name__ == "__main__":
    validator = ConfigValidator()
    report = validator.get_validation_report()
    print(report)

    result = validator.validate_all()
    if not result["valid"]:
        exit(1)
