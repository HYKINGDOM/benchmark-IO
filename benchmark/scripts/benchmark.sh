#!/bin/bash

# 性能测试主脚本
# 支持多种测试场景和并发级别

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/results"

# API 配置
API_KEY="benchmark-api-key-2024"
JAVA_PORT=8080
GOLANG_PORT=8081
PYTHON_PORT=8082
RUST_PORT=8083

# 默认配置
DEFAULT_DURATION="30s"
DEFAULT_THREADS=4

# 并发级别配置
declare -A CONCURRENCY_LEVELS
CONCURRENCY_LEVELS["single"]=1
CONCURRENCY_LEVELS["low"]=10
CONCURRENCY_LEVELS["medium"]=50
CONCURRENCY_LEVELS["high"]=100

# 数据量档位配置
DATA_SIZES=("1000000" "2000000" "5000000" "10000000" "20000000")
DATA_SIZE_LABELS=("100万" "200万" "500万" "1000万" "2000万")

# 使用说明
usage() {
    cat << EOF
用法: $0 [选项]

性能测试脚本 - 支持多种测试场景

选项:
    -t, --test-type <type>       测试类型: query, sync, async, stream
    -s, --service <service>      服务类型: java, golang, python, rust, all
    -c, --concurrency <level>    并发级别: single, low, medium, high
    -d, --duration <duration>    测试时长 (默认: 30s)
    -n, --data-size <size>       数据量: 1000000, 2000000, 5000000, 10000000, 20000000
    --start-date <date>          开始日期 (格式: YYYY-MM-DD)
    --end-date <date>            结束日期 (格式: YYYY-MM-DD)
    --status <status>            订单状态: pending, paid, cancelled, refunded, completed
    --min-amount <amount>        最小金额
    --max-amount <amount>        最大金额
    --user-id <id>               用户ID
    --region <region>            地区
    --format <format>            导出格式: csv, excel (默认: csv)
    -o, --output <file>          输出文件路径
    -h, --help                   显示帮助信息

示例:
    # 查询接口测试 - Java服务 - 高并发
    $0 -t query -s java -c high

    # 同步导出测试 - 所有服务 - 中等并发
    $0 -t sync -s all -c medium

    # 异步导出测试 - Golang服务 - 低并发 - 指定日期范围
    $0 -t async -s golang -c low --start-date 2024-01-01 --end-date 2024-06-30

    # 流式导出测试 - Python服务 - 单用户 - 指定数据量
    $0 -t stream -s python -c single -n 5000000

EOF
    exit 0
}

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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v wrk &> /dev/null; then
        log_error "wrk 未安装，请先安装 wrk"
        log_info "macOS: brew install wrk"
        log_info "Ubuntu: sudo apt-get install wrk"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 获取服务端口
get_service_port() {
    local service=$1
    case $service in
        java) echo $JAVA_PORT ;;
        golang) echo $GOLANG_PORT ;;
        python) echo $PYTHON_PORT ;;
        rust) echo $RUST_PORT ;;
        *) log_error "未知服务: $service"; exit 1 ;;
    esac
}

# 获取并发数
get_concurrency() {
    local level=$1
    if [[ -v CONCURRENCY_LEVELS[$level] ]]; then
        echo ${CONCURRENCY_LEVELS[$level]}
    else
        log_error "未知并发级别: $level"
        exit 1
    fi
}

# 构建 wrk 命令
build_wrk_command() {
    local test_type=$1
    local service=$2
    local concurrency=$3
    local duration=$4
    
    local port=$(get_service_port $service)
    local base_url="http://localhost:$port"
    local lua_script="$SCRIPT_DIR/${test_type}_test.lua"
    
    if [[ ! -f "$lua_script" ]]; then
        log_error "Lua 脚本不存在: $lua_script"
        exit 1
    fi
    
    local cmd="wrk -s $lua_script --latency -t$DEFAULT_THREADS -c$concurrency -d$duration $base_url"
    
    # 添加环境变量
    if [[ -n "$START_DATE" ]]; then
        cmd="start_date=$START_DATE $cmd"
    fi
    if [[ -n "$END_DATE" ]]; then
        cmd="end_date=$END_DATE $cmd"
    fi
    if [[ -n "$ORDER_STATUS" ]]; then
        cmd="order_status=$ORDER_STATUS $cmd"
    fi
    if [[ -n "$MIN_AMOUNT" ]]; then
        cmd="min_amount=$MIN_AMOUNT $cmd"
    fi
    if [[ -n "$MAX_AMOUNT" ]]; then
        cmd="max_amount=$MAX_AMOUNT $cmd"
    fi
    if [[ -n "$USER_ID" ]]; then
        cmd="user_id=$USER_ID $cmd"
    fi
    if [[ -n "$REGION" ]]; then
        cmd="region=$REGION $cmd"
    fi
    if [[ -n "$EXPORT_FORMAT" ]]; then
        cmd="format=$EXPORT_FORMAT $cmd"
    fi
    
    echo "$cmd"
}

