# 📡 CastMind RSS 配置指南

## 🎯 快速开始

### 步骤 1: 准备你的 OpenAI API Key
1. 打开 `/Volumes/MxStore/Project/castmind/config/.env` 文件
2. 找到 `OPENAI_API_KEY=` 这一行
3. 将 `你的OpenAI_API_Key_在这里` 替换为你的实际 API Key
4. 保存文件

### 步骤 2: 测试配置
```bash
cd /Volumes/MxStore/Project/castmind

# 安装 OpenAI 包（如果未安装）
pip install openai

# 测试配置
python -c "
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from core.config import ConfigManager
config = ConfigManager('config')
api_key = config.get('OPENAI_API_KEY')
if api_key and '你的OpenAI_API_Key_在这里' not in api_key:
    print('✅ API Key 配置正确')
else:
    print('❌ 请先配置 API Key')
"
```

### 步骤 3: 添加 RSS 订阅

## 📋 RSS 配置方法

### 方法一：使用命令行添加（推荐）
```bash
cd /Volumes/MxStore/Project/castmind

# 基本格式
python castmind.py add --url "RSS链接" --name "播客名称"

# 示例：添加"得到"播客
python castmind.py add --url "https://www.ximalaya.com/album/XXXXX" --name "得到"

# 示例：添加"小宇宙"播客  
python castmind.py add --url "https://www.xiaoyuzhoufm.com/rss/XXXXX" --name "小宇宙播客"

# 添加分类标签
python castmind.py add --url "RSS链接" --name "名称" --tags "商业,科技,学习"
```

### 方法二：批量添加 RSS
创建一个 `rss_list.txt` 文件：
```
# 格式：名称,RSS链接,标签（可选）
得到,https://www.ximalaya.com/album/XXXXX,知识付费
商业就是这样,https://www.xiaoyuzhoufm.com/rss/YYYYY,商业,案例
疯投圈,https://feeds.fireside.fm/ZZZZZ/rss,投资,商业
```

然后运行：
```bash
python castmind.py add-batch --file rss_list.txt
```

### 方法三：直接编辑数据库（高级）
```bash
# 查看数据库
sqlite3 data/castmind.db "SELECT * FROM podcasts;"

# 手动添加
sqlite3 data/castmind.db "INSERT INTO podcasts (name, rss_url, enabled, created_at) VALUES ('测试播客', 'https://example.com/rss', 1, datetime('now'));"
```

## 🎧 推荐的中文播客 RSS 源

### 知识类播客
| 播客名称 | 可能找到 RSS 的地方 | 标签 |
|----------|-------------------|------|
| **得到** | 喜马拉雅专辑页面 | 知识付费,学习 |
| **看理想** | 看理想官网 | 文化,思想 |
| **故事FM** | 官网或播客平台 | 故事,人文 |
| **日谈公园** | 官网 | 文化,生活 |

### 商业类播客
| 播客名称 | 可能找到 RSS 的地方 | 标签 |
|----------|-------------------|------|
| **商业就是这样** | 第一财经 | 商业,案例 |
| **疯投圈** | 官网或播客平台 | 投资,VC |
| **贝望录** | 官网 | 营销,品牌 |
| **高能量** | 得到APP | 商业思维 |

### 科技类播客
| 播客名称 | 可能找到 RSS 的地方 | 标签 |
|----------|-------------------|------|
| **硅谷101** | 官网 | 科技,硅谷 |
| **科技早知道** | 播客平台 | 科技新闻 |
| **乱翻书** | 官网 | 互联网,产品 |
| **产品沉思录** | 少数派 | 产品,设计 |

### 生活类播客
| 播客名称 | 可能找到 RSS 的地方 | 标签 |
|----------|-------------------|------|
| **故事FM** | 官网 | 故事,人生 |
| **日谈公园** | 官网 | 文化,生活 |
| **博物志** | 官网 | 博物馆,文化 |
| **杯弓舌瘾** | 官网 | 酒,文化 |

## 🔍 如何找到 RSS 链接

### 方法 1: 播客平台
1. **喜马拉雅**：专辑页面 → 分享 → 复制链接
2. **小宇宙**：播客页面 → 更多 → 复制 RSS 链接
3. **Apple Podcasts**：播客页面 → 分享 → 复制节目链接
4. **Spotify**：播客页面 → ... → 分享 → 复制链接

