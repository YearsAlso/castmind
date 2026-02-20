# 🎧 CastMind Zoo - Zoo Framework + FastAPI 集成框架

## 🚀 概述

CastMind Zoo 是基于 **Zoo Framework** 和 **FastAPI** 的播客智能处理系统。采用 **继承为主，插件为辅** 的混合架构，深度集成两个框架的优势。

## 🏗️ 架构设计

### **核心架构**
```
🎧 CastMindMaster (继承 Zoo Framework Master)
├── 🦁 Worker 管理 (继承 Zoo Framework 核心)
├── 🔄 事件系统 (继承 Zoo Framework 事件)
├── 🚀 FastAPI 服务 (深度集成)
├── 📊 状态机管理
├── 🗃️ 任务队列
└── 🔌 插件系统 (可选扩展)
```

### **技术栈**
- **框架**: Zoo Framework (Python 多线程框架)
- **Web API**: FastAPI (现代化异步 Web 框架)
- **数据库**: SQLite (默认) / PostgreSQL (可选)
- **缓存**: Redis (可选)
- **任务队列**: 内存队列 / Celery (可选)
- **监控**: Prometheus + Grafana (可选)

## 📁 项目结构

```
castmind_zoo/
├── __init__.py              # 包定义
├── master.py               # 主控制器 (继承 Zoo Framework)
├── config.py               # 配置管理
├── api/                    # FastAPI 路由
│   ├── dependencies.py     # 依赖注入
│   └── routers/           # 路由模块
│       ├── health.py      # 健康检查
│       ├── workers.py     # Worker 管理
│       ├── tasks.py       # 任务管理
│       ├── podcasts.py    # 播客管理
│       └── system.py      # 系统管理
└── workers/               # Worker 实现
    └── test_worker.py     # 测试 Worker
```

## 🚀 快速开始

### **1. 安装依赖**
```bash
# 安装基础依赖
pip install fastapi uvicorn psutil

# 安装 Zoo Framework (如果可用)
# pip install zoo-framework

# 或者从源码安装
cd /path/to/zoo-framework
pip install -e .
```

### **2. 启动服务**
```bash
# 使用默认配置启动
python run_castmind_zoo.py

# 使用自定义配置
python run_castmind_zoo.py --config config.json --port 8080 --debug

# 指定 Worker 数量
python run_castmind_zoo.py --workers 10 --port 8000
```

### **3. 访问服务**
```
🌐 Web 界面: http://localhost:8000
📚 API 文档: http://localhost:8000/api/docs
🔍 健康检查: http://localhost:8000/api/v1/health
```

## ⚙️ 配置说明

### **配置文件示例**
```json
{
  "environment": "development",
  "debug": true,
  "api": {
    "port": 8000,
    "host": "0.0.0.0"
  },
  "ai": {
    "deepseek_api_key": "your_key_here"
  }
}
```

### **环境变量**
```bash
# 基础配置
export ENVIRONMENT=production
export DEBUG=false

# API 配置
export API_PORT=8000
export API_HOST=0.0.0.0
export API_KEY=your_api_key

# AI 配置
export DEEPSEEK_API_KEY=your_deepseek_key
export OPENAI_API_KEY=your_openai_key

# 数据目录
export DATA_DIR=/data/castmind
```

## 🔧 API 端点

### **健康检查**
```
GET  /api/v1/health           # 基础健康检查
GET  /api/v1/health/detailed  # 详细系统信息
GET  /api/v1/health/readiness # Kubernetes 就绪检查
GET  /api/v1/health/liveness  # Kubernetes 存活检查
GET  /api/v1/health/metrics   # 性能指标
GET  /api/v1/health/config    # 配置检查
```

### **Worker 管理**
```
GET  /api/v1/workers          # 获取 Worker 列表
GET  /api/v1/workers/{id}     # 获取 Worker 详情
POST /api/v1/workers/{id}/restart  # 重启 Worker
GET  /api/v1/workers/{id}/metrics  # Worker 指标
GET  /api/v1/workers/stats    # Worker 统计
POST /api/v1/workers/scale    # 调整 Worker 数量
```

### **任务管理**
```
GET  /api/v1/tasks            # 获取任务列表
GET  /api/v1/tasks/{id}       # 获取任务详情
POST /api/v1/tasks            # 创建新任务
POST /api/v1/tasks/batch      # 批量创建任务
POST /api/v1/tasks/{id}/cancel    # 取消任务
POST /api/v1/tasks/{id}/retry     # 重试任务
GET  /api/v1/tasks/queue/stats    # 队列统计
POST /api/v1/tasks/queue/clear    # 清空队列
```

### **系统管理**
```
GET  /api/v1/system/info      # 系统信息
GET  /api/v1/system/config    # 当前配置
POST /api/v1/system/reload    # 重载配置
POST /api/v1/system/shutdown  # 优雅关闭
GET  /api/v1/system/logs      # 查看日志
POST /api/v1/system/backup    # 备份数据
```

