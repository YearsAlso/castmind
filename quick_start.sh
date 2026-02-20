#!/bin/bash
# CastMind 快速开始脚本

echo "🧠🌊 CastMind 快速开始"
echo "=" * 60

# 检查是否在正确目录
if [ ! -f "castmind.py" ]; then
    echo "❌ 请在 CastMind 项目目录运行此脚本"
    echo "   当前目录: $(pwd)"
    echo "   应该位于: /Volumes/MxStore/Project/castmind"
    exit 1
fi

echo "1. 🔑 配置 API Key"
echo "   -------------------------"
echo "   请打开 config/.env 文件"
echo "   找到 OPENAI_API_KEY=你的OpenAI_API_Key_在这里"
echo "   替换 '你的OpenAI_API_Key_在这里' 为你的实际 API Key"
echo ""
read -p "   按回车继续，或 Ctrl+C 退出..."

# 测试配置
echo ""
echo "2. 🧪 测试配置"
echo "   -------------------------"
python test_config.py

echo ""
echo "3. 📦 安装依赖"
echo "   -------------------------"
read -p "   是否安装 Python 依赖包？(y/N): " install_deps
if [[ $install_deps =~ ^[Yy]$ ]]; then
    echo "   安装中..."
    pip install openai feedparser > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   ✅ 依赖安装完成"
    else
        echo "   ⚠️  依赖安装失败，请手动安装: pip install openai feedparser"
    fi
else
    echo "   ⏭️  跳过依赖安装"
fi

echo ""
echo "4. 📡 添加 RSS 订阅"
echo "   -------------------------"
echo "   你需要一个 RSS 链接来开始。"
echo "   以下是一些示例："
echo ""
echo "   a) 测试用 RSS（英文）:"
echo "      https://rss.art19.com/the-daily"
echo "      名称: The Daily"
echo "      标签: 新闻,测试"
echo ""
echo "   b) BBC 新闻（英文）:"
echo "      https://feeds.bbci.co.uk/news/rss.xml"
echo "      名称: BBC News"
echo "      标签: 新闻,国际"
echo ""
echo "   c) TED Talks（英文）:"
echo "      https://feeds.feedburner.com/TedTalks_audio"
echo "      名称: TED Talks"
echo "      标签: 演讲,知识"
echo ""
echo "   💡 提示：首次测试建议使用英文 RSS"
echo "       找到中文 RSS 后可以用同样方法添加"
echo ""

read -p "   输入 RSS 链接（或按回车跳过）: " rss_url
read -p "   输入播客名称: " podcast_name

if [ -n "$rss_url" ] && [ -n "$podcast_name" ]; then
    echo ""
    echo "   添加播客: $podcast_name"
    echo "   RSS: $rss_url"
    
    # 添加标签选项
    read -p "   输入标签（用逗号分隔，可选）: " tags
    
    if [ -n "$tags" ]; then
        python castmind.py add --url "$rss_url" --name "$podcast_name" --tags "$tags"
    else
        python castmind.py add --url "$rss_url" --name "$podcast_name"
    fi
    
    echo ""
    echo "5. 🎧 处理播客"
    echo "   -------------------------"
    read -p "   是否处理第一期节目？(y/N): " process_podcast
    
    if [[ $process_podcast =~ ^[Yy]$ ]]; then
        echo "   处理中...（这可能需要几分钟）"
        python castmind.py process --name "$podcast_name" --limit 1 --verbose
        
        echo ""
        echo "6. 📊 检查结果"
        echo "   -------------------------"
        echo "   生成的文件："
        ls -la data/transcripts/ 2>/dev/null || echo "   转录目录为空"
        ls -la data/summaries/ 2>/dev/null || echo "   总结目录为空"
        ls -la data/notes/ 2>/dev/null || echo "   笔记目录为空"
        
        echo ""
        echo "   查看最新笔记："
        latest_note=$(ls -t data/notes/*.md 2>/dev/null | head -1)
        if [ -n "$latest_note" ]; then
            echo "   📝 $latest_note"
            echo ""
            head -20 "$latest_note"
        fi
    else
        echo "   ⏭️  跳过处理"
    fi
else
    echo "   ⏭️  跳过 RSS 添加"
fi

echo ""
echo "🎯 下一步建议"
echo "=" * 60
echo ""
echo "1. 查看完整指南："
echo "   cat RSS_配置指南.md"
echo ""
echo "2. 查看所有命令："
echo "   python castmind.py --help"
echo ""
echo "3. 管理播客："
echo "   python castmind.py list          # 列出所有播客"
echo "   python castmind.py info --name \"名称\"  # 查看详情"
echo "   python castmind.py process-all   # 处理所有播客"
echo ""
echo "4. 查看状态："
echo "   python castmind.py status"
echo ""
echo "5. 查看日志："
echo "   tail -f logs/castmind.log"
echo ""
echo "💡 提示："
echo "   - 首次使用建议从简单的英文播客开始"
echo "   - 确保 API Key 有足够的额度"
echo "   - 处理过程中可以查看日志了解进度"
echo ""
echo "=" * 60
echo "✅ CastMind 快速开始完成！"
echo "=" * 60