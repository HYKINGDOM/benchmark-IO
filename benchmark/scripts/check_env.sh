#!/bin/bash

# 环境检查和服务验证脚本
# 用于验证测试环境和检查服务状态

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 服务配置
declare -A SERVICES
SERVICES["java"]=8080
SERVICES["golang"]=8081
SERVICES["python"]=8082
SERVICES["rust"]=8083

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 检查命令是否存在
check_command() {
    local cmd=$1
    local package=$2
    
    if command -v $cmd &> /dev/null; then
        log_success "$cmd 已安装"
        return 0
    else
        log_error "$cmd 未安装"
        log_info "安装方法: $package"
        return 1
    fi
}

# 检查系统依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    local all_ok=true
    
    # 检查 wrk
    if ! check_command "wrk" "brew install wrk (macOS) 或 apt-get install wrk (Ubuntu)"; then
        all_ok=false
    fi
    
    # 检查 curl
    if ! check_command "curl" "系统自带或包管理器安装"; then
        all_ok=false
    fi
    
    # 检查 jq (可选)
    if command -v jq &> /dev/null; then
        log_success "jq 已安装 (可选)"
    else
        log_warning "jq 未安装 (可选，用于 JSON 处理)"
        log_info "安装方法: brew install jq (macOS) 或 apt-get install jq (Ubuntu)"
    fi
    
    # 检查 Python (可选)
    if command -v python3 &> /dev/null; then
        log_success "Python3 已安装 (可选，用于结果分析)"
        
        # 检查 Python 包
        if python3 -c "import pandas" 2>/dev/null; then
            log_success "pandas 已安装 (可选，用于 Excel 导出)"
        else
            log_warning "pandas 未安装 (可选)"
            log_info "安装方法: pip install pandas openpyxl"
        fi
    else
        log_warning "Python3 未安装 (可选，用于结果分析)"
    fi
    
    if [[ "$all_ok" == "true" ]]; then
        log_success "所有必需依赖已安装"
        return 0
    else
        return 1
    fi
}

# 检查服务状态
check_service() {
    local service=$1
    local port=${SERVICES[$service]}
    
    if [[ -z "$port" ]]; then
        log_error "未知服务: $service"
        return 1
    fi
    
    log_info "检查 $service 服务 (端口: $port)..."
    
    # 检查端口是否被占用
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "$service 服务正在运行 (端口: $port)"
        
        # 尝试健康检查
        local health_url="http://localhost:$port/health"
        local response=$(curl -s -o /dev/null -w "%{http_code}" "$health_url" 2>/dev/null || echo "000")
        
        if [[ "$response" == "200" ]] || [[ "$response" == "404" ]]; then
            log_success "$service 服务健康检查通过"
            return 0
        else
            log_warning "$service 服务健康检查失败 (HTTP $response)"
            return 0  # 端口开放即认为服务运行
        fi
    else
        log_error "$service 服务未运行 (端口: $port)"
        return 1
    fi
}

# 检查所有服务
check_all_services() {
    log_info "检查所有服务状态..."
    
    local running_count=0
    local total=${#SERVICES[@]}
    
    for service in "${!SERVICES[@]}"; do
        if check_service "$service"; then
            ((running_count++))
        fi
    done
    
    echo ""
    log_info "服务状态汇总: $running_count/$total 个服务运行中"
    
    if [[ $running_count -eq 0 ]]; then
        log_error "没有服务在运行，请先启动至少一个服务"
        return 1
    elif [[ $running_count -lt $total ]]; then
        log_warning "部分服务未运行，将只测试运行中的服务"
        return 0
    else
        log_success "所有服务运行正常"
        return 0
    fi
}

# 检查数据库连接
check_database() {
    log_info "检查数据库连接..."
    
    # 从 .env 文件读取数据库配置
    local env_file="$PROJECT_ROOT/.env"
    
    if [[ -f "$env_file" ]]; then
        local db_host=$(grep DB_HOST "$env_file" | cut -d '=' -f2)
        local db_port=$(grep DB_PORT "$env_file" | cut -d '=' -f2)
        
        if [[ -n "$db_host" ]] && [[ -n "$db_port" ]]; then
            if nc -z "$db_host" "$db_port" 2>/dev/null; then
                log_success "数据库连接正常 ($db_host:$db_port)"
                return 0
            else
                log_error "无法连接到数据库 ($db_host:$db_port)"
                return 1
            fi
        fi
    fi
    
    log_warning "未找到数据库配置，跳过数据库检查"
    return 0
}

# 检查测试数据
check_test_data() {
    log_info "检查测试数据..."
    
    # 检查数据库中是否有测试数据
    # 这里可以添加具体的检查逻辑
    
    log_warning "请确保数据库中有足够的测试数据"
    log_info "建议数据量: 100万 - 2000万条订单记录"
    log_info "可以使用 init/generate_data 工具生成测试数据"
    
    return 0
}

# 检查系统资源
check_system_resources() {
    log_info "检查系统资源..."
    
    # CPU
    local cpu_cores=$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo "未知")
    log_info "CPU 核心数: $cpu_cores"
    
    # 内存
    if [[ "$(uname)" == "Darwin" ]]; then
        local total_mem=$(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024}')
        log_info "总内存: ${total_mem%.*} GB"
        
        local free_mem=$(vm_stat | grep "free" | awk '{print $3}' | sed 's/\.//')
        free_mem=$((free_mem * 4096 / 1024 / 1024))
        log_info "可用内存: ${free_mem} MB"
    else
        local mem_info=$(free -h | grep "Mem:")
        log_info "内存信息: $mem_info"
    fi
    
    # 磁盘空间
    local disk_usage=$(df -h "$PROJECT_ROOT" | tail -1 | awk '{print $5}')
    log_info "磁盘使用率: $disk_usage"
    
    # 检查资源是否充足
    if [[ "${disk_usage%\%}" -gt 90 ]]; then
        log_warning "磁盘空间不足，可能影响测试结果"
    fi
    
    return 0
}

