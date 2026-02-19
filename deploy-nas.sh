#!/bin/bash
# 🏠 CastMind NAS 专用部署脚本
# 版本: 1.0.0
# 描述: 一键部署 CastMind 到家庭 NAS 服务器

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示横幅
show_banner() {
    cat << "EOF"
    
    ███╗   ██╗ █████╗ ███████╗
    ████╗  ██║██╔══██╗██╔════╝
    ██╔██╗ ██║███████║███████╗
    ██║╚██╗██║██╔══██║╚════██║
    ██║ ╚████║██║  ██║███████║
    ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
    
    🎧 CastMind NAS 部署版 🏠
    
EOF
}

# 检查 NAS 环境
check_nas_environment() {
    log_info "检查 NAS 环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先在 NAS 上安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先在 NAS 上安装 Docker Compose"
        exit 1
    fi
    
    # 检查 Docker 服务状态
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行，请启动 Docker"
        exit 1
    fi
    
    # 检查存储空间
    local available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 5 ]; then
        log_warning "可用存储空间不足 (${available_space}G)，建议至少 5G"
    fi
    
    # 检查内存
    local total_memory=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$total_memory" -lt 1024 ]; then
        log_warning "系统内存较小 (${total_memory}MB)，建议至少 1GB"
    fi
    
    # 检查环境变量文件
    if [ ! -f .env ]; then
        log_warning "未找到 .env 文件"
        read -p "是否从模板创建 .env 文件？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ -f .env.template ]; then
                cp .env.template .env
                log_success "已创建 .env 文件，请编辑配置"
                log_info "请编辑 .env 文件后重新运行部署脚本"
                exit 0
            else
                log_error "未找到 .env.template 文件"
                exit 1
            fi
        else
            log_error "需要 .env 文件才能继续部署"
            exit 1
        fi
    fi
    
    # 检查必要环境变量
    if [ -z "$OPENAI_API_KEY" ]; then
        log_error "请在 .env 文件中设置 OPENAI_API_KEY"
        exit 1
    fi
    
    # 检查 Obsidian 路径
    if [ -n "$OBSIDIAN_VAULT" ] && [ ! -d "$OBSIDIAN_VAULT" ]; then
        log_warning "Obsidian 仓库路径不存在: $OBSIDIAN_VAULT"
        read -p "是否创建此目录？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mkdir -p "$OBSIDIAN_VAULT/Podcasts/CastMind"
            log_success "已创建 Obsidian 目录结构"
        fi
    fi
    
    log_success "NAS 环境检查通过"
}