## 🎯 核心特性

### **1. 深度集成**
- ✅ 继承 Zoo Framework Master，充分利用框架功能
- ✅ 集成 FastAPI，提供现代化 Web API
- ✅ 统一的事件驱动架构
- ✅ 共享状态机和配置管理

### **2. 高性能**
- ✅ 多线程 Worker 池
- ✅ 异步 Web 服务器
- ✅ 内存高效的任务队列
- ✅ 实时性能监控

### **3. 可扩展性**
- ✅ 插件系统支持功能扩展
- ✅ 可配置的 Worker 数量
- ✅ 支持多种数据库后端
- ✅ 模块化的 API 设计

### **4. 生产就绪**
- ✅ 健康检查和监控
- ✅ 优雅启动和关闭
- ✅ 配置验证和热重载
- ✅ 详细的日志和错误处理

## 🔄 工作流程

### **任务处理流程**
```
1. API 接收任务请求
2. 任务加入 Zoo Framework 事件队列
3. Worker 从队列获取任务
4. Worker 处理任务（RSS 解析、音频下载、转录、AI 总结等）
5. 结果保存到数据库和文件系统
6. 通过 WebSocket 或轮询通知客户端
```

### **系统启动流程**
```
1. 加载配置和环境变量
2. 初始化 Zoo Framework Master
3. 创建 FastAPI 应用和路由
4. 启动 Worker 池
5. 启动 Web 服务器
6. 启动监控和调度器
7. 进入主事件循环
```

## 📊 监控和日志

### **监控指标**
- CPU 和内存使用率
- 任务队列长度和处理时间
- Worker 状态和性能
- API 请求统计和延迟
- 数据库连接和查询性能

### **日志系统**
- 结构化 JSON 日志
- 按级别过滤（DEBUG, INFO, WARNING, ERROR）
- 日志轮转和归档
- 集成到系统日志

## 🔒 安全特性

### **API 安全**
- API Key 认证
- CORS 配置
- 速率限制
- 请求验证和过滤
- 敏感信息隐藏

### **系统安全**
- 非 root 用户运行（容器中）
- 文件权限控制
- 配置加密（可选）
- 安全头设置

## 🐳 Docker 部署

### **Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run_castmind_zoo.py", "--port", "8000"]
```

### **docker-compose.yml**
```yaml
version: '3.8'

services:
  castmind:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## 🚨 故障排除

### **常见问题**

#### **1. Zoo Framework 未安装**
```
错误: ModuleNotFoundError: No module named 'zoo_framework'
解决: 安装 Zoo Framework 或使用模拟模式
```

#### **2. 端口被占用**
```
错误: Address already in use
解决: 更改端口 --port 8080 或杀死占用进程
```

#### **3. 权限问题**
```
错误: Permission denied
解决: 确保数据目录可写，或使用 --data-dir 参数
```

#### **4. API Key 无效**
```
错误: 401 Unauthorized
解决: 设置正确的 API Key 或禁用认证
```

### **调试模式**
```bash
# 启用调试模式
python run_castmind_zoo.py --debug

# 查看详细日志
tail -f logs/castmind.log

# 检查系统状态
curl http://localhost:8000/api/v1/health/detailed
```

## 📈 性能优化

### **硬件建议**
- CPU: 4+ 核心
- 内存: 8GB+ RAM
- 存储: SSD 推荐
- 网络: 稳定连接

### **配置优化**
```json
{
  "worker": {
    "rss_parser_count": 4,
    "audio_downloader_count": 6,
    "transcription_worker_count": 4,
    "ai_processor_count": 4
  },
  "api": {
    "workers": 8
  }
}
```

### **监控建议**
- 设置 Prometheus 监控
- 配置告警规则
- 定期检查日志
- 性能测试和基准测试

## 🔮 未来计划

### **短期计划**
- [ ] 完整的播客处理 Worker 实现
- [ ] 数据库集成（SQLite/PostgreSQL）
- [ ] Redis 缓存支持
- [ ] WebSocket 实时通知
- [ ] 管理界面开发

### **长期计划**
- [ ] 插件系统完善
- [ ] 分布式部署支持
- [ ] 机器学习模型集成
- [ ] 移动端应用
- [ ] 社区功能

## 📞 支持与贡献

### **问题报告**
- GitHub Issues: 报告 bug 和功能请求
- 文档更新: 改进文档和示例
- 代码贡献: Pull Requests 欢迎

### **社区**
- 讨论区: GitHub Discussions
- 文档: 详细的使用指南
- 示例: 完整的示例项目

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🙏 致谢

- **Zoo Framework** - 强大的 Python 多线程框架
- **FastAPI** - 现代化高性能 Web 框架
- **所有贡献者** - 感谢你们的支持和贡献

---

**开始使用 CastMind Zoo，享受高效的播客处理体验！** 🎧🚀