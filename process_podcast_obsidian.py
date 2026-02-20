#!/usr/bin/env python3
"""
支持 Obsidian 输出的播客处理脚本
"""

import ssl
import sys
import os
import json
import sqlite3
import feedparser
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("🎧 CastMind - Obsidian 集成版")
print("=" * 60)

# 加载配置
def load_config():
    """加载 Obsidian 输出配置"""
    config_file = Path(__file__).parent / "config" / "obsidian_output.json"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        print("请先运行: python config_obsidian_output.py")
        return None
    
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    return config

def get_output_dirs(config):
    """获取输出目录"""
    output_mode = config.get("output_mode", "both")
    
    dirs = {}
    
    if output_mode in ["obsidian", "both"]:
        obsidian_base = Path(config["obsidian_podcasts_dir"])
        folder_structure = config["obsidian_folder_structure"]
        
        dirs["obsidian"] = {
            "transcripts": obsidian_base / folder_structure["transcripts"],
            "summaries": obsidian_base / folder_structure["summaries"],
            "notes": obsidian_base / folder_structure["notes"],
            "metadata": obsidian_base / folder_structure["metadata"]
        }
        
        # 创建目录
        for dir_path in dirs["obsidian"].values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    if output_mode in ["local", "both"]:
        local_base = Path(config["local_data_dir"])
        
        dirs["local"] = {
            "transcripts": local_base / "transcripts",
            "summaries": local_base / "summaries", 
            "notes": local_base / "notes",
            "logs": local_base / "logs"
        }
        
        # 创建目录
        for dir_path in dirs["local"].values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs

def load_ai_config():
    """加载 AI 配置"""
    env_file = Path(__file__).parent / "config" / ".env"
    
    if not env_file.exists():
        print(f"❌ 环境配置文件不存在: {env_file}")
        return None
    
    config = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    
    return config

def get_podcast_info(name):
    """从数据库获取播客信息"""
    db_path = Path(__file__).parent / "data" / "castmind.db"
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, rss_url, category, tags FROM podcasts WHERE name = ?", (name,))
    podcast = cursor.fetchone()
    
    conn.close()
    
    if not podcast:
        print(f"❌ 未找到播客: {name}")
        return None
    
    return {
        "name": podcast[0],
        "rss_url": podcast[1],
        "category": podcast[2],
        "tags": podcast[3]
    }

