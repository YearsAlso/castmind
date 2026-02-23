#!/bin/bash
# CastMind Agent Loop Script
# 基于 Anthropic "Effective Harnesses for Long-Running Agents" 设计
# 双 Agent 架构：Initializer + Coding Agent

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(cd "$SKILL_DIR/.." && pwd)"

ARTIFACTS_DIR="$SKILL_DIR/artifacts"
PROGRESS_FILE="$ARTIFACTS_DIR/CLAUDE_PROGRESS.md"
FEATURE_FILE="$ARTIFACTS_DIR/feature_list.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_phase() { echo -e "${CYAN}[PHASE]${NC} $1"; }

check_dependencies() {
    if ! command -v jq &> /dev/null; then
        log_error "需要 jq，请先安装: brew install jq"
        exit 1
    fi
}

get_pending_count() {
    jq '[.[] | select(.passes == false)] | length' "$FEATURE_FILE"
}

get_completed_count() {
    jq '[.[] | select(.passes == true)] | length' "$FEATURE_FILE"
}

update_feature_status() {
    local description="$1"
    local status="$2"
    local tmp_file="/tmp/feature_list_tmp.json"
    
    jq --arg desc "$description" --argjson status "$status" \
        'map(if .description == $desc then .passes = $status else . end)' \
        "$FEATURE_FILE" > "$tmp_file" && mv "$tmp_file" "$FEATURE_FILE"
}

log_progress() {
    local phase="$1"
    local message="$2"
    
    {
        echo ""
        echo "### $(date '+%Y-%m-%d %H:%M') - $phase"
        echo "$message"
    } >> "$PROGRESS_FILE"
}

check_git_status() {
    cd "$PROJECT_DIR"
    
    if [ -d ".git" ]; then
        local status=$(git status --porcelain)
        if [ -n "$status" ]; then
            log_warn "有未提交的更改:"
            echo "$status"
            return 1
        fi
        log_info "Git 状态干净"
        return 0
    else
        log_warn "不是 Git 仓库"
        return 1
    fi
}

commit_changes() {
    local description="$1"
    
    cd "$PROJECT_DIR"
    
    if [ -d ".git" ]; then
        git add -A
        if git diff --cached --quiet; then
            log_info "没有需要提交的更改"
            return 0
        fi
        
        local commit_msg="feat: $description"
        
        if git commit -m "$commit_msg"; then
            log_info "已提交: $commit_msg"
            return 0
        else
            log_error "提交失败"
            return 1
        fi
    fi
}

# ============================================
# PHASE 1: 了解现状 (Understand Current State)
# ============================================
phase_understand() {
    log_phase "=== 阶段 1: 了解现状 ==="
    
    cd "$PROJECT_DIR"
    
    echo ""
    log_step "1. 检查工作目录..."
    echo "  目录: $(pwd)"
    
    echo ""
    log_step "2. 查看 Git 历史 (最近 5 次提交)..."
    if [ -d ".git" ]; then
        git log --oneline -5
    else
        echo "  非 Git 仓库"
    fi
    
    echo ""
    log_step "3. 查看进度记录..."
    if [ -f "$PROGRESS_FILE" ]; then
        echo "--- 最近进度 ---"
        tail -15 "$PROGRESS_FILE"
    else
        echo "  无进度记录"
    fi
    
    echo ""
    log_step "4. 查看待办任务..."
    local pending=$(get_pending_count)
    local completed=$(get_completed_count)
    echo "  已完成: $completed"
    echo "  待完成: $pending"
    
    echo ""
    echo "--- 优先级最高的待办 ---"
    jq -r '.[] | select(.passes == false) | "[P\(.priority)] \(.category): \(.description)"' "$FEATURE_FILE" | head -3
    
    log_phase "现状了解完成"
}

# ============================================
# PHASE 2: 验证基线 (Verify Baseline)
# ============================================
phase_verify_baseline() {
    log_phase "=== 阶段 2: 验证基线 ==="
    
    cd "$PROJECT_DIR"
    
    echo ""
    log_step "1. 检查 Git 状态..."
    check_git_status || true
    
    echo ""
    log_step "2. 检查依赖..."
    
    if [ -d "backend" ]; then
        cd backend
        if python -c "import fastapi" 2>/dev/null; then
            log_info "  Backend 依赖 OK"
        else
            log_warn "  Backend 依赖可能有问题"
        fi
        cd "$PROJECT_DIR"
    fi
    
    if [ -d "frontend/node_modules" ]; then
        log_info "  Frontend 依赖 OK"
    else
        log_warn "  Frontend 依赖可能有问题"
    fi
    
    echo ""
    log_step "3. 运行快速测试..."
    local test_passed=true
    
    if [ -d "tests" ]; then
        if python -m pytest tests/ -v --tb=short -x 2>&1 | tail -10; then
            log_info "  后端测试通过"
        else
            log_warn "  后端测试失败"
            test_passed=false
        fi
    fi
    
    cd "$PROJECT_DIR"
    
    log_phase "基线验证完成"
    
    if [ "$test_passed" = false ]; then
        log_warn "基线测试失败，是否继续?"
        read -p "继续? (y/n): " confirm
        [ "$confirm" != "y" ] && exit 1
    fi
}

