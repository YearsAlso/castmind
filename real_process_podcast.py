#!/usr/bin/env python3
"""
实际处理播客的脚本
实现完整的 RSS 解析、AI 处理、笔记生成流程
"""

import ssl
import sys
import os
import sqlite3
import feedparser
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# 禁用 SSL 验证（临时方案）
ssl._create_default_https_context = ssl._create_unverified_context

print("🎧 CastMind 实际播客处理")
print("=" * 60)


def load_config():
    """加载配置"""
    env_file = Path(__file__).parent / "config" / ".env"
    if not env_file.exists():
        print(f"❌ 配置文件不存在: {env_file}")
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


def simulate_audio_download(entry):
    """模拟音频下载（实际中会下载音频文件）"""
    print(f"\n📥 模拟音频下载...")
    
    # 在实际应用中，这里会下载音频文件
    # 现在我们先模拟
    
    audio_info = {
        "title": entry.title,
        "published": entry.get("published", datetime.now().isoformat()),
        "description": entry.get("description", entry.get("summary", "")),
        "audio_url": "",
        "duration": "30:00"
    }
    
    # 尝试获取音频链接
    enclosures = entry.get("enclosures", [])
    if enclosures:
        audio_info["audio_url"] = enclosures[0].get("href", "")
    
    print(f"   标题: {audio_info['title'][:50]}...")
    print(f"   发布时间: {audio_info['published']}")
    print(f"   描述: {audio_info['description'][:100]}...")
    
    if audio_info["audio_url"]:
        print(f"   音频链接: {audio_info['audio_url'][:50]}...")
    else:
        print(f"   ⚠️  未找到音频链接，使用模拟内容")
    
    return audio_info


def simulate_transcription(audio_info):
    """模拟音频转录（实际中会调用 Whisper API）"""
    print(f"\n🎤 模拟音频转录...")
    
    # 在实际应用中，这里会调用 OpenAI Whisper API
    # 现在我们先创建模拟转录文本
    
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
    transcript_dir = Path(__file__).parent / "data" / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建安全的文件名
    safe_title = "".join(c for c in audio_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title[:50]  # 限制长度
    
    transcript_file = transcript_dir / f"{safe_title}_transcript.txt"
    
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)
    
    print(f"✅ 转录完成")
    print(f"   保存到: {transcript_file}")
    
    return transcript, transcript_file


def generate_ai_summary(config, transcript):
    """使用 AI 生成总结"""
    print(f"\n🤖 使用 AI 生成总结...")
    
    api_key = config.get("OPENAI_API_KEY")
    base_url = config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = config.get("DEFAULT_AI_MODEL", "deepseek-chat")
    
    if not api_key:
        print("❌ 未找到 API Key 配置")
        return None, None
    
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
            summary_dir = Path(__file__).parent / "data" / "summaries"
            summary_dir.mkdir(parents=True, exist_ok=True)
            
            summary_file = summary_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_summary.md"
            
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            
            print(f"✅ AI 总结生成成功")
            print(f"   保存到: {summary_file}")
            
            # 显示部分内容
            print(f"\n   生成的总结（前200字）:")
            print(f"   {'='*50}")
            print(f"   {summary[:200]}...")
            print(f"   {'='*50}")
            
            return summary, summary_file
        else:
            print("❌ AI 总结生成失败")
            return None, None
            
    except Exception as e:
        print(f"❌ AI 总结失败: {e}")
        return None, None


def generate_note(podcast_info, audio_info, transcript, summary):
    """生成结构化笔记"""
    print(f"\n📝 生成结构化笔记...")
    
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
#播客 #AI总结 #{podcast_info['category']}

---
*本笔记由 CastMind 自动生成*
*处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存笔记文件
    notes_dir = Path(__file__).parent / "data" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建安全的文件名
    safe_title = "".join(c for c in audio_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title[:50]  # 限制长度
    
    note_file = notes_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_title}.md"
    
    with open(note_file, "w", encoding="utf-8") as f:
        f.write(note_content)
    
    print(f"✅ 笔记生成完成")
    print(f"   保存到: {note_file}")
    
    return note_file


def update_processing_log(podcast_name, status, files):
    """更新处理日志"""
    print(f"\n📊 更新处理日志...")
    
    # 在实际应用中，这里会更新数据库
    # 现在我们先打印日志
    
    log_entry = f"""
处理记录:
- 播客: {podcast_name}
- 时间: {datetime.now().isoformat()}
- 状态: {status}
- 生成文件:
  • 转录: {files.get('transcript', '无')}
  • 总结: {files.get('summary', '无')}
  • 笔记: {files.get('note', '无')}
"""
    
    print(log_entry)
    
    # 保存到日志文件
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / f"castmind_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print(f"✅ 日志保存到: {log_file}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python real_process_podcast.py <播客名称> [限制数量]")
        print("示例: python real_process_podcast.py \"BBC Global News\" 1")
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
    
    # 2. 获取播客信息
    podcast_info = get_podcast_info(podcast_name)
    if not podcast_info:
        return
    
    # 3. 解析 RSS
    feed = parse_rss_feed(podcast_info["rss_url"])
    if not feed:
        return
    
    # 处理指定数量的最新期数
    for i in range(min(limit, len(feed.entries))):
        print(f"\n{'='*60}")
        print(f"处理第 {i+1}/{min(limit, len(feed.entries))} 期")
        print(f"{'='*60}")
        
        entry = feed.entries[i]
        
        # 4. 模拟音频下载
        audio_info = simulate_audio_download(entry)
        
        # 5. 模拟转录
        transcript, transcript_file = simulate_transcription(audio_info)
        
        # 6. AI 总结
        summary, summary_file = generate_ai_summary(config, transcript)
        
        if not summary:
            print("⚠️  AI 总结失败，使用模拟总结继续")
            summary = "这是模拟的 AI 总结内容。在实际使用中，这里会是真实的 AI 生成总结。"
        
        # 7. 生成笔记
        note_file = generate_note(podcast_info, audio_info, transcript, summary)
        
        # 8. 更新日志
        files = {
            "transcript": str(transcript_file),
            "summary": str(summary_file) if summary_file else "无",
            "note": str(note_file)
        }
        
        update_processing_log(podcast_name, "完成", files)
    
    print(f"\n{'='*60}")
    print(f"✅ 处理完成！共处理 {min(limit, len(feed.entries))} 期播客")
    print(f"{'='*60}")
    
    print(f"\n📁 生成的文件:")
    print(f"   转录文件: data/transcripts/")
    print(f"   总结文件: data/summaries/")
    print(f"   笔记文件: data/notes/")
    print(f"   日志文件: logs/")
    
    print(f"\n🚀 下一步:")
    print(f"   1. 查看生成的文件: ls -la data/notes/")
    print(f"   2. 查看最新笔记: cat data/notes/*.md | head -20")
    print(f"   3. 处理其他播客: python real_process_podcast.py \"TED Talks Daily\" 1")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)