def parse_rss_feed(rss_url):
    """解析 RSS feed"""
    print(f"\n📡 解析 RSS feed...")
    print(f"URL: {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"❌ RSS 解析错误: {feed.bozo_exception}")
            return None
        
        if not feed.entries:
            print("❌ 没有找到播客条目")
            return None
        
        print(f"✅ RSS 解析成功")
        print(f"   标题: {feed.feed.get('title', '无标题')}")
        print(f"   描述: {feed.feed.get('description', '无描述')[:100]}...")
        print(f"   条目数: {len(feed.entries)}")
        
        # 获取最新一期
        latest_entry = feed.entries[0]
        print(f"\n🎵 最新一期:")
        print(f"   标题: {latest_entry.title}")
        print(f"   发布时间: {latest_entry.get('published', '未知')}")
        
        return feed
        
    except Exception as e:
        print(f"❌ RSS 解析异常: {e}")
        return None

def simulate_transcription(audio_info, output_dirs):
    """模拟音频转录"""
    print(f"\n🎤 模拟音频转录...")
    
    transcript = f"""
播客标题: {audio_info['title']}
发布时间: {audio_info['published']}
处理时间: {datetime.now().isoformat()}

转录内容:
{audio_info['description']}

这是模拟的转录内容。在实际使用中，这里会是真实的音频转录文本。
转录过程包括:
1. 音频下载和预处理
2. Whisper API 调用
3. 文本清理和分段
4. 时间戳生成

模拟信息:
- 语言: 英语
- 置信度: 高
- 分段数: 5
- 总字数: {len(audio_info['description'])}
"""
    
    # 保存转录文件
    files_saved = []
    
    # 创建安全的文件名
    safe_title = "".join(c for c in audio_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title[:50]  # 限制长度
    
    filename = f"{safe_title}_transcript.txt"
    
    # 保存到各个输出目录
    for output_type, dirs in output_dirs.items():
        if "transcripts" in dirs:
            transcript_file = dirs["transcripts"] / filename
            
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript)
            
            files_saved.append((output_type, str(transcript_file)))
    
    print(f"✅ 转录完成")
    for output_type, filepath in files_saved:
        print(f"   保存到 {output_type}: {filepath}")
    
    return transcript, files_saved

def generate_ai_summary(ai_config, transcript, output_dirs):
    """使用 AI 生成总结"""
    print(f"\n🤖 使用 AI 生成总结...")
    
    api_key = ai_config.get("OPENAI_API_KEY")
    base_url = ai_config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = ai_config.get("DEFAULT_AI_MODEL", "deepseek-chat")
    
    if not api_key:
        print("❌ 未找到 API Key 配置")
        return None, []
    
    print(f"   使用 {model} 模型")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 准备提示词
        prompt = f"""
请总结以下播客内容：

{transcript[:1500]}...

请提供:
1. 3-5个关键观点
2. 主要内容摘要
3. 听众可能感兴趣的点
4. 使用中文回复
"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的播客内容总结助手"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        if response.choices and response.choices[0].message.content:
            summary = response.choices[0].message.content
            
            # 保存总结文件
            files_saved = []
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_summary.md"
            
            # 保存到各个输出目录
            for output_type, dirs in output_dirs.items():
                if "summaries" in dirs:
                    summary_file = dirs["summaries"] / filename
                    
                    with open(summary_file, "w", encoding="utf-8") as f:
                        f.write(summary)
                    
                    files_saved.append((output_type, str(summary_file)))
            
            print(f"✅ AI 总结生成成功")
            for output_type, filepath in files_saved:
                print(f"   保存到 {output_type}: {filepath}")
            
            # 显示部分内容
            print(f"\n   生成的总结（前200字）:")
            print(f"   {'='*50}")
            print(f"   {summary[:200]}...")
            print(f"   {'='*50}")
            
            return summary, files_saved
        else:
            print("❌ AI 总结生成失败")
            return None, []
            
    except Exception as e:
        print(f"❌ AI 总结失败: {e}")
        return None, []

def generate_note(podcast_info, audio_info, transcript, summary, output_dirs, config):
    """生成结构化笔记"""
    print(f"\n📝 生成结构化笔记...")
    
    # 获取 Obsidian 标签
    obsidian_tags = config.get("obsidian_tags", ["#播客", "#AI总结"])
    
    note_content = f"""# {audio_info['title']}

## 基本信息
- **播客名称**: {podcast_info['name']}
- **分类**: {podcast_info['category']}
- **标签**: {podcast_info['tags']}
- **发布时间**: {audio_info['published']}
- **处理时间**: {datetime.now().isoformat()}

## AI 总结
{summary}

## 关键内容
{transcript[:500]}...

## 标签
{podcast_info['tags']}
{', '.join(obsidian_tags)}

---
*本笔记由 CastMind 自动生成*
*处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存笔记文件
    files_saved = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 创建安全的文件名
    safe_title = "".join(c for c in audio_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title[:50]  # 限制长度
    
    filename = f"{timestamp}_{safe_title}.md"
    
    # 保存到各个输出目录
    for output_type, dirs in output_dirs.items():
        if "notes" in dirs:
            note_file = dirs["notes"] / filename
            
            with open(note_file, "w", encoding="utf-8") as f:
                f.write(note_content)
            
            files_saved.append((output_type, str(note_file)))
    
    print(f"✅ 笔记生成完成")
    for output_type, filepath in files_saved:
        print(f"   保存到 {output_type}: {filepath}")
    
    return files_saved

def update_processing_log(podcast_name, status, files, output_dirs):
    """更新处理日志"""
    print(f"\n📊 更新处理日志...")
    
    log_entry = f"""
处理记录:
- 播客: {podcast_name}
- 时间: {datetime.now().isoformat()}
- 状态: {status}
- 生成文件:
"""
    
    for file_type, filepath in files:
        log_entry += f"  • {file_type}: {filepath}\n"
    
    # 保存日志
    files_saved = []
    
    for output_type, dirs in output_dirs.items():
        if "logs" in dirs or "metadata" in dirs:
            log_dir = dirs.get("logs", dirs.get("metadata"))
            if log_dir:
                log_file = log_dir / f"castmind_{datetime.now().strftime('%Y%m%d')}.log"
                
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                
                files_saved.append((output_type, str(log_file)))
    
    print(f"✅ 日志保存完成")
    for output_type, filepath in files_saved:
        print(f"   保存到 {output_type}: {filepath}")
    
    return files_saved

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python process_podcast_obsidian.py <播客名称> [限制数量]")
        print("示例: python process_podcast_obsidian.py \"知行小酒馆\" 1")
        return
    
    podcast_name = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    print(f"开始处理: {podcast_name}")
    print(f"处理数量: 最新 {limit} 期")
    print("=" * 60)
    
    # 1. 加载配置
    config = load_config()
    if not config:
        return
    
    output_dirs = get_output_dirs(config)
    if not output_dirs:
        print("❌ 无法获取输出目录")
        return
    
    print(f"\n📁 输出目录配置:")
    for output_type, dirs in output_dirs.items():
        print(f"  {output_type}:")
        for dir_name, dir_path in dirs.items():
            print(f"    {dir_name}: {dir_path}")
    
    # 2. 加载 AI 配置
    ai_config = load_ai_config()
    if not ai_config:
        return
    
    # 3. 获取播客信息
    podcast_info = get_podcast_info(podcast_name)
    if not podcast_info:
        return
    
    # 4. 解析 RSS
    feed = parse_rss_feed(podcast_info["rss_url"])
    if not feed:
        return
    
    # 处理指定数量的最新期数
    all_files = []
    
    for i in range(min(limit, len(feed.entries))):
        print(f"\n{'='*60}")
        print(f"处理第 {i+1}/{min(limit, len(feed.entries))} 期")
        print(f"{'='*60}")
        
        entry = feed.entries[i]
        
        # 准备音频信息
        audio_info = {
            "title": entry.title,
            "published": entry.get("published", datetime.now().isoformat()),
            "description": entry.get("description", entry.get("summary", "")),
        }
        
        # 5. 模拟转录
        transcript, transcript_files = simulate_transcription(audio_info, output_dirs)
        all_files.extend([("transcript", f) for _, f in transcript_files])
        
        # 6. AI 总结
        summary, summary_files = generate_ai_summary(ai_config, transcript, output_dirs)
        
        if not summary:
            print("⚠️  AI 总结失败，使用模拟总结继续")
            summary = "这是模拟的 AI 总结内容。在实际使用中，这里会是真实的 AI 生成总结。"
        else:
            all_files.extend([("summary", f) for _, f in summary_files])
        
        # 7. 生成笔记
        note_files = generate_note(podcast_info, audio_info, transcript, summary, output_dirs, config)
        all_files.extend([("note", f) for _, f in note_files])
        
        # 8. 更新日志
        log_files = update_processing_log(podcast_name, "完成", all_files[-3:], output_dirs)
        all_files.extend([("log", f) for _, f in log_files])
    
    print(f"\n{'='*60}")
    print(f"✅ 处理完成！共处理 {min(limit, len(feed.entries))} 期播客")
    print(f"{'='*60}")
    
    print(f"\n📁 生成的文件位置:")
    for file_type, filepath in all_files:
        print(f"  • {file_type}: {filepath}")
    
    print(f"\n🚀 下一步:")
    print(f"   1. 在 Obsidian 中打开: {config['obsidian_podcasts_dir']}")
    print(f"   2. 查看生成的笔记")
    print(f"   3. 使用 Obsidian 的链接和搜索功能")
    
    print(f"\n💡 Obsidian 使用提示:")
    print(f"   • 使用 [[链接]] 语法链接相关笔记")
    print(f"   • 使用 #标签 进行分类")
    print(f"   • 使用图谱视图查看知识关联")
    print(f"   • 使用搜索快速找到相关内容")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)