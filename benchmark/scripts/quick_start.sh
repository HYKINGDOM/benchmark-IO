#!/bin/bash

# 快速启动脚本
# 提供简单的菜单界面来运行性能测试

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 显示标题
show_header() {
    clear
    echo -e "${MAGENTA}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              性能测试脚本 - 快速启动                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo ""
}

# 显示菜单
show_menu() {
    echo -e "${CYAN}请选择操作:${NC}"
    echo ""
    echo "  1) 环境检查"
    echo "  2) 快速测试 (查询接口 - 所有服务)"
    echo "  3) 完整测试套件"
    echo "  4) 查询接口测试"
    echo "  5) 同步导出测试"
    echo "  6) 异步导出测试"
    echo "  7) 流式导出测试"
    echo "  8) 并发级别测试"
    echo "  9) 数据量测试"
    echo "  10) 收集测试结果"
    echo "  11) 生成对比报告"
    echo "  12) 查看帮助"
    echo "  0) 退出"
    echo ""
}

# 选择服务
select_service() {
    echo -e "${CYAN}请选择服务:${NC}"
    echo "  1) Java (端口 8080)"
    echo "  2) Golang (端口 8081)"
    echo "  3) Python (端口 8082)"
    echo "  4) Rust (端口 8083)"
    echo "  5) 所有服务"
    echo ""
    
    read -p "请输入选项 [1-5]: " service_choice
    
    case $service_choice in
        1) echo "java" ;;
        2) echo "golang" ;;
        3) echo "python" ;;
        4) echo "rust" ;;
        5) echo "all" ;;
        *) echo "" ;;
    esac
}

# 选择并发级别
select_concurrency() {
    echo -e "${CYAN}请选择并发级别:${NC}"
    echo "  1) 单用户 (1 并发)"
    echo "  2) 低并发 (10 并发)"
    echo "  3) 中等并发 (50 并发)"
    echo "  4) 高并发 (100 并发)"
    echo ""
    
    read -p "请输入选项 [1-4]: " concurrency_choice
    
    case $concurrency_choice in
        1) echo "single" ;;
        2) echo "low" ;;
        3) echo "medium" ;;
        4) echo "high" ;;
        *) echo "medium" ;;
    esac
}

# 确认执行
confirm_execution() {
    local description=$1
    
    echo ""
    echo -e "${YELLOW}即将执行: $description${NC}"
    read -p "确认执行? [y/N]: " confirm
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        return 0
    else
        echo -e "${YELLOW}已取消${NC}"
        return 1
    fi
}

# 执行环境检查
do_env_check() {
    show_header
    echo -e "${BLUE}执行环境检查...${NC}"
    echo ""
    "$SCRIPT_DIR/check_env.sh" all
    echo ""
    read -p "按回车键继续..."
}