# 运行测试
run_test() {
    local test_type=$1
    local service=$2
    local concurrency=$3
    local duration=$4
    local output_file=$5
    
    log_info "开始测试: $test_type - $service - $concurrency 并发 - $duration"
    
    local cmd=$(build_wrk_command $test_type $service $concurrency $duration)
    
    if [[ -n "$output_file" ]]; then
        log_info "结果将保存到: $output_file"
        mkdir -p "$(dirname "$output_file")"
        eval $cmd | tee "$output_file"
    else
        eval $cmd
    fi
    
    log_success "测试完成: $test_type - $service"
}

# 运行所有服务测试
run_all_services() {
    local test_type=$1
    local concurrency=$2
    local duration=$3
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    for service in java golang python rust; do
        local output_file="$RESULTS_DIR/${test_type}_${service}_${concurrency}_${timestamp}.txt"
        run_test $test_type $service $concurrency $duration "$output_file"
        echo ""
    done
}

# 主函数
main() {
    local test_type=""
    local service=""
    local concurrency_level=""
    local duration=$DEFAULT_DURATION
    local data_size=""
    local output_file=""
    
    START_DATE=""
    END_DATE=""
    ORDER_STATUS=""
    MIN_AMOUNT=""
    MAX_AMOUNT=""
    USER_ID=""
    REGION=""
    EXPORT_FORMAT="csv"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--test-type)
                test_type="$2"
                shift 2
                ;;
            -s|--service)
                service="$2"
                shift 2
                ;;
            -c|--concurrency)
                concurrency_level="$2"
                shift 2
                ;;
            -d|--duration)
                duration="$2"
                shift 2
                ;;
            -n|--data-size)
                data_size="$2"
                shift 2
                ;;
            --start-date)
                START_DATE="$2"
                shift 2
                ;;
            --end-date)
                END_DATE="$2"
                shift 2
                ;;
            --status)
                ORDER_STATUS="$2"
                shift 2
                ;;
            --min-amount)
                MIN_AMOUNT="$2"
                shift 2
                ;;
            --max-amount)
                MAX_AMOUNT="$2"
                shift 2
                ;;
            --user-id)
                USER_ID="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --format)
                EXPORT_FORMAT="$2"
                shift 2
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "未知参数: $1"
                usage
                ;;
        esac
    done
    
    # 验证参数
    if [[ -z "$test_type" ]]; then
        log_error "必须指定测试类型 (-t, --test-type)"
        usage
    fi
    
    if [[ -z "$service" ]]; then
        log_error "必须指定服务类型 (-s, --service)"
        usage
    fi
    
    if [[ -z "$concurrency_level" ]]; then
        log_error "必须指定并发级别 (-c, --concurrency)"
        usage
    fi
    
    # 检查依赖
    check_dependencies
    
    # 获取并发数
    local concurrency=$(get_concurrency $concurrency_level)
    
    # 运行测试
    if [[ "$service" == "all" ]]; then
        run_all_services $test_type $concurrency $duration
    else
        if [[ -n "$output_file" ]]; then
            run_test $test_type $service $concurrency $duration "$output_file"
        else
            local timestamp=$(date +%Y%m%d_%H%M%S)
            output_file="$RESULTS_DIR/${test_type}_${service}_${concurrency_level}_${timestamp}.txt"
            run_test $test_type $service $concurrency $duration "$output_file"
        fi
    fi
}

main "$@"
