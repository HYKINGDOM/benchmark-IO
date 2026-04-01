#!/bin/bash

# ==================== 百万级数据导出跨语言性能基准测试系统 ====================
# 一键启动脚本
# 作者: DevOps Architect
# 版本: 1.0.0
# ==============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

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

# 显示帮助信息
show_help() {
    cat << EOF
百万级数据导出跨语言性能基准测试系统 - 一键启动脚本

用法: $0 [命令] [选项]

命令:
    start               启动所有服务（默认）
    stop                停止所有服务
    restart             重启所有服务
    status              查看服务状态
    logs                查看服务日志
    build               构建所有服务镜像
    clean               清理所有容器和卷
    generate-data       生成测试数据
    quick-start         快速启动（仅启动核心服务）
    monitor             仅启动监控服务
    help                显示帮助信息

选项:
    -s, --service       指定服务名称（java, golang, python, rust, frontend, all）
    -f, --follow        跟踪日志输出
    -d, --detach        后台运行
    --no-cache          构建时不使用缓存
    --skip-monitor      跳过监控服务

示例:
    $0 start                    # 启动所有服务
    $0 start --skip-monitor     # 启动服务但不启动监控
    $0 stop                     # 停止所有服务
    $0 logs -f java-api         # 跟踪 Java 服务日志
    $0 generate-data            # 生成测试数据
    $0 quick-start              # 快速启动核心服务
    $0 build --no-cache         # 强制重新构建镜像

EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    # 检查 Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    # 检查 .env 文件
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning ".env 文件不存在，从模板创建..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        log_success ".env 文件已创建"
    fi

    log_success "依赖检查完成"
}

# 等待服务健康
wait_for_healthy() {
    local service=$1
    local max_wait=120
    local wait_time=0

    log_info "等待 $service 服务启动..."

    while [ $wait_time -lt $max_wait ]; do
        if docker compose ps "$service" 2>/dev/null | grep -q "healthy"; then
            log_success "$service 服务已就绪"
            return 0
        fi
        sleep 2
        wait_time=$((wait_time + 2))
        printf "\r${BLUE}[INFO]${NC} 等待中... %ds/%ds" "$wait_time" "$max_wait"
    done

    log_error "$service 服务启动超时"
    return 1
}

# 启动服务
start_services() {
    local skip_monitor=false
    local detach=true

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-monitor)
                skip_monitor=true
                shift
                ;;
            -d|--detach)
                detach=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    log_info "启动服务..."
    check_dependencies

    # 启动核心服务
    log_info "启动数据库..."
    docker compose up -d postgres

    wait_for_healthy postgres

    log_info "启动后端服务..."
    docker compose up -d java-api golang-api python-api rust-api

    log_info "启动前端服务..."
    docker compose up -d frontend

    # 启动监控服务
    if [ "$skip_monitor" = false ]; then
        log_info "启动监控服务..."
        docker compose up -d prometheus cadvisor postgres_exporter grafana
    fi

    log_success "所有服务已启动"

    # 显示服务状态
    show_status

    # 显示访问信息
    echo ""
    log_info "==================== 访问信息 ===================="
    echo -e "  前端界面:    ${GREEN}http://localhost:${FRONTEND_PORT:-80}${NC}"
    echo -e "  Java API:    ${GREEN}http://localhost:${JAVA_PORT:-8080}${NC}"
    echo -e "  Golang API:  ${GREEN}http://localhost:${GOLANG_PORT:-8081}${NC}"
    echo -e "  Python API:  ${GREEN}http://localhost:${PYTHON_PORT:-8082}${NC}"
    echo -e "  Rust API:    ${GREEN}http://localhost:${RUST_PORT:-8083}${NC}"
    echo -e "  Prometheus:  ${GREEN}http://localhost:${PROMETHEUS_PORT:-9090}${NC}"
    echo -e "  Grafana:     ${GREEN}http://localhost:${GRAFANA_PORT:-3000}${NC} (admin/admin123)"
    echo -e "  cAdvisor:    ${GREEN}http://localhost:${CADVISOR_PORT:-8084}${NC}"
    echo ""
    log_info "API Key: ${GREEN}${API_KEY:-benchmark-api-key-2024}${NC}"
    log_info "=================================================="
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    docker compose down
    log_success "所有服务已停止"
}

# 重启服务
restart_services() {
    stop_services
    start_services "$@"
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker compose ps
}

# 查看日志
show_logs() {
    local service=""
    local follow=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--follow)
                follow=true
                shift
                ;;
            -s|--service)
                service="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    if [ "$follow" = true ]; then
        if [ -n "$service" ]; then
            docker compose logs -f "$service"
        else
            docker compose logs -f
        fi
    else
        if [ -n "$service" ]; then
            docker compose logs --tail=100 "$service"
        else
            docker compose logs --tail=100
        fi
    fi
}

# 构建镜像
build_images() {
    local no_cache=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-cache)
                no_cache=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    log_info "构建所有服务镜像..."

    if [ "$no_cache" = true ]; then
        docker compose build --no-cache
    else
        docker compose build
    fi

    log_success "镜像构建完成"
}

# 清理
clean_all() {
    log_warning "这将删除所有容器、卷和镜像！"
    read -p "确认继续? (y/N): " confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        log_info "清理所有容器和卷..."
        docker compose down -v --remove-orphans
        docker compose rm -f

        log_info "清理未使用的镜像..."
        docker image prune -f

        log_success "清理完成"
    else
        log_info "操作已取消"
    fi
}

# 生成测试数据
generate_data() {
    local total=${1:-20000000}
    local workers=${2:-4}

    log_info "生成测试数据..."
    log_info "数据量: $total 条"
    log_info "并发进程: $workers"

    check_dependencies

    # 确保数据库已启动
    if ! docker compose ps postgres | grep -q "Up"; then
        log_info "启动数据库..."
        docker compose up -d postgres
        wait_for_healthy postgres
    fi

    # 运行数据生成器
    docker compose run --rm data-generator python main.py generate --total "$total" --workers "$workers"

    log_success "数据生成完成"
}

# 快速启动
quick_start() {
    log_info "快速启动核心服务..."
    check_dependencies

    # 启动数据库
    docker compose up -d postgres
    wait_for_healthy postgres

    # 启动一个后端服务和前端
    docker compose up -d java-api frontend

    log_success "核心服务已启动"
    show_status
}

# 仅启动监控
start_monitor() {
    log_info "启动监控服务..."
    check_dependencies

    docker compose up -d prometheus cadvisor postgres_exporter grafana

    log_success "监控服务已启动"
    echo ""
    log_info "==================== 监控访问信息 ===================="
    echo -e "  Prometheus:  ${GREEN}http://localhost:${PROMETHEUS_PORT:-9090}${NC}"
    echo -e "  Grafana:     ${GREEN}http://localhost:${GRAFANA_PORT:-3000}${NC} (admin/admin123)"
    echo -e "  cAdvisor:    ${GREEN}http://localhost:${CADVISOR_PORT:-8084}${NC}"
    log_info "====================================================="
}

# 主函数
main() {
    local command=${1:-start}

    case $command in
        start)
            start_services "${@:2}"
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services "${@:2}"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "${@:2}"
            ;;
        build)
            build_images "${@:2}"
            ;;
        clean)
            clean_all
            ;;
        generate-data)
            generate_data "${@:2}"
            ;;
        quick-start)
            quick_start
            ;;
        monitor)
            start_monitor
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
