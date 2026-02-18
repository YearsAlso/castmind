#!/usr/bin/env python3
"""
CastMind - 配置管理模块
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config_cache = {}
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self._load_environment()
        self._load_ai_models()
        self._load_workflows()
    
    def _load_environment(self) -> None:
        """加载环境变量"""
        env_file = self.config_dir / ".env"
        
        if env_file.exists():
            # 简单的.env文件解析
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # 移除引号
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            os.environ.setdefault(key, value)
            
            print("✅ 从 .env 文件加载环境变量")
        else:
            print("⚠️  环境配置文件不存在: .env")
            print("   请创建: cp .env.example .env")
    
    def _load_ai_models(self) -> None:
        """加载AI模型配置"""
        ai_models_file = self.config_dir / "ai_models.json"
        
        if ai_models_file.exists():
            with open(ai_models_file, "r", encoding="utf-8") as f:
                self._config_cache["ai_models"] = json.load(f)
            print("✅ 加载AI模型配置")
        else:
            print("⚠️  AI模型配置文件不存在: ai_models.json")
            self._config_cache["ai_models"] = {}
    
    def _load_workflows(self) -> None:
        """加载工作流配置"""
        workflows_file = self.config_dir / "workflows.json"
        
        if workflows_file.exists():
            with open(workflows_file, "r", encoding="utf-8") as f:
                self._config_cache["workflows"] = json.load(f)
            print("✅ 加载工作流配置")
        else:
            print("⚠️  工作流配置文件不存在: workflows.json")
            self._config_cache["workflows"] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 首先检查环境变量
        env_value = os.environ.get(key)
        if env_value is not None:
            return env_value
        
        # 然后检查缓存配置
        keys = key.split(".")
        value = self._config_cache
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_ai_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取AI模型配置"""
        models = self.get("ai_models.models", {})
        return models.get(model_id)
    
    def get_workflow_config(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流配置"""
        workflows = self.get("workflows.workflows", {})
        return workflows.get(workflow_id)
    
    def get_default_workflow(self) -> str:
        """获取默认工作流"""
        return self.get("workflows.default_workflow", "basic_processing")
    
    def get_scheduled_workflows(self) -> Dict[str, Any]:
        """获取计划任务配置"""
        return self.get("workflows.scheduling", {})
    
    def validate_config(self) -> list:
        """验证配置"""
        errors = []
        
        # 检查必要的环境变量
        required_env_vars = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "KIMI_API_KEY"]
        for var in required_env_vars:
            if not os.environ.get(var):
                errors.append(f"缺少必要的环境变量: {var}")
        
        # 检查配置文件
        required_files = [".env", "ai_models.json", "workflows.json"]
        for file in required_files:
            if not (self.config_dir / file).exists():
                errors.append(f"缺少配置文件: {file}")
        
        # 检查数据目录
        data_dir = Path(self.get("DATA_PATH", "data"))
        if not data_dir.exists():
            try:
                data_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建数据目录: {e}")
        
        return errors
    
    def get_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "environment": self.get("CASTMIND_ENV", "development"),
            "log_level": self.get("LOG_LEVEL", "INFO"),
            "data_path": self.get("DATA_PATH", "data"),
            "default_ai_model": self.get("DEFAULT_AI_MODEL", "deepseek"),
            "default_podcast_limit": int(self.get("DEFAULT_PODCAST_LIMIT", 5)),
            "auto_process_interval": int(self.get("AUTO_PROCESS_INTERVAL", 3600)),
            "ai_models_count": len(self.get("ai_models.models", {})),
            "workflows_count": len(self.get("workflows.workflows", {})),
            "scheduled_tasks": len(self.get("workflows.scheduling", {})),
        }


# 全局配置实例
config = ConfigManager()


if __name__ == "__main__":
    # 测试配置
    print("🧪 配置管理器测试")
    print("=" * 60)
    
    # 验证配置
    errors = config.validate_config()
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 配置验证通过")
    
    # 显示配置摘要
    summary = config.get_summary()
    print("\n📋 配置摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # 显示AI模型
    print("\n🧠 AI模型配置:")
    models = config.get("ai_models.models", {})
    for model_id, model_config in models.items():
        enabled = "✅" if model_config.get("enabled", False) else "❌"
        print(f"  {enabled} {model_id}: {model_config.get('name', '未知')}")
    
    # 显示工作流
    print("\n🌊 工作流配置:")
    workflows = config.get("workflows.workflows", {})
    for workflow_id, workflow_config in workflows.items():
        print(f"  📋 {workflow_id}: {workflow_config.get('name', '未知')}")