### 方法 2: 搜索引擎
```
搜索词："播客名称 RSS" 或 "播客名称 feed"
示例："得到 RSS"、"商业就是这样 feed"
```

### 方法 3: 播客官网
很多播客会在官网提供 RSS 订阅链接。

### 方法 4: RSS 查找工具
- [GetRSSFeed](https://getrssfeed.com/) - 从网站提取 RSS
- [RSS.app](https://rss.app/) - RSS 生成器
- [Podlink](https://pod.link/) - 播客链接查找

## 🛠️ RSS 测试和验证

### 测试 RSS 链接是否有效
```bash
# 使用 curl 测试
curl -I "你的RSS链接"

# 应该返回 200 OK 和 Content-Type: application/xml

# 查看 RSS 内容
curl "你的RSS链接" | head -50
```

### 常见的 RSS 格式问题
1. **链接失效**：返回 404 或 403
2. **格式错误**：不是有效的 XML
3. **内容为空**：没有节目信息
4. **需要认证**：私有 RSS 需要 token

### 修复 RSS 链接
```bash
# 如果 RSS 链接需要修改
# 原始链接：https://www.ximalaya.com/album/123456
# RSS 链接：https://www.ximalaya.com/album/123456.xml
# 或：https://www.ximalaya.com/album/123456/feed.xml
```

## 📊 管理 RSS 订阅

### 查看已添加的播客
```bash
# 列出所有播客
python castmind.py list

# 查看播客详情
python castmind.py info --name "播客名称"

# 查看播客节目列表
python castmind.py episodes --name "播客名称"
```

### 启用/禁用播客
```bash
# 禁用播客（暂停处理）
python castmind.py disable --name "播客名称"

# 启用播客
python castmind.py enable --name "播客名称"

# 删除播客
python castmind.py remove --name "播客名称"
```

### 更新 RSS 链接
```bash
# 更新 RSS 链接
python castmind.py update --name "播客名称" --url "新的RSS链接"
```

## 🚀 开始处理播客

### 处理单个播客
```bash
# 处理最新一期
python castmind.py process --name "播客名称"

# 处理最新3期
python castmind.py process --name "播客名称" --limit 3

# 指定使用 OpenAI
python castmind.py process --name "播客名称" --model openai

# 详细输出
python castmind.py process --name "播客名称" --verbose
```

### 批量处理
```bash
# 处理所有启用的播客
python castmind.py process-all

# 限制处理数量
python castmind.py process-all --limit 5

# 只处理特定标签
python castmind.py process-all --tags "商业,科技"
```

### 定时处理
```bash
# 设置定时任务（每小时检查一次）
python castmind.py schedule --interval 3600

# 查看定时任务状态
python castmind.py schedule-status
```

## 📁 文件结构和数据

### 项目结构
```
castmind/
├── data/                    # 数据目录
│   ├── audio/              # 下载的音频文件
│   ├── transcripts/        # 转录文本
│   ├── summaries/          # AI总结
│   ├── notes/              # 生成的笔记
│   └── castmind.db         # SQLite数据库
├── config/                 # 配置目录
│   ├── .env               # 环境变量（你的API Key在这里）
│   ├── ai_models.json     # AI模型配置
│   └── workflows.json     # 工作流配置
└── logs/                  # 日志目录
```

### 数据库结构
```sql
-- 播客表
CREATE TABLE podcasts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    rss_url TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 节目表
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY,
    podcast_id INTEGER,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    published_date DATETIME,
    processed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 处理记录表
CREATE TABLE processing_logs (
    id INTEGER PRIMARY KEY,
    episode_id INTEGER,
    status TEXT,  -- pending, downloading, transcribing, summarizing, completed, failed
    transcript_path TEXT,
    summary_path TEXT,
    note_path TEXT,
    started_at DATETIME,
    completed_at DATETIME
);
```

## 🧪 测试完整流程

### 测试脚本
```bash
#!/bin/bash
# test_full_process.sh

echo "🧪 测试完整播客处理流程"
echo "=" * 60

# 1. 检查配置
echo "1. 检查 API Key 配置..."
python -c "
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path('.').parent / 'src'))
from core.config import ConfigManager
config = ConfigManager('config')
api_key = config.get('OPENAI_API_KEY')
if api_key and '你的OpenAI_API_Key_在这里' not in api_key:
    print('✅ API Key 配置正确')
else:
    print('❌ 请先配置 API Key')
    exit(1)
"

# 2. 添加测试播客
echo "2. 添加测试播客..."
python castmind.py add --url "https://rss.art19.com/the-daily" --name "测试播客" --tags "测试"

# 3. 列出播客
echo "3. 查看播客列表..."
python castmind.py list

# 4. 处理一期
echo "4. 处理最新一期..."
python castmind.py process --name "测试播客" --limit 1 --verbose

# 5. 检查结果
echo "5. 检查处理结果..."
ls -la data/transcripts/
ls -la data/summaries/
ls -la data/notes/

echo "✅ 测试完成"
```

### 手动测试步骤
1. **配置 API Key**：编辑 `.env` 文件
2. **添加测试 RSS**：找一个简单的 RSS 链接测试
3. **处理一期节目**：验证整个流程
4. **检查输出**：确认文件生成正确

## 🚨 常见问题解决

### Q1: RSS 链接无效
```
错误: Failed to parse RSS feed
解决: 
1. 验证 RSS 链接是否能正常访问
2. 尝试其他 RSS 格式
3. 检查是否需要特殊处理
```

### Q2: 音频下载失败
```
错误: Failed to download audio
解决:
1. 检查网络连接
2. 增加 DOWNLOAD_TIMEOUT
3. 检查音频链接是否有效
```

### Q3: API 调用失败
```
错误: OpenAI API error
解决:
1. 检查 API Key 是否正确
2. 检查账户余额
3. 检查网络连接
```

### Q4: 内存不足
```
错误: MemoryError
解决:
1. 减少 DEFAULT_PODCAST_LIMIT
2. 增加系统内存
3. 分批处理
```

## 📈 最佳实践

### RSS 管理最佳实践
1. **定期验证**：每月检查一次 RSS 链接是否有效
2. **分类标签**：为播客添加标签，方便筛选
3. **质量优先**：选择更新稳定、内容优质的播客
4. **数量控制**：开始时添加 3-5 个播客，逐步增加

### 处理策略最佳实践
1. **分批处理**：不要一次性处理太多期
2. **错峰处理**：避开 API 使用高峰期
3. **监控成本**：定期检查 API 使用情况
4. **备份数据**：定期备份数据库和处理结果

### 性能优化建议
1. **使用缓存**：启用缓存减少重复处理
2. **并行处理**：配置合适的并发数
3. **清理旧数据**：定期清理不需要的音频文件
4. **优化存储**：使用 SSD 提升 I/O 性能

## 🎯 总结

### 快速开始清单
1. ✅ 编辑 `.env` 文件，填入 OpenAI API Key
2. ✅ 测试 API Key 配置
3. ✅ 添加第一个 RSS 订阅
4. ✅ 处理第一期节目
5. ✅ 检查生成的结果

### 成功标志
- ✅ `.env` 文件配置正确
- ✅ RSS 订阅添加成功
- ✅ 音频下载完成
- ✅ 转录和总结生成
- ✅ 笔记保存到 `data/notes/`

### 下一步
1. **探索更多功能**：尝试不同的 AI 模型
2. **优化配置**：调整参数获得更好效果
3. **扩展播客库**：添加更多感兴趣的播客
4. **集成知识库**：将笔记同步到 Obsidian

## 📞 获取帮助

```bash
# 查看所有命令
python castmind.py --help

# 查看命令详细帮助
python castmind.py add --help
python castmind.py process --help

# 查看系统状态
python castmind.py status

# 查看日志
tail -f logs/castmind.log
```

---

**文档生成时间**: 2026-02-19 16:20  
**文档位置**: `/Volumes/MxStore/Project/castmind/RSS_配置指南.md`

**牛马提示**: 🐂 先配置好 API Key，🐴 再添加 RSS 订阅，🚀 然后就可以开始处理播客了！每个步骤都有详细说明，遇到问题随时查看常见问题部分！📡🎧