#!/usr/bin/env python3
"""
配置 CastMind 输出到 Obsidian 仓库
"""

import os
from pathlib import Path
import json

print("🎯 配置 CastMind 输出到 Obsidian 仓库")
print("=" * 60)

# Obsidian 仓库路径
OBSIDIAN_VAULT = "/Volumes/MxStore/Project/YearsAlso"
OBSIDIAN_PODCASTS_DIR = f"{OBSIDIAN_VAULT}/Podcasts/CastMind"

# 创建配置目录
config_dir = Path(__file__).parent / "config"
config_dir.mkdir(exist_ok=True)

# 配置选项
config_options = {
    "output_mode": "obsidian",  # obsidian | local | both
    "obsidian_vault": OBSIDIAN_VAULT,
    "obsidian_podcasts_dir": OBSIDIAN_PODCASTS_DIR,
    "local_data_dir": "/Volumes/MxStore/Project/castmind/data",
    "create_obsidian_structure": True,
    "sync_method": "direct",  # direct | symlink | copy
    "obsidian_tags": ["#播客", "#AI总结", "#CastMind生成"],
    "obsidian_folder_structure": {
        "transcripts": "transcripts",
        "summaries": "summaries", 
        "notes": "notes",
        "metadata": "metadata"
    }
}

print("📁 Obsidian 仓库配置:")
print(f"   仓库路径: {OBSIDIAN_VAULT}")
print(f"   播客目录: {OBSIDIAN_PODCASTS_DIR}")

# 检查 Obsidian 仓库是否存在
if Path(OBSIDIAN_VAULT).exists():
    print("✅ Obsidian 仓库存在")
    
    # 创建目录结构
    if config_options["create_obsidian_structure"]:
        print("\n📂 创建 Obsidian 目录结构...")
        
        for folder_name, folder_path in config_options["obsidian_folder_structure"].items():
            full_path = Path(OBSIDIAN_PODCASTS_DIR) / folder_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   创建: {full_path}")
        
        # 创建 Obsidian 配置文件
        obsidian_config = {
            "folders": [
                {
                    "path": "Podcasts/CastMind/transcripts",
                    "name": "播客转录",
                    "color": "#4CAF50"
                },
                {
                    "path": "Podcasts/CastMind/summaries", 
                    "name": "AI总结",
                    "color": "#2196F3"
                },
                {
                    "path": "Podcasts/CastMind/notes",
                    "name": "结构化笔记",
                    "color": "#FF9800"
                }
            ],
            "tags": config_options["obsidian_tags"],
            "settings": {
                "autoUpdateLinks": True,
                "newFileLocation": "folder",
                "newFileFolderPath": "Podcasts/CastMind/notes",
                "defaultViewMode": "preview"
            }
        }
        
        config_file = Path(OBSIDIAN_PODCASTS_DIR) / ".obsidian" / "castmind.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(obsidian_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建 Obsidian 配置文件: {config_file}")
        
else:
    print("❌ Obsidian 仓库不存在，使用本地目录")

# 保存配置
config_file = config_dir / "obsidian_output.json"
with open(config_file, "w", encoding="utf-8") as f:
    json.dump(config_options, f, indent=2, ensure_ascii=False)

print(f"\n✅ 配置已保存到: {config_file}")

print(f"\n🚀 使用配置:")
print(f"   输出模式: {config_options['output_mode']}")
print(f"   Obsidian目录: {config_options['obsidian_podcasts_dir']}")
print(f"   本地目录: {config_options['local_data_dir']}")
print(f"   同步方法: {config_options['sync_method']}")

print(f"\n📝 下一步操作:")
print(f"   1. 修改 real_process_podcast.py 使用此配置")
print(f"   2. 测试输出到 Obsidian")
print(f"   3. 在 Obsidian 中查看生成的文件")

print(f"\n💡 在 Obsidian 中的优势:")
print(f"   • 直接查看和管理生成的笔记")
print(f"   • 使用 Obsidian 的链接和搜索功能")
print(f"   • 与现有知识库集成")
print(f"   • 支持双向链接和图谱视图")