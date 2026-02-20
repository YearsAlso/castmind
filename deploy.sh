#!/bin/bash
# 🚀 CastMind 部署脚本
# 版本: 1.0.0
# 描述: 一键部署 CastMind 到 Docker 环境

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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 '$1' 未找到，请先安装"
        exit 1
    fi
}

# 显示横幅
show_banner() {
    cat << "EOF"
    
    ██████╗ █████╗ ███████╗████████╗███╗   ███╗██╗███╗   ██╗██████╗ 
    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝████╗ ████║██║████╗  ██║██╔══██╗
    ██║     ███████║███████╗   ██║   ██╔████╔██║██║██╔██╗ ██║██║  ██║
    ██║     ██╔══██║╚════██║   ██║   ██║╚██╔╝██║██║██║╚██╗██║██║  ██║
    ╚██████╗██║  ██║███████║   ██║   ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
     ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ 
    
    🎧 播客智能处理系统 🚀
    
EOF
}

# 检查环境
check_environment() {
    log_info "检查部署环境..."
    
    # 检查必要命令
    check_command docker
    check_command docker-compose
    
    # 检查 Docker 服务状态
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行，请启动 Docker"
        exit 1
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
    
    log_success "环境检查通过"
}

# 构建镜像
build_images() {
    log_info "开始构建 Docker 镜像..."
    
    # 构建生产镜像
    docker-compose build --target production
    
    # 构建开发镜像（可选）
    if [ "$1" == "--dev" ]; then
        log_info "构建开发镜像..."
        docker-compose build --target development
    fi
    
    log_success "Docker 镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动 CastMind 服务..."
    
    # 启动所有服务
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        docker-compose logs
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_retries=30
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s -f http://localhost:${HOST_PORT:-8000}/api/v1/health > /dev/null 2>&1; then
            log_success "健康检查通过"
            return 0
        fi
        
        log_info "等待服务就绪... ($((retry_count + 1))/$max_retries)"
        sleep 5
        ((retry_count++))
    done
    
    log_error "健康检查失败，服务未在指定时间内就绪"
    docker-compose logs
    return 1
}

# 显示部署信息
show_deployment_info() {
    local host_port=${HOST_PORT:-8000}
    
    cat << EOF

🎉 CastMind 部署完成！

📊 服务信息:
   服务地址: http://localhost:${host_port}
   API 文档: http://localhost:${host_port}/docs
   健康检查: http://localhost:${host_port}/api/v1/health

📁 数据目录:
   数据文件: $(pwd)/data
   日志文件: $(pwd)/logs
   配置文件: $(pwd)/config

🔧 管理命令:
   查看日志: docker-compose logs -f
   停止服务: docker-compose down
   重启服务: docker-compose restart
   更新服务: ./deploy.sh --update

📈 监控信息:
   Redis 监控: docker exec -it castmind-redis redis-cli info
   服务状态: docker-compose ps
   资源使用: docker stats

🚀 下一步:
   1. 访问 http://localhost:${host_port}/docs 查看 API 文档
   2. 配置定时任务处理播客
   3. 查看日志确认服务运行正常

💡 提示:
   • 首次使用需要配置播客订阅
   • 检查 .env 文件中的 AI 配置
   • 定期备份数据目录

EOF
}

# 更新服务
update_services() {
    log_info "更新 CastMind 服务..."
    
    # 拉取最新代码
    git pull
    
    # 重新构建镜像
    build_images
    
    # 重启服务
    docker-compose down
    start_services
    
    log_success "服务更新完成"
}

# 备份数据
backup_data() {
    local backup_dir="./backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/castmind_backup_${timestamp}.tar.gz"
    
    log_info "备份数据..."
    
    mkdir -p "$backup_dir"
    
    # 备份数据目录
    tar -czf "$backup_file" \
        --exclude="*.log" \
        --exclude="*.tmp" \
        ./data ./config .env
    
    # 保留最近7天的备份
    find "$backup_dir" -name "castmind_backup_*.tar.gz" -mtime +7 -delete
    
    log_success "数据备份完成: $backup_file"
    log_info "备份文件大小: $(du -h "$backup_file" | cut -f1)"
}

# 恢复数据
restore_data() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        echo "用法: $0 --restore <备份文件>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log_info "恢复数据从: $backup_file"
    
    # 停止服务
    docker-compose down
    
    # 恢复数据
    tar -xzf "$backup_file" -C ./
    
    # 启动服务
    start_services
    
    log_success "数据恢复完成"
}

# 显示帮助
show_help() {
    cat << EOF
🚀 CastMind 部署脚本

用法: $0 [选项]

选项:
    --help          显示此帮助信息
    --dev           开发模式部署
    --update        更新服务
    --backup        备份数据
    --restore FILE  从备份恢复数据
    --info          显示部署信息
    --logs          查看服务日志
    --stop          停止服务
    --start         启动服务
    --restart       重启服务

示例:
    $0              标准部署
    $0 --dev        开发模式部署
    $0 --update     更新服务
    $0 --backup     备份数据
    $0 --info       显示部署信息

环境要求:
    • Docker 20.10+
    • Docker Compose 2.0+
    • 至少 2GB 可用内存
    • 至少 5GB 磁盘空间

配置文件:
    • .env          环境变量配置
    • docker-compose.yml Docker 编排配置

EOF
}

# 主函数
main() {
    show_banner
    
    case "$1" in
        --help)
            show_help
            ;;
        --dev)
            check_environment
            build_images --dev
            start_services
            health_check
            show_deployment_info
            ;;
        --update)
            check_environment
            update_services
            health_check
            show_deployment_info
            ;;
        --backup)
            backup_data
            ;;
        --restore)
            restore_data "$2"
            ;;
        --info)
            show_deployment_info
            ;;
        --logs)
            docker-compose logs -f
            ;;
        --stop)
            docker-compose down
            log_success "服务已停止"
            ;;
        --start)
            start_services
            health_check
            show_deployment_info
            ;;
        --restart)
            docker-compose restart
            log_success "服务已重启"
            ;;
        *)
            check_environment
            build_images
            start_services
            health_check
            show_deployment_info
            ;;
    esac
}

# 加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 执行主函数
main "$@"