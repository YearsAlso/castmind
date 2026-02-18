# 🚀 CastMind 部署指南

本指南介绍如何在不同环境中部署CastMind播客智能流系统。

## 📋 部署选项

| 部署方式 | 适用场景 | 复杂度 | 维护成本 |
|----------|----------|--------|----------|
| [本地部署](#本地部署) | 开发测试、个人使用 | 低 | 低 |
| [Docker部署](#docker部署) | 生产环境、团队使用 | 中 | 中 |
| [Kubernetes部署](#kubernetes部署) | 大规模生产、高可用 | 高 | 高 |
| [云服务部署](#云服务部署) | 企业级、弹性伸缩 | 高 | 高 |

## 🖥️ 本地部署

### 系统要求
- **操作系统**: Linux、macOS、Windows (WSL2)
- **Python**: 3.9+
- **内存**: 4GB+
- **磁盘**: 10GB+
- **网络**: 稳定的互联网连接

### 安装步骤

#### 1. 下载代码
```bash
# 克隆仓库
git clone https://github.com/YearsAlso/castmind.git
cd castmind

# 或下载发布版本
wget https://github.com/YearsAlso/castmind/releases/latest/download/castmind.tar.gz
tar -xzf castmind.tar.gz
cd castmind
```

#### 2. 安装依赖
```bash
# 使用uv（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv sync

# 或使用pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. 配置系统
```bash
# 复制配置文件
cp config/.env.example config/.env

# 编辑配置文件
nano config/.env
```

配置文件示例：
```bash
# AI服务配置
OPENAI_API_KEY=sk-your-openai-key
DEEPSEEK_API_KEY=your-deepseek-key
KIMI_API_KEY=your-kimi-key

# 系统配置
CASTMIND_ENV=production
LOG_LEVEL=INFO
DATA_PATH=/var/lib/castmind/data

# 网络配置
HOST=0.0.0.0
PORT=8000
```

#### 4. 初始化数据
```bash
# 创建数据目录
mkdir -p /var/lib/castmind/data
chmod 755 /var/lib/castmind/data

# 初始化数据库
python castmind.py init
```

#### 5. 启动服务
```bash
# 前台运行（开发）
python castmind.py start

# 后台运行（生产）
nohup python castmind.py start > castmind.log 2>&1 &

# 使用systemd（Linux）
sudo cp scripts/castmind.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable castmind
sudo systemctl start castmind
```

### systemd服务文件
创建 `/etc/systemd/system/castmind.service`：
```ini
[Unit]
Description=CastMind Podcast Intelligence System
After=network.target

[Service]
Type=simple
User=castmind
Group=castmind
WorkingDirectory=/opt/castmind
Environment="PATH=/opt/castmind/.venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/castmind/config/.env
ExecStart=/opt/castmind/.venv/bin/python castmind.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🐳 Docker部署

### 1. 使用预构建镜像
```bash
# 拉取最新镜像
docker pull ghcr.io/yearsalso/castmind:latest

# 运行容器
docker run -d \
  --name castmind \
  -p 8000:8000 \
  -v castmind_data:/app/data \
  -e OPENAI_API_KEY="your-api-key" \
  ghcr.io/yearsalso/castmind:latest
```

### 2. 使用Docker Compose
创建 `docker-compose.yml`：
```yaml
version: '3.8'

services:
  castmind:
    image: ghcr.io/yearsalso/castmind:latest
    container_name: castmind
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - castmind_data:/app/data
      - ./config:/app/config
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - KIMI_API_KEY=${KIMI_API_KEY}
      - CASTMIND_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  castmind_data:
```

启动服务：
```bash
# 创建.env文件
echo "OPENAI_API_KEY=your-key" > .env
echo "DEEPSEEK_API_KEY=your-key" >> .env
echo "KIMI_API_KEY=your-key" >> .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 3. 自定义Docker构建
创建 `Dockerfile`：
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.cargo/bin/uv /usr/local/bin/uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY requirements.txt ./
COPY src/ ./src/
COPY config/ ./config/
COPY castmind.py ./

# 安装依赖
RUN uv venv \
    && uv sync --frozen

# 创建非root用户
RUN useradd -m -u 1000 castmind \
    && chown -R castmind:castmind /app

USER castmind

EXPOSE 8000

CMD ["python", "castmind.py", "start"]
```

构建和运行：
```bash
# 构建镜像
docker build -t castmind:latest .

# 运行容器
docker run -d -p 8000:8000 castmind:latest
```

## ☸️ Kubernetes部署

### 1. 创建命名空间
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: castmind
```

### 2. 创建ConfigMap
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: castmind-config
  namespace: castmind
data:
  config.yaml: |
    environment: production
    log_level: info
    data_path: /data/castmind
```

### 3. 创建Secret
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: castmind-secrets
  namespace: castmind
type: Opaque
stringData:
  openai-api-key: "your-openai-key"
  deepseek-api-key: "your-deepseek-key"
  kimi-api-key: "your-kimi-key"
```

### 4. 创建Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: castmind
  namespace: castmind
spec:
  replicas: 3
  selector:
    matchLabels:
      app: castmind
  template:
    metadata:
      labels:
        app: castmind
    spec:
      containers:
      - name: castmind
        image: ghcr.io/yearsalso/castmind:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: castmind-secrets
              key: openai-api-key
        - name: CASTMIND_ENV
          value: "production"
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: castmind-config
      - name: data
        persistentVolumeClaim:
          claimName: castmind-data-pvc
```

### 5. 创建Service
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: castmind-service
  namespace: castmind
spec:
  selector:
    app: castmind
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 6. 创建Ingress（可选）
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: castmind-ingress
  namespace: castmind
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: castmind.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: castmind-service
            port:
              number: 80
```

### 7. 部署所有资源
```bash
# 应用所有配置
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# 查看部署状态
kubectl get all -n castmind

# 查看日志
kubectl logs -n castmind deployment/castmind -f
```

## ☁️ 云服务部署

### AWS部署

#### 使用ECS Fargate
```bash
# 创建ECR仓库
aws ecr create-repository --repository-name castmind

# 构建并推送镜像
docker build -t castmind .
docker tag castmind:latest <account-id>.dkr.ecr.<region>.amazonaws.com/castmind:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/castmind:latest

# 创建任务定义
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 创建服务
aws ecs create-service --cluster castmind-cluster --service-name castmind-service --task-definition castmind
```

#### 使用Elastic Beanstalk
```bash
# 初始化EB应用
eb init -p python-3.12 castmind

# 创建环境
eb create castmind-env

# 部署
eb deploy
```

### Google Cloud部署

#### 使用Cloud Run
```bash
# 构建镜像
gcloud builds submit --tag gcr.io/<project-id>/castmind

# 部署到Cloud Run
gcloud run deploy castmind \
  --image gcr.io/<project-id>/castmind \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure部署

#### 使用Container Instances
```bash
# 创建容器组
az container create \
  --resource-group castmind-rg \
  --name castmind-container \
  --image ghcr.io/yearsalso/castmind:latest \
  --ports 8000 \
  --environment-variables \
    OPENAI_API_KEY="your-key" \
    CASTMIND_ENV="production"
```

## 📊 监控与运维

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查就绪状态
curl http://localhost:8000/ready

# 检查指标
curl http://localhost:8000/metrics
```

### 日志管理
```bash
# 查看实时日志
docker logs -f castmind

# 查看Kubernetes日志
kubectl logs -n castmind deployment/castmind -f

# 日志轮转配置
# /etc/logrotate.d/castmind
/var/log/castmind/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 castmind castmind
}
```

### 性能监控
```bash
# 安装监控工具
pip install prometheus-client

# 查看性能指标
curl http://localhost:8000/metrics | grep castmind

# 使用Grafana仪表板
# 导入dashboard.json到Grafana
```

### 备份与恢复
```bash
# 备份数据
python castmind.py backup --output backup-$(date +%Y%m%d).tar.gz

# 恢复数据
python castmind.py restore --input backup-20240218.tar.gz

# 自动备份脚本
# scripts/backup.sh
#!/bin/bash
BACKUP_DIR="/backup/castmind"
DATE=$(date +%Y%m%d)
python /app/castmind.py backup --output $BACKUP_DIR/backup-$DATE.tar.gz
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## 🔒 安全配置

### 网络安全
```bash
# 配置防火墙
sudo ufw allow 8000/tcp
sudo ufw enable

# 使用HTTPS
# 配置Nginx反向代理
server {
    listen 443 ssl;
    server_name castmind.example.com;
    
    ssl_certificate /etc/ssl/certs/castmind.crt;
    ssl_certificate_key /etc/ssl/private/castmind.key;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 访问控制
```bash
# 配置API密钥认证
# config/.env
API_AUTH_ENABLED=true
API_KEYS=key1,key2,key3

# 使用请求头认证
curl -H "Authorization: Bearer your-api-key" \
  http://localhost:8000/api/v1/podcasts
```

## 🚨 故障排除

### 常见问题

#### 问题1：服务无法启动
**症状**: 端口被占用或依赖缺失
**解决**:
```bash
# 检查端口占用
sudo lsof -i :8000

# 检查依赖
python -c "import feedparser; print('feedparser OK')"
```

#### 问题2：内存不足
**症状**: 进程被OOM Killer终止
**解决**:
```bash
# 查看内存使用
free -h

# 调整内存限制
# docker-compose.yml
services:
  castmind:
    mem_limit: 2g
    mem_reservation: 1g
```

#### 问题3：网络连接失败
**症状**: 无法下载音频或访问API
**解决**:
```bash
# 测试网络连接
curl -I https://api.openai.com

# 检查代理设置
echo $http_proxy
echo $https_proxy
```

### 获取帮助
- **文档**: https://github.com/YearsAlso/castmind/docs
- **Issues**: https://github.com/YearsAlso/castmind/issues
- **Discussions**: https://github.com/YearsAlso/castmind/discussions

---

**最后更新**: 2026-02-18  
**部署版本**: v1.0.0