# 检查网络
check_network() {
    log_info "检查网络连接..."
    
    # 检查本地回环
    if ping -c 1 localhost &> /dev/null; then
        log_success "本地回环正常"
    else
        log_error "本地回环异常"
        return 1
    fi
    
    # 检查端口可用性
    local test_ports=(8080 8081 8082 8083)
    for port in "${test_ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_info "端口 $port: 已被使用"
        else
            log_info "端口 $port: 可用"
        fi
    done
    
    return 0
}

# 生成环境报告
generate_env_report() {
    log_info "生成环境报告..."
    
    local report_file="$PROJECT_ROOT/benchmark/results/environment_report.txt"
    mkdir -p "$(dirname "$report_file")"
    
    {
        echo "================================"
        echo "性能测试环境报告"
        echo "================================"
        echo ""
        echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "系统信息:"
        echo "  操作系统: $(uname -s)"
        echo "  内核版本: $(uname -r)"
        echo "  架构: $(uname -m)"
        echo ""
        echo "硬件信息:"
        echo "  CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || cat /proc/cpuinfo | grep "model name" | head -1 | cut -d':' -f2)"
        echo "  CPU 核心数: $(sysctl -n hw.ncpu 2>/dev/null || nproc)"
        echo "  总内存: $(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024/1024 " GB"}' || free -h | grep Mem | awk '{print $2}')"
        echo ""
        echo "软件信息:"
        echo "  wrk 版本: $(wrk --version 2>&1 | head -1)"
        echo "  curl 版本: $(curl --version | head -1)"
        echo ""
        echo "服务状态:"
        for service in "${!SERVICES[@]}"; do
            local port=${SERVICES[$service]}
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                echo "  $service: 运行中 (端口 $port)"
            else
                echo "  $service: 未运行 (端口 $port)"
            fi
        done
        echo ""
        echo "磁盘空间:"
        df -h "$PROJECT_ROOT"
        echo ""
        echo "================================"
    } > "$report_file"
    
    log_success "环境报告已生成: $report_file"
}

# 主函数
main() {
    local action=${1:-"all"}
    
    echo ""
    echo "================================"
    echo "性能测试环境检查"
    echo "================================"
    echo ""
    
    case $action in
        deps)
            check_dependencies
            ;;
        services)
            check_all_services
            ;;
        service)
            local service=$2
            if [[ -z "$service" ]]; then
                log_error "请指定服务名称"
                echo "用法: $0 service {java|golang|python|rust}"
                exit 1
            fi
            check_service "$service"
            ;;
        database)
            check_database
            ;;
        resources)
            check_system_resources
            ;;
        network)
            check_network
            ;;
        report)
            generate_env_report
            ;;
        all)
            check_dependencies
            echo ""
            check_all_services
            echo ""
            check_database
            echo ""
            check_system_resources
            echo ""
            check_network
            echo ""
            generate_env_report
            ;;
        *)
            echo "用法: $0 {deps|services|service|database|resources|network|report|all}"
            echo ""
            echo "检查项:"
            echo "  deps      - 检查系统依赖"
            echo "  services  - 检查所有服务状态"
            echo "  service   - 检查指定服务状态 (需指定服务名)"
            echo "  database  - 检查数据库连接"
            echo "  resources - 检查系统资源"
            echo "  network   - 检查网络连接"
            echo "  report    - 生成环境报告"
            echo "  all       - 执行所有检查"
            exit 1
            ;;
    esac
}

main "$@"