# ============================================
# PHASE 3: 实现功能 (Implement Feature)
# ============================================
phase_implement() {
    local description="$1"
    local category="$2"
    local steps="$3"
    
    log_phase "=== 阶段 3: 实现功能 ==="
    
    log_step "任务: $description"
    echo ""
    echo "步骤:"
    echo "$steps"
    echo ""
    
    log_step "启动 opencode 进行实现..."
    echo ""
    echo "请在 opencode 中执行以下任务:"
    echo ""
    echo "## 任务描述"
    echo "$description"
    echo ""
    echo "## 具体步骤"
    echo "$steps"
    echo ""
    
    opencode "请执行以下任务：
    
## 任务描述
$description

## 具体步骤
$steps

## 重要提醒
1. 每完成一个步骤后进行验证
2. 确保代码可以正常运行
3. 遵循项目现有的代码规范
4. 不要引入新的 lint 错误
"
    
    log_phase "功能实现完成"
}

# ============================================
# PHASE 4: 记录收尾 (Record & Cleanup)
# ============================================
phase_record() {
    local description="$1"
    local test_passed="$2"
    local lint_passed="$3"
    
    log_phase "=== 阶段 4: 记录收尾 ==="
    
    cd "$PROJECT_DIR"
    
    echo ""
    log_step "1. 运行完整测试..."
    local full_test_passed=false
    
    if run_tests; then
        log_info "测试通过 ✓"
        full_test_passed=true
    else
        log_warn "测试失败"
    fi
    
    echo ""
    log_step "2. 运行 Lint 检查..."
    local full_lint_passed=false
    
    if run_lint; then
        log_info "Lint 通过 ✓"
        full_lint_passed=true
    else
        log_warn "Lint 有警告"
        full_lint_passed=true
    fi
    
    echo ""
    log_step "3. 检查 Git 状态..."
    local needs_commit=false
    
    if [ -d ".git" ]; then
        local status=$(git status --porcelain)
        if [ -n "$status" ]; then
            log_info "有更改需要提交"
            echo "$status"
            needs_commit=true
        else
            log_info "没有代码更改"
        fi
    fi
    
    echo ""
    log_step "4. 提交代码..."
    if [ "$needs_commit" = true ]; then
        if [ "$full_test_passed" = true ]; then
            commit_changes "$description"
        else
            log_warn "测试未通过，暂不提交"
        fi
    fi
    
    echo ""
    log_step "5. 更新进度..."
    log_progress "Coding Agent" "- 任务: $description
  - 测试: $([ "$full_test_passed" = true ] && echo "通过" || echo "失败")
  - Lint: $([ "$full_lint_passed" = true ] && echo "通过" || echo "警告")
  - 提交: $([ "$needs_commit" = true ] && echo "是" || echo "否")"
    
    echo ""
    log_step "6. 标记任务完成?"
    echo "  [y] 是 - 标记为完成并继续下一个"
    echo "  [n] 否 - 保留为待办"
    echo "  [q] 退出"
    read -p "选择 [y/n/q]: " confirm
    
    case "$confirm" in
        y|Y)
            update_feature_status "$description" "true"
            log_info "任务已标记为完成"
            return 0
            ;;
        n|N)
            log_warn "任务保留为未完成"
            return 1
            ;;
        q|Q)
            echo "退出脚本"
            exit 0
            ;;
    esac
}

run_tests() {
    cd "$PROJECT_DIR"
    
    local all_passed=true
    
    if [ -d "tests" ]; then
        if ! python -m pytest tests/ -v --tb=short 2>&1; then
            all_passed=false
        fi
    fi
    
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        cd frontend
        if ! pnpm test -- --run 2>&1; then
            all_passed=false
        fi
        cd "$PROJECT_DIR"
    fi
    
    $all_passed
}

run_lint() {
    cd "$PROJECT_DIR"
    
    local all_passed=true
    
    if command -v ruff &> /dev/null && [ -d "backend" ]; then
        cd backend
        if ! ruff check . 2>&1; then
            all_passed=false
        fi
        cd "$PROJECT_DIR"
    fi
    
    if command -v pnpm &> /dev/null && [ -d "frontend" ]; then
        cd frontend
        if ! pnpm lint 2>&1; then
            all_passed=false
        fi
        cd "$PROJECT_DIR"
    fi
    
    $all_passed
}

get_next_feature() {
    jq -r '.[] | select(.passes == false) | @json' "$FEATURE_FILE" | head -1
}

