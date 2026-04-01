#!/bin/bash

# 脚本验证脚本
# 验证所有性能测试脚本是否可以正常工作

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# 验证脚本文件
verify_scripts() {
    log_info "验证脚本文件..."
    
    local scripts=(
        "benchmark.sh"
        "run_all.sh"
        "collect_results.sh"
        "check_env.sh"
        "quick_start.sh"
        "query_test.lua"
        "export_sync_test.lua"
        "export_async_test.lua"
        "export_stream_test.lua"
    )
    
    local all_ok=true
    
    for script in "${scripts[@]}"; do
        local script_path="$SCRIPT_DIR/$script"
        
        if [[ -f "$script_path" ]]; then
            log_success "文件存在: $script"
            
            # 检查 Shell 脚本是否有执行权限
            if [[ "$script" == *.sh ]]; then
                if [[ -x "$script_path" ]]; then
                    log_success "  可执行权限: OK"
                else
                    log_error "  可执行权限: 缺失"
                    all_ok=false
                fi
            fi
            
            # 检查 Shell 脚本语法
            if [[ "$script" == *.sh ]]; then
                if bash -n "$script_path" 2>/dev/null; then
                    log_success "  语法检查: OK"
                else
                    log_error "  语法检查: 失败"
                    all_ok=false
                fi
            fi
        else
            log_error "文件缺失: $script"
            all_ok=false
        fi
    done
    
    if [[ "$all_ok" == "true" ]]; then
        log_success "所有脚本文件验证通过"
        return 0
    else
        log_error "部分脚本文件验证失败"
        return 1
    fi
}

# 验证帮助信息
verify_help() {
    log_info "验证帮助信息..."
    
    # benchmark.sh 帮助
    if "$SCRIPT_DIR/benchmark.sh" --help &>/dev/null; then
        log_success "benchmark.sh --help: OK"
    else
        log_error "benchmark.sh --help: 失败"
    fi
    
    # run_all.sh 帮助（无参数时显示用法）
    if "$SCRIPT_DIR/run_all.sh" 2>&1 | grep -q "用法"; then
        log_success "run_all.sh 用法说明: OK"
    else
        log_error "run_all.sh 用法说明: 失败"
    fi
    
    # collect_results.sh 帮助（无参数时显示用法）
    if "$SCRIPT_DIR/collect_results.sh" 2>&1 | grep -q "用法"; then
        log_success "collect_results.sh 用法说明: OK"
    else
        log_error "collect_results.sh 用法说明: 失败"
    fi
    
    # check_env.sh 帮助（无参数时显示用法）
    if "$SCRIPT_DIR/check_env.sh" 2>&1 | grep -q "用法"; then
        log_success "check_env.sh 用法说明: OK"
    else
        log_error "check_env.sh 用法说明: 失败"
    fi
}

# 验证依赖
verify_dependencies() {
    log_info "验证依赖..."
    
    # 检查 wrk
    if command -v wrk &> /dev/null; then
        log_success "wrk 已安装: $(wrk --version 2>&1 | head -1)"
    else
        log_error "wrk 未安装"
        log_info "安装方法: brew install wrk (macOS) 或 apt-get install wrk (Ubuntu)"
    fi
    
    # 检查 curl
    if command -v curl &> /dev/null; then
        log_success "curl 已安装"
    else
        log_error "curl 未安装"
    fi
}

# 验证目录结构
verify_directories() {
    log_info "验证目录结构..."
    
    local project_root="$(dirname "$SCRIPT_DIR")"
    local dirs=(
        "$project_root/results"
        "$project_root/results/analysis"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            log_success "目录存在: $dir"
        else
            log_info "创建目录: $dir"
            mkdir -p "$dir"
            log_success "目录已创建: $dir"
        fi
    done
}

# 运行简单测试
run_simple_test() {
    log_info "运行简单测试..."
    
    # 检查是否有服务在运行
    local has_service=false
    local ports=(8080 8081 8082 8083)
    local service_names=("Java" "Golang" "Python" "Rust")
    
    for i in "${!ports[@]}"; do
        local port=${ports[$i]}
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_success "${service_names[$i]} 服务运行中 (端口: $port)"
            has_service=true
        fi
    done
    
    if [[ "$has_service" == "false" ]]; then
        log_warning "没有服务在运行，跳过实际测试"
        log_info "请先启动至少一个后端服务"
        return 0
    fi
    
    # 如果有服务运行，运行一个快速测试
    log_info "运行快速测试 (查询接口 - Java - 单用户 - 5秒)..."
    
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        if "$SCRIPT_DIR/benchmark.sh" -t query -s java -c single -d 5s 2>&1 | grep -q "Summary"; then
            log_success "测试执行成功"
        else
            log_error "测试执行失败"
        fi
    else
        log_warning "Java 服务未运行，跳过测试"
    fi
}

# 主函数
main() {
    echo ""
    echo "================================"
    echo "性能测试脚本验证"
    echo "================================"
    echo ""
    
    verify_scripts
    echo ""
    
    verify_help
    echo ""
    
    verify_dependencies
    echo ""
    
    verify_directories
    echo ""
    
    run_simple_test
    echo ""
    
    echo "================================"
    echo "验证完成"
    echo "================================"
}

main "$@"