# 执行快速测试
do_quick_test() {
    show_header
    echo -e "${BLUE}执行快速测试...${NC}"
    echo ""
    
    if confirm_execution "快速测试 - 查询接口 - 所有服务 - 中等并发"; then
        "$SCRIPT_DIR/run_all.sh" quick
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 执行完整测试
do_full_test() {
    show_header
    echo -e "${BLUE}执行完整测试套件...${NC}"
    echo ""
    
    if confirm_execution "完整测试套件 (可能需要较长时间)"; then
        "$SCRIPT_DIR/run_all.sh" full
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 执行查询测试
do_query_test() {
    show_header
    echo -e "${BLUE}查询接口测试${NC}"
    echo ""
    
    local service=$(select_service)
    if [[ -z "$service" ]]; then
        echo -e "${RED}无效选择${NC}"
        read -p "按回车键继续..."
        return
    fi
    
    local concurrency=$(select_concurrency)
    
    if confirm_execution "查询测试 - $service - $concurrency"; then
        "$SCRIPT_DIR/benchmark.sh" -t query -s "$service" -c "$concurrency"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 执行同步导出测试
do_sync_export_test() {
    show_header
    echo -e "${BLUE}同步导出测试${NC}"
    echo ""
    
    local service=$(select_service)
    if [[ -z "$service" ]]; then
        echo -e "${RED}无效选择${NC}"
        read -p "按回车键继续..."
        return
    fi
    
    local concurrency=$(select_concurrency)
    
    if confirm_execution "同步导出测试 - $service - $concurrency"; then
        "$SCRIPT_DIR/benchmark.sh" -t sync -s "$service" -c "$concurrency"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 执行异步导出测试
do_async_export_test() {
    show_header
    echo -e "${BLUE}异步导出测试${NC}"
    echo ""
    
    local service=$(select_service)
    if [[ -z "$service" ]]; then
        echo -e "${RED}无效选择${NC}"
        read -p "按回车键继续..."
        return
    fi
    
    local concurrency=$(select_concurrency)
    
    if confirm_execution "异步导出测试 - $service - $concurrency"; then
        "$SCRIPT_DIR/benchmark.sh" -t async -s "$service" -c "$concurrency"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 执行流式导出测试
do_stream_export_test() {
    show_header
    echo -e "${BLUE}流式导出测试${NC}"
    echo ""
    
    local service=$(select_service)
    if [[ -z "$service" ]]; then
        echo -e "${RED}无效选择${NC}"
        read -p "按回车键继续..."
        return
    fi
    
    local concurrency=$(select_concurrency)
    
    if confirm_execution "流式导出测试 - $service - $concurrency"; then
        "$SCRIPT_DIR/benchmark.sh" -t stream -s "$service" -c "$concurrency"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 执行并发测试
do_concurrency_test() {
    show_header
    echo -e "${BLUE}并发级别测试${NC}"
    echo ""
    
    echo -e "${CYAN}请选择测试类型:${NC}"
    echo "  1) 查询接口"
    echo "  2) 同步导出"
    echo "  3) 异步导出"
    echo "  4) 流式导出"
    echo ""
    read -p "请输入选项 [1-4]: " test_choice
    
    local test_type=""
    case $test_choice in
        1) test_type="query" ;;
        2) test_type="sync" ;;
        3) test_type="async" ;;
        4) test_type="stream" ;;
        *) echo -e "${RED}无效选择${NC}"; read -p "按回车键继续..."; return ;;
    esac
    
    local service=$(select_service)
    if [[ -z "$service" ]]; then
        echo -e "${RED}无效选择${NC}"
        read -p "按回车键继续..."
        return
    fi
    
    if confirm_execution "并发测试 - $test_type - $service"; then
        "$SCRIPT_DIR/run_all.sh" concurrency "$test_type" "$service"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 执行数据量测试
do_data_size_test() {
    show_header
    echo -e "${BLUE}数据量测试${NC}"
    echo ""
    
    echo -e "${CYAN}请选择测试类型:${NC}"
    echo "  1) 同步导出"
    echo "  2) 流式导出"
    echo ""
    read -p "请输入选项 [1-2]: " test_choice
    
    local test_type=""
    case $test_choice in
        1) test_type="sync" ;;
        2) test_type="stream" ;;
        *) echo -e "${RED}无效选择${NC}"; read -p "按回车键继续..."; return ;;
    esac
    
    local service=$(select_service)
    if [[ -z "$service" ]]; then
        echo -e "${RED}无效选择${NC}"
        read -p "按回车键继续..."
        return
    fi
    
    if confirm_execution "数据量测试 - $test_type - $service"; then
        "$SCRIPT_DIR/run_all.sh" data-size "$test_type" "$service"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 收集结果
do_collect_results() {
    show_header
    echo -e "${BLUE}收集测试结果${NC}"
    echo ""
    
    if confirm_execution "收集所有测试结果"; then
        "$SCRIPT_DIR/collect_results.sh" all
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 生成对比报告
do_compare_report() {
    show_header
    echo -e "${BLUE}生成对比报告${NC}"
    echo ""
    
    if confirm_execution "生成性能对比报告"; then
        "$SCRIPT_DIR/collect_results.sh" compare
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 显示帮助
do_show_help() {
    show_header
    "$SCRIPT_DIR/benchmark.sh" --help
    echo ""
    read -p "按回车键继续..."
}

# 主循环
main() {
    while true; do
        show_header
        show_menu
        
        read -p "请输入选项 [0-12]: " choice
        
        case $choice in
            1) do_env_check ;;
            2) do_quick_test ;;
            3) do_full_test ;;
            4) do_query_test ;;
            5) do_sync_export_test ;;
            6) do_async_export_test ;;
            7) do_stream_export_test ;;
            8) do_concurrency_test ;;
            9) do_data_size_test ;;
            10) do_collect_results ;;
            11) do_compare_report ;;
            12) do_show_help ;;
            0)
                echo -e "${GREEN}感谢使用!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选项，请重新选择${NC}"
                sleep 1
                ;;
        esac
    done
}

# 运行主程序
main
