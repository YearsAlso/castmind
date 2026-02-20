# 🐳 CastMind - Docker 容器化部署指南

## 🎯 概述

CastMind 是一个播客智能处理系统，现在支持完整的 Docker 容器化部署。本指南将帮助你快速部署 CastMind 到任何支持 Docker 的环境。

## 📋 功能特性

### ✅ 已实现的功能
- 🐳 **完整 Docker 化** - 多阶段构建，生产就绪
- 🔄 **CI/CD 流水线** - GitHub Actions 自动化
- 🎧 **后台服务** - 7x24 小时持久运行
- 📊 **监控系统** - 健康检查和性能监控
- 🔒 **安全加固** - 非 root 运行，最小权限
- 📁 **数据持久化** - 卷挂载，数据安全

### 🚀 部署选项
- **开发环境** - 快速本地测试
- **测试环境** - CI/CD 自动部署
- **生产环境** - 高可用集群部署
- **NAS 部署** - 家庭服务器专用配置

## 🚀 快速开始

### 1. 环境要求
```bash
# 检查 Docker
docker --version
docker-compose --version

# 要求
- Docker 20.10+
- Docker Compose 2.0+
- 2GB 可用内存
- 5GB 磁盘空间
```

### 2. 克隆项目
```bash
git clone https://github.com/your-org/castmind.git
cd castmind
git checkout feature/docker-ci-backend
```

### 3. 配置环境
```bash
# 复制环境变量模板
cp .env.template .env

# 编辑配置
vi .env
```

### 4. 一键部署
```bash
# 赋予执行权限
chmod +x deploy.sh

# 标准部署
./deploy.sh

# 开发模式部署
./deploy.sh --dev
```

## 📁 项目结构

```
castmind/
├── .github/workflows/          # GitHub Actions 工作流
│   └── ci-cd.yml              # CI/CD 流水线
├── config/                    # 配置文件
│   └── obsidian_output.json   # Obsidian 集成配置
├── Dockerfile                 # Docker 构建文件
├── docker-compose.yml         # Docker 编排配置
├── castmind_service.py        # 后台服务脚本
├── deploy.sh                  # 部署脚本
├── .env.template              # 环境变量模板
├── requirements.txt           # Python 依赖
└── README-DOCKER.md           # 本文档
```

## 🐳 Docker 配置详解

### 多阶段构建
```dockerfile
# 构建阶段
FROM python:3.9-slim AS builder
# 安装构建依赖

# 生产阶段  
FROM python:3.9-slim AS production
# 最小化生产镜像

# 开发阶段
FROM builder AS development
# 包含调试工具
```

### 服务编排
```yaml
services:
  castmind:        # 主服务
  redis:           # 消息队列
  celery-worker:   # 任务处理
  celery-beat:     # 定时调度
  postgres:        # 数据库（可选）
  monitoring:      # 监控面板
```

## 🔄 CI/CD 流水线

### 自动化流程
```
代码推送 → 质量检查 → 单元测试 → 集成测试 → 
Docker 构建测试 → 安全扫描 → 生成报告
```

### GitHub Actions 工作流
1. **🔍 CI 工作流** (`ci.yml`)
   - **代码质量检查** - Black, Flake8, MyPy, Bandit
   - **自动化测试** - 单元测试 + 集成测试
   - **Docker 构建测试** - 验证构建过程
   - **测试报告** - 覆盖率报告和测试结果

2. **🐳 镜像发布工作流** (`publish-images.yml`)
   - **自动标签生成** - 基于 Git 标签和分支
   - **多架构构建** - amd64 + arm64 支持
   - **安全扫描** - Trivy 漏洞扫描
   - **SBOM 生成** - 软件物料清单
   - **自动发布** - GitHub Releases 和容器镜像