# 创建 NAS 专用目录结构
create_nas_directories() {
    log_info "创建 NAS 专用目录结构..."
    
    # 基础目录
    local base_dirs=("data" "logs" "config" "backups" "monitoring")
    
    for dir in "${base_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "  创建目录: $dir"
        fi
    done
    
    # 创建数据子目录
    local data_subdirs=("transcripts" "summaries" "notes" "metadata" "database")
    
    for subdir in "${data_subdirs[@]}"; do
        local full_path="data/$subdir"
        if [ ! -d "$full_path" ]; then
            mkdir -p "$full_path"
            log_info "  创建数据子目录: $full_path"
        fi
    done
    
    # 设置权限（NAS 通常需要特定权限）
    chmod -R 755 data logs config
    chmod 644 config/* 2>/dev/null || true
    
    log_success "目录结构创建完成"
}

# 创建 NAS 监控配置
create_nas_monitoring() {
    log_info "创建 NAS 监控配置..."
    
    # 创建监控目录
    mkdir -p monitoring/html
    
    # 创建 nginx 配置
    cat > monitoring/nginx.conf << 'EOF'
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    keepalive_timeout 65;

    server {
        listen 80;
        server_name localhost;

        location / {
            root /usr/share/nginx/html;
            index index.html;
        }

        location /api/ {
            proxy_pass http://castmind-nas:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /health {
            proxy_pass http://castmind-nas:8000/api/v1/health;
            proxy_set_header Host $host;
        }
    }
}
EOF
    
    # 创建监控页面
    cat > monitoring/html/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎧 CastMind NAS 监控面板</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            color: #4a5568;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #718096;
            font-size: 1.2rem;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .status-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-5px);
        }
        
        .card-title {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            color: #4a5568;
            font-size: 1.3rem;
        }
        
        .card-title i {
            margin-right: 10px;
            font-size: 1.5rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-up { background: #48bb78; }
        .status-down { background: #f56565; }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: #f7fafc;
            border-radius: 10px;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4a5568;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #718096;
            margin-top: 5px;
        }
        
        .actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        
        .btn {
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: #4299e1;
            color: white;
        }
        
        .btn-primary:hover {
            background: #3182ce;
        }
        
        .btn-secondary {
            background: #e2e8f0;
            color: #4a5568;
        }
        
        .btn-secondary:hover {
            background: #cbd5e0;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            color: #718096;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .status-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎧 CastMind NAS 监控面板</h1>
            <p class="subtitle">播客智能处理系统 - 家庭服务器版</p>
        </header>
        
        <div class="status-grid">
            <div class="status-card">
                <div class="card-title">
                    <span class="status-indicator status-up"></span>
                    CastMind 服务状态
                </div>
                <div id="service-status">正在检查...</div>
            </div>
            
            <div class="status-card">
                <div class="card-title">
                    <span class="status-indicator status-up"></span>
                    Redis 服务状态
                </div>
                <div id="redis-status">正在检查...</div>
            </div>
            
            <div class="status-card">
                <div class="card-title">
                    📊 系统统计
                </div>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value" id="processed-count">0</div>
                        <div class="stat-label">已处理播客</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="storage-usage">0 GB</div>
                        <div class="stat-label">存储使用</div>
                    </div>
                </div>
            </div>
            
            <div class="status-card">
                <div class="card-title">
                    ⏰ 最近活动
                </div>
                <div id="recent-activity">
                    <p>正在加载活动记录...</p>
                </div>
            </div>
        </div>
        
        <div class="actions">
            <a href="/api/docs" class="btn btn-primary" target="_blank">📚 API 文档</a>
            <a href="http://localhost:8000" class="btn btn-secondary" target="_blank">🔧 管理界面</a>
            <button onclick="processPodcasts()" class="btn btn-primary">🎧 立即处理播客</button>
            <button onclick="backupData()" class="btn btn-secondary">💾 备份数据</button>
        </div>
        
        <footer>
            <p>© 2026 CastMind NAS 版 | 版本 1.0.0 | 最后更新: <span id="last-update">正在加载...</span></p>
        </footer>
    </div>
    
    <script>
        // 更新状态
        async function updateStatus() {
            try {
                // 检查服务状态
                const healthRes = await fetch('/health');
                if (healthRes.ok) {
                    document.getElementById('service-status').innerHTML = 
                        '<span style="color: #48bb78;">✅ 服务运行正常</span>';
                } else {
                    document.getElementById('service-status').innerHTML = 
                        '<span style="color: #f56565;">❌ 服务异常</span>';
                }
                
                // 更新统计信息（这里需要后端 API 支持）
                // 在实际部署中，需要实现对应的 API 端点
                
                // 更新最后更新时间
                document.getElementById('last-update').textContent = new Date().toLocaleString();
                
            } catch (error) {
                console.error('状态更新失败:', error);
                document.getElementById('service-status').innerHTML = 
                    '<span style="color: #f56565;">❌ 连接失败</span>';
            }
        }
        
        // 处理播客
        async function processPodcasts() {
            try {
                const response = await fetch('/api/v1/tasks/process-podcasts', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    alert('✅ 播客处理任务已启动');
                } else {
                    alert('❌ 任务启动失败');
                }
            } catch (error) {
                console.error('处理失败:', error);
                alert('❌ 请求失败，请检查网络连接');
            }
        }
        
        // 备份数据
        async function backupData() {
            try {
                const response = await fetch('/api/v1/backup', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    alert('✅ 数据备份任务已启动');
                } else {
                    alert('❌ 备份失败');
                }
            } catch (error) {
                console.error('备份失败:', error);
                alert('❌ 请求失败，请检查网络连接');
            }
        }
        
        // 页面加载时更新状态
        document.addEventListener('DOMContentLoaded', () => {
            updateStatus();
            // 每30秒更新一次状态
            setInterval(updateStatus, 30000);
        });
    </script>
</body>
</html>
EOF
    
    log_success "监控配置创建完成"
}

# 部署 NAS 服务
deploy_nas_services() {
    log_info "开始部署 NAS 服务..."
    
    # 使用 NAS 专用配置
    if [ -f "docker-compose.nas.yml" ]; then
        log_info "使用 NAS 专用配置"
        COMPOSE_FILE="docker-compose.nas.yml"
    else
        log_warning "未找到 NAS 专用配置，使用标准配置"
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建 Docker 镜像..."
    docker-compose -f $COMPOSE_FILE build --target production
    
    # 启动服务
    log_info "启动服务..."
    docker-compose -f $COMPOSE_FILE up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15
    
    # 检查服务状态
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        docker-compose -f $COMPOSE_FILE logs
        exit 1
    fi
}

# 显示部署信息
show_nas_deployment_info() {
    local host_port=${HOST_PORT:-8000}
    local monitor_port=${MONITOR_PORT:-8080}
    
    cat << EOF

🎉 CastMind NAS 部署完成！

📊 服务信息:
   主服务地址: http://localhost:${host_port}
   监控面板: http://localhost:${monitor_port}
   API 文档: http://localhost:${host_port}/docs
   健康检查: http://localhost:${host_port}/api/v1/health

📁 数据目录:
   数据文件: $(pwd)/data
   日志文件: $(pwd)/logs
   配置文件: $(pwd)/config
   备份文件: $(pwd)/backups

🔧 管理命令:
   查看日志: docker-compose -f docker-compose.nas.yml logs -f
   停止服务: docker-compose -f docker-compose.nas.yml down
   重启服务: docker-compose -f docker-compose.nas.yml restart
   更新服务: ./deploy-nas.sh --update

📈 监控信息:
   服务状态: docker-compose -f docker-compose.nas.yml ps
   资源使用: docker stats
   容器日志: docker logs castmind-nas

🚀 定时任务:
   每30分钟: 自动处理播客
   每天03:00: 自动数据备份
   每周一03:00: 清理旧文件

💡 NAS 专用提示:
   • 首次使用需要配置播客订阅
   • 检查 .env 文件中的 Obsidian 路径
   • 确保 NAS 有足够的存储空间
   • 建议设置定期备份

🔒 安全建议:
   • 修改默认密码 (REDIS_PASSWORD)
   • 定期更新 Docker 镜像
   • 监控系统资源使用
   • 定期检查日志文件

📞 故障排除:
   1. 服务无法启动: 查看日志 docker-compose logs
   2. 存储空间不足: 清理旧备份文件
   3. 网络连接问题: 检查 NAS 防火墙设置
   4. AI 服务失败: 验证 API Key 配置

EOF
}

# 更新 NAS 服务
update_nas_services() {
    log_info "更新 NAS 服务..."
    
    # 拉取最新代码
    git pull
    
    # 重新构建镜像
    docker-compose -f docker-compose.nas.yml build --target production
    
    # 重启服务
    docker-compose -f docker-compose.nas.yml down
    deploy_nas_services
    
    log_success "NAS 服务更新完成"
}

# 显示帮助
show_nas_help() {
    cat << EOF
🏠 CastMind NAS 部署脚本

用法: $0 [选项]

选项:
    --help          显示此帮助信息
    --update        更新 NAS 服务
    --backup        备份 NAS 数据
    --monitor       启动监控面板
    --info          显示部署信息
    --logs          查看服务日志
    --stop          停止 NAS 服务
    --start         启动 NAS 服务
    --restart       重启 NAS 服务

示例:
    $0              标准 NAS 部署
    $0 --update     更新 NAS 服务
    $0 --backup     备份 NAS 数据
    $0 --info       显示部署信息

NAS 要求:
    • Docker 20.10+
    • Docker Compose 2.0+
    • 至少 1GB 可用内存
    • 至少 5GB 磁盘空间
    • 稳定的网络连接

配置文件:
    • .env          环境变量配置
    • docker-compose.nas.yml NAS 专用配置

支持的系统:
    • 群晖 DSM 7.0+
    • 威联通 QTS 5.0+
    • Unraid 6.9+
    • TrueNAS Scale
    • 其他 Linux NAS 系统

EOF
}

# 主函数
main() {
    show_banner
    
    case "$1" in
        --help)
            show_nas_help
            ;;
        --update)
            check_nas_environment
            update_nas_services
            show_nas_deployment_info
            ;;
        --backup)
            log_info "备份 NAS 数据..."
            # 这里可以添加备份逻辑
            log_success "备份功能待实现"
            ;;
        --monitor)
            log_info "启动监控面板..."
            docker-compose -f docker-compose.nas.yml up -d castmind-monitor
            log_success "监控面板已启动"
            ;;
        --info)
            show_nas_deployment_info
            ;;
        --logs)
            docker-compose -f docker-compose.nas.yml logs -f
            ;;
        --stop)
            docker-compose -f docker-compose.nas.yml down
            log_success "NAS 服务已停止"
            ;;
        --start)
            deploy_nas_services
            show_nas_deployment_info
            ;;
        --restart)
            docker-compose -f docker-compose.nas.yml restart
            log_success "NAS 服务已重启"
            ;;
        *)
            check_nas_environment
            create_nas_directories
            create_nas_monitoring
            deploy_nas_services
            show_nas_deployment_info
            ;;
    esac
}

# 加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 执行主函数
main "$@"