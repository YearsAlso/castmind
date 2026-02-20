#!/bin/bash
# 迁移现有文件到 Obsidian 目录

echo "🚚 迁移现有 CastMind 文件到 Obsidian 目录"
echo "=" * 60

# 源目录和目标目录
SOURCE_DIR="/Volumes/MxStore/Project/castmind/data"
TARGET_DIR="/Volumes/MxStore/Project/YearsAlso/Podcasts/CastMind"

# 检查目录
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ 源目录不存在: $SOURCE_DIR"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ 目标目录不存在: $TARGET_DIR"
    echo "请先运行: python3 config_obsidian_output.py"
    exit 1
fi

# 迁移函数
migrate_files() {
    local source_type=$1
    local target_type=$2
    
    local source_path="$SOURCE_DIR/$source_type"
    local target_path="$TARGET_DIR/$target_type"
    
    if [ -d "$source_path" ]; then
        echo "📁 迁移 $source_type → $target_type"
        
        # 创建目标目录
        mkdir -p "$target_path"
        
        # 复制文件
        if [ "$(ls -A "$source_path" 2>/dev/null)" ]; then
            cp -r "$source_path"/* "$target_path"/
            echo "   ✅ 复制 $(ls "$source_path" | wc -l) 个文件"
        else
            echo "   ⚠️  源目录为空"
        fi
    else
        echo "   ⚠️  源目录不存在: $source_path"
    fi
}

# 执行迁移
echo ""
echo "开始迁移文件..."
echo ""

migrate_files "transcripts" "transcripts"
migrate_files "summaries" "summaries"
migrate_files "notes" "notes"

# 迁移日志文件
echo ""
echo "📄 迁移日志文件..."
LOG_SOURCE="$SOURCE_DIR/../logs"
LOG_TARGET="$TARGET_DIR/metadata"

if [ -d "$LOG_SOURCE" ]; then
    mkdir -p "$LOG_TARGET"
    cp -r "$LOG_SOURCE"/* "$LOG_TARGET"/ 2>/dev/null || true
    echo "   ✅ 日志文件已迁移"
else
    echo "   ⚠️  日志目录不存在"
fi

# 创建软链接（可选）
echo ""
echo "🔗 创建软链接（可选）..."
read -p "是否创建从本地目录到 Obsidian 的软链接？(y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "创建软链接..."
    
    # 备份原有目录
    mv "$SOURCE_DIR/transcripts" "$SOURCE_DIR/transcripts.backup" 2>/dev/null || true
    mv "$SOURCE_DIR/summaries" "$SOURCE_DIR/summaries.backup" 2>/dev/null || true
    mv "$SOURCE_DIR/notes" "$SOURCE_DIR/notes.backup" 2>/dev/null || true
    
    # 创建软链接
    ln -s "$TARGET_DIR/transcripts" "$SOURCE_DIR/transcripts"
    ln -s "$TARGET_DIR/summaries" "$SOURCE_DIR/summaries"
    ln -s "$TARGET_DIR/notes" "$SOURCE_DIR/notes"
    
    echo "   ✅ 软链接创建完成"
    echo "   本地目录现在指向 Obsidian 目录"
fi

# 验证迁移结果
echo ""
echo "📊 迁移结果统计:"
echo ""

for dir_type in "transcripts" "summaries" "notes"; do
    target_path="$TARGET_DIR/$dir_type"
    if [ -d "$target_path" ]; then
        file_count=$(find "$target_path" -type f 2>/dev/null | wc -l)
        echo "  $dir_type: $file_count 个文件"
    else
        echo "  $dir_type: 目录不存在"
    fi
done

echo ""
echo "🎉 迁移完成！"
echo ""
echo "📁 文件现在位于:"
echo "   $TARGET_DIR/"
echo ""
echo "🚀 下一步:"
echo "   1. 在 Obsidian 中打开目录查看文件"
echo "   2. 使用 process_podcast_obsidian.py 处理新播客"
echo "   3. 所有新文件将自动保存到 Obsidian"
echo ""
echo "💡 提示:"
echo "   • 在 Obsidian 中使用 #播客 标签筛选"
echo "   • 使用双向链接 [[笔记名称]] 连接相关笔记"
echo "   • 定期备份 Obsidian 仓库"