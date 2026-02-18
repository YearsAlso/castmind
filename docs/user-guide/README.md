# 📖 CastMind 用户手册

欢迎使用CastMind！本手册将指导您完成安装、配置和使用CastMind播客智能流系统的全过程。

## 🎯 概述

CastMind是一个智能化的播客处理系统，能够自动：
- 📡 订阅和解析播客RSS
- 🎧 下载和处理音频内容
- 🧠 使用AI进行深度分析
- 📝 生成结构化知识笔记
- 🔍 构建智能知识图谱

## 🚀 快速开始

### 1. 系统要求
- Python 3.9+
- 4GB以上内存
- 10GB以上磁盘空间
- 稳定的网络连接

### 2. 安装步骤

#### 使用uv安装（推荐）
```bash
# 克隆项目
git clone https://github.com/YearsAlso/castmind.git
cd castmind

# 安装uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
uv sync
```

#### 使用pip安装
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置系统

#### 复制环境变量模板
```bash
cp config/.env.example config/.env
```

#### 编辑配置文件
编辑 `config/.env` 文件，填入必要的API密钥：

```bash
# AI服务配置
OPENAI_API_KEY=sk-your-openai-key-here
DEEPSEEK_API_KEY=your-deepseek-key-here
KIMI_API_KEY=your-kimi-key-here

# 系统配置
CASTMIND_ENV=development
LOG_LEVEL=INFO
DATA_PATH=./data
```

#### 验证配置
```bash
python castmind.py config --validate
```

## 📡 基本使用

### 1. 启动系统
```bash
# 启动CastMind系统
python castmind.py start

# 开发模式（热重载）
python castmind.py start --reload
```

### 2. 订阅播客
```bash
# 添加播客订阅
python castmind.py subscribe \
  --name "商业思维" \
  --url "https://example.com/podcast/rss"

# 查看订阅列表
python castmind.py subscribe --list
```

### 3. 处理播客
```bash
# 处理特定播客的最新3期
python castmind.py process \
  --name "商业思维" \
  --limit 3

# 处理所有订阅
python castmind.py process --all
```

### 4. 查看状态
```bash
# 查看系统状态
python castmind.py status

# 详细状态信息
python castmind.py status --detailed

# 查看处理日志
python castmind.py logs
```

## ⚙️ 配置详解

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | - | 是 |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - | 是 |
| `KIMI_API_KEY` | Kimi API密钥 | - | 是 |
| `CASTMIND_ENV` | 运行环境 | `development` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `DATA_PATH` | 数据存储路径 | `./data` | 否 |
| `DEFAULT_PODCAST_LIMIT` | 默认处理数量 | `5` | 否 |
| `AUTO_PROCESS_INTERVAL` | 自动处理间隔(秒) | `3600` | 否 |

### 配置文件

#### AI模型配置 (`config/ai_models.json`)
配置可用的AI模型及其参数：
```json
{
  "models": {
    "deepseek": {
      "name": "DeepSeek",
      "provider": "deepseek",
      "model": "deepseek-chat",
      "capabilities": ["analysis", "summary", "translation"],
      "max_tokens": 4096,
      "temperature": 0.7,
      "cost_per_token": 0.0000014
    }
  }
}
```

#### 工作流配置 (`config/workflows.json`)
配置处理工作流：
```json
{
  "workflows": {
    "basic_processing": {
      "name": "基础处理工作流",
      "steps": ["rss_parsing", "audio_download", "transcription", "ai_summary", "note_generation"]
    }
  }
}
```

## 🔄 工作流程

### 标准处理流程
1. **RSS解析** → 获取播客信息和剧集列表
2. **音频下载** → 下载音频文件到本地
3. **语音转录** → 将音频转换为文字
4. **AI分析** → 深度分析和智能总结
5. **笔记生成** → 创建结构化Markdown笔记
6. **知识存储** → 保存到知识库并建立关联

### 自定义工作流
您可以在 `config/workflows.json` 中自定义工作流：
- 调整处理步骤顺序
- 启用/禁用特定步骤
- 配置步骤参数
- 设置错误处理策略

## 📊 监控与管理

### 系统监控
```bash
# 查看实时状态
python castmind.py monitor

# 查看性能指标
python castmind.py metrics

# 查看资源使用
python castmind.py resources
```

### 日志管理
```bash
# 查看系统日志
tail -f logs/castmind.log

# 查看特定服务日志
python castmind.py logs --service workflow

# 查看错误日志
python castmind.py logs --level ERROR
```

### 数据管理
```bash
# 备份数据
python castmind.py backup --output backup.tar.gz

# 恢复数据
python castmind.py restore --input backup.tar.gz

# 清理临时文件
python castmind.py cleanup
```

## 🎯 高级功能

### 1. 批量处理
```bash
# 批量处理多个播客
python castmind.py batch \
  --input podcasts.txt \
  --output ./results \
  --parallel 3
```

### 2. 定时任务
```bash
# 设置定时处理
python castmind.py schedule \
  --cron "0 8 * * *" \
  --workflow basic_processing

# 查看定时任务
python castmind.py schedule --list

# 删除定时任务
python castmind.py schedule --remove <task_id>
```

### 3. Web管理界面
```bash
# 启动Web界面
python castmind.py web

# 访问 http://localhost:8000
```

### 4. API接口
```bash
# 启动API服务
python castmind.py api

# 使用curl测试API
curl http://localhost:8000/api/v1/status
```

## 🔧 故障排除

### 常见问题

#### 问题1：API密钥错误
**症状**：AI分析失败，日志显示认证错误
**解决**：
1. 检查 `config/.env` 文件中的API密钥
2. 确保密钥有足够的额度
3. 验证网络连接

#### 问题2：音频下载失败
**症状**：下载进度卡住或失败
**解决**：
1. 检查网络连接
2. 验证RSS链接有效性
3. 检查磁盘空间

#### 问题3：内存不足
**症状**：处理过程中程序崩溃
**解决**：
1. 减少并发处理数量
2. 增加系统内存
3. 使用更小的AI模型

### 获取帮助
```bash
# 查看帮助
python castmind.py --help

# 查看命令帮助
python castmind.py <command> --help

# 查看详细文档
python castmind.py docs
```

## 📚 下一步

- 阅读 [API文档](../api/README.md) 了解完整接口
- 查看 [部署指南](../deployment/README.md) 了解生产部署
- 参与 [开发指南](../development/README.md) 了解如何贡献

## 🤝 支持与反馈

- **问题报告**: [GitHub Issues](https://github.com/YearsAlso/castmind/issues)
- **功能请求**: [GitHub Discussions](https://github.com/YearsAlso/castmind/discussions)
- **文档反馈**: 提交Pull Request或Issue

---

**最后更新**: 2026-02-18  
**文档版本**: v1.0.0