### 标签策略
```
Git 标签 → Docker 镜像标签
v1.2.3      → v1.2.3, 1.2.3, 1.2, 1, latest
v1.2.3-rc1  → v1.2.3-rc1, 1.2.3-rc1
main 分支   → latest, sha-<commit-hash>
其他分支    → <branch-name>, sha-<commit-hash>
```

## 🎧 后台服务

### 服务特性
```python
class CastMindService:
    """后台服务类"""
    - 定时任务调度
    - 健康检查报告
    - 优雅关闭处理
    - 错误重试机制
    - 资源监控统计
```

### 定时任务
- **每30分钟** - 处理播客任务
- **每10分钟** - 检查 RSS 更新
- **每天03:00** - 清理旧文件
- **每小时** - 健康报告

## 📊 监控和维护

### 健康检查
```bash
# 手动检查
curl http://localhost:8000/api/v1/health

# Docker 健康检查
docker inspect --format='{{.State.Health.Status}}' castmind
```

### 日志查看
```bash
# 查看所有日志
docker-compose logs

# 实时查看
docker-compose logs -f castmind

# 查看特定服务
docker-compose logs -f celery-worker
```

### 数据备份
```bash
# 手动备份
./deploy.sh --backup

# 自动备份（配置在 .env）
BACKUP_SCHEDULE="0 2 * * *"  # 每天凌晨2点
```

## 🔒 安全配置

### 容器安全
```yaml
security_opt:
  - no-new-privileges:true
read_only: true
user: "1000:1000"  # 非 root 用户
```

### 网络安全
```yaml
networks:
  castmind-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 数据加密
```bash
# 使用 Docker Secrets
echo "your_api_key" | docker secret create openai_api_key -
```

## 🏠 NAS 部署指南

### 群晖 DSM
```yaml
# docker-compose.yml (群晖优化)
volumes:
  - /volume1/docker/castmind/data:/app/data
environment:
  - PUID=1026  # 群晖默认用户ID
  - PGID=100   # 群晖默认组ID
```

### 威联通 QNAP
```yaml
# docker-compose.yml (QNAP 优化)
volumes:
  - /share/CACHEDEV1_DATA/Container/castmind/data:/app/data
network_mode: host  # QNAP 推荐
```

## 🚨 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细日志
docker-compose logs castmind

# 检查端口占用
netstat -tulpn | grep :8000
```

#### 2. 数据库连接问题
```bash
# 检查数据库文件权限
ls -la data/

# 重建数据库
docker-compose exec castmind python -c "from app.database import init_db; init_db()"
```

#### 3. AI 服务失败
```bash
# 测试 API Key
docker-compose exec castmind python test_api_key.py

# 检查网络连接
docker-compose exec castmind ping api.deepseek.com
```

#### 4. 内存不足
```bash
# 查看内存使用
docker stats

# 调整内存限制
# 在 .env 中设置: MEMORY_LIMIT=2048
```

### 调试模式
```bash
# 进入容器
docker-compose exec castmind bash

# 查看环境变量
env | grep -i castmind

# 手动运行服务
python castmind_service.py --debug
```

## 📈 性能优化

### 资源限制
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '2'
    reservations:
      memory: 512M
      cpus: '1'
```

### 缓存配置
```yaml
# Redis 缓存
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 数据库优化
```sql
-- PostgreSQL 优化
ALTER DATABASE castmind SET work_mem = '16MB';
ALTER DATABASE castmind SET maintenance_work_mem = '64MB';
```

## 🔄 更新和升级

### 常规更新
```bash
# 拉取最新代码
git pull origin feature/docker-ci-backend

# 更新服务
./deploy.sh --update
```

### 版本升级
```bash
# 备份数据
./deploy.sh --backup

# 停止旧服务
docker-compose down

# 更新配置
git checkout new-version
cp .env.template .env
# 编辑 .env 文件

# 启动新服务
./deploy.sh
```

### 回滚操作
```bash
# 恢复到备份
./deploy.sh --restore backups/castmind_backup_20260219_120000.tar.gz

# 切换回旧版本
git checkout old-version
docker-compose