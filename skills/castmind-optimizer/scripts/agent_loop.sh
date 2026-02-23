#!/bin/bash
# CastMind Agent Loop Script
# 用于运行多次 agent session 进行代码优化

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

ARTIFACTS_DIR="$PROJECT_DIR/artifacts"
PROGRESS_FILE="$ARTIFACTS_DIR/CLAUDE_PROGRESS.md"
FEATURE_FILE="$ARTIFACTS_DIR/feature_list.json"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查 artifacts 目录
check_artifacts() {
    if [ ! -d "$ARTIFACTS_DIR" ]; then
        log_info "创建 artifacts 目录..."
        mkdir -p "$ARTIFACTS_DIR"
    fi
    
    if [ ! -f "$PROGRESS_FILE" ]; then
        log_warn "未找到进度文件，请先运行初始化"
        return 1
    fi
    
    if [ ! -f "$FEATURE_FILE" ]; then
        log_warn "未找到功能列表，请先运行初始化"
        return 1
    fi
}

# 显示当前状态
show_status() {
    log_info "=== 当前状态 ==="
    echo ""
    echo "--- Git 最近提交 ---"
    git log --oneline -5
    echo ""
    echo "--- 进度文件 ---"
    cat "$PROGRESS_FILE"
    echo ""
    echo "--- 功能列表 (未完成) ---"
    if command -v jq &> /dev/null; then
        jq '.[] | select(.passes == false) | "\(.category): \(.description)"' "$FEATURE_FILE" 2>/dev/null || echo "无"
    else
        grep '"passes": false' "$FEATURE_FILE" || echo "无"
    fi
}

# 验证环境
verify_environment() {
    log_info "验证开发环境..."
    
    # 检查后端
    if cd backend && python -c "import fastapi" 2>/dev/null; then
        log_info "Backend 依赖 OK"
    else
        log_warn "Backend 依赖可能有问题"
    fi
    
    # 检查前端
    if [ -d "frontend/node_modules" ]; then
        log_info "Frontend 依赖 OK"
    else
        log_warn "Frontend 依赖可能有问题"
    fi
    
    # 检查数据库
    if [ -f "data/castmind.db" ]; then
        log_info "数据库存在"
    else
        log_warn "数据库不存在，可能需要初始化"
    fi
}

# 运行 lint
run_lint() {
    log_info "运行代码检查..."
    
    # Backend lint
    if command -v ruff &> /dev/null; then
        cd "$PROJECT_DIR/backend"
        ruff check . --fix || true
    fi
    
    # Frontend lint
    if [ -d "$PROJECT_DIR/frontend" ] && command -v pnpm &> /dev/null; then
        cd "$PROJECT_DIR/frontend"
        pnpm lint 2>/dev/null || true
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # Backend tests
    if [ -d "$PROJECT_DIR/tests" ]; then
        cd "$PROJECT_DIR"
        python -m pytest tests/ -v --tb=short 2>/dev/null || log_warn "测试执行有问题"
    fi
}

# 选择下一个功能
pick_next_feature() {
    log_info "选择下一个功能..."
    
    if command -v jq &> /dev/null; then
        jq -r '.[] | select(.passes == false) | .description' "$FEATURE_FILE" | head -1
    else
        log_warn "需要 jq 来选择功能"
        echo "请手动查看 $FEATURE_FILE"
    fi
}

# 主菜单
main_menu() {
    while true; do
        echo ""
        echo "======================================"
        echo "     CastMind Agent Loop Menu"
        echo "======================================"
        echo "1. 显示当前状态"
        echo "2. 验证环境"
        echo "3. 运行 Lint"
        echo "4. 运行测试"
        echo "5. 选择下一个功能"
        echo "6. 初始化项目 (仅第一次)"
        echo "q. 退出"
        echo ""
        read -p "选择: " choice
        
        case $choice in
            1) show_status ;;
            2) verify_environment ;;
            3) run_lint ;;
            4) run_tests ;;
            5) 
                feature=$(pick_next_feature)
                log_info "下一个功能: $feature"
                ;;
            6) 
                log_info "初始化项目..."
                # 创建初始化脚本
                cat > "$PROGRESS_FILE" << 'EOF'
# CastMind 开发进度

## 当前状态: 初始化完成

## 待完成
请查看 feature_list.json
EOF
                log_info "初始化完成，请编辑 feature_list.json 添加功能"
                ;;
            q|Q) break ;;
            *) log_error "无效选择" ;;
        esac
    done
}

# 解析参数
case "${1:-}" in
    status)
        check_artifacts
        show_status
        ;;
    verify)
        verify_environment
        ;;
    lint)
        run_lint
        ;;
    test)
        run_tests
        ;;
    next)
        pick_next_feature
        ;;
    init)
        mkdir -p "$ARTIFACTS_DIR"
        log_info "初始化完成"
        ;;
    *)
        # 如果不是第一次运行，显示菜单
        if ! check_artifacts 2>/dev/null; then
            log_info "项目未初始化，使用 'init' 命令初始化"
        fi
        main_menu
        ;;
esac