show_feature() {
    local feature="$1"
    
    local description=$(echo "$feature" | jq -r '.description')
    local category=$(echo "$feature" | jq -r '.category')
    local priority=$(echo "$feature" | jq -r '.priority')
    local ux_impact=$(echo "$feature" | jq -r '.ux_impact')
    local reason=$(echo "$feature" | jq -r '.reason')
    local steps=$(echo "$feature" | jq -r '.steps | join("
")')
    
    echo ""
    echo "========================================"
    echo "  下一个任务"
    echo "========================================"
    echo "优先级: P$priority"
    echo "类别: $category"
    echo "UX影响: $ux_impact"
    echo "----------------------------------------"
    echo "描述: $description"
    echo "原因: $reason"
    echo "----------------------------------------"
    echo "步骤:"
    echo "$steps"
    echo "========================================"
    echo ""
}

main_loop() {
    check_dependencies
    
    if [ ! -f "$FEATURE_FILE" ]; then
        log_error "未找到 feature_list.json: $FEATURE_FILE"
        exit 1
    fi
    
    local total=$(jq 'length' "$FEATURE_FILE")
    local pending=$(get_pending_count)
    local completed=$(get_completed_count)
    
    log_info "========================================"
    log_info "  CastMind Agent Loop"
    log_info "  基于 Anthropic Long-Running Agents"
    log_info "========================================"
    echo ""
    log_info "总任务: $total | 已完成: $completed | 待办: $pending"
    
    if [ "$pending" -eq 0 ]; then
        log_info "所有任务已完成! 🎉"
        exit 0
    fi
    
    echo ""
    read -p "开始执行下一个任务? (y/n/q): " confirm
    
    case "$confirm" in
        q|Q) exit 0 ;;
        n|N) 
            log_info "退出"
            exit 0
            ;;
    esac
    
    local feature=$(get_next_feature)
    
    if [ -z "$feature" ] || [ "$feature" = "null" ]; then
        log_info "没有待办任务"
        exit 0
    fi
    
    local description=$(echo "$feature" | jq -r '.description')
    local category=$(echo "$feature" | jq -r '.category')
    local steps=$(echo "$feature" | jq -r '.steps | join("
")')
    
    show_feature "$feature"
    
    echo ""
    read -p "确认执行此任务? (y/n): " confirm
    [ "$confirm" != "y" ] && exit 0
    
    phase_understand
    
    phase_verify_baseline
    
    phase_implement "$description" "$category" "$steps"
    
    phase_record "$description"
    
    local remaining=$(get_pending_count)
    log_info "剩余任务: $remaining"
    
    if [ "$remaining" -eq 0 ]; then
        log_info "所有任务已完成! 🎉"
    else
        echo ""
        read -p "继续执行下一个任务? (y/n): " confirm
        [ "$confirm" = "y" ] && main_loop
    fi
}

show_status() {
    log_info "=== 当前状态 ==="
    echo ""
    
    cd "$PROJECT_DIR"
    
    echo "--- Git 最近提交 ---"
    git log --oneline -5 2>/dev/null || echo "非 Git 仓库"
    echo ""
    
    echo "--- 进度统计 ---"
    echo "已完成: $(get_completed_count)"
    echo "待完成: $(get_pending_count)"
    echo ""
    
    echo "--- 进度记录 ---"
    if [ -f "$PROGRESS_FILE" ]; then
        tail -20 "$PROGRESS_FILE"
    else
        echo "无"
    fi
    echo ""
    
    echo "--- 待办任务 ---"
    jq -r '.[] | select(.passes == false) | "[P\(.priority)] \(.category): \(.description)"' "$FEATURE_FILE"
    echo ""
    
    echo "--- 已完成任务 ---"
    jq -r '.[] | select(.passes == true) | "[P\(.priority)] \(.category): \(.description)"' "$FEATURE_FILE"
}

show_help() {
    echo "CastMind Agent Loop - 使用帮助"
    echo ""
    echo "基于 Anthropic 'Effective Harnesses for Long-Running Agents'"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  run       - 开始执行任务 (四阶段工作流)"
    echo "  status    - 显示当前状态"
    echo "  next      - 显示下一个待办任务"
    echo "  list      - 列出所有任务"
    echo "  pending   - 显示待办任务"
    echo "  completed - 显示已完成任务"
    echo "  test      - 运行测试"
    echo "  lint      - 运行 Lint"
    echo "  help      - 显示帮助"
    echo ""
    echo "四阶段工作流:"
    echo "  1. 了解现状 - 读取 Git 历史、进度文件"
    echo "  2. 验证基线 - 运行测试确保环境正常"
    echo "  3. 实现功能 - 调用 opencode 执行任务"
    echo "  4. 记录收尾 - 测试、提交、更新进度"
    echo ""
}

case "${1:-run}" in
    run)
        main_loop
        ;;
    status)
        show_status
        ;;
    next)
        feature=$(get_next_feature)
        if [ -n "$feature" ] && [ "$feature" != "null" ]; then
            show_feature "$feature"
        else
            log_info "没有待办任务"
        fi
        ;;
    list)
        jq -r '.[] | "[P\(.priority)] [\(.category)] \(.description)"' "$FEATURE_FILE"
        ;;
    pending)
        jq -r '.[] | select(.passes == false) | "[P\(.priority)] \(.description)"' "$FEATURE_FILE"
        ;;
    completed)
        jq -r '.[] | select(.passes == true) | "[P\(.priority)] \(.description)"' "$FEATURE_FILE"
        ;;
    test)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
