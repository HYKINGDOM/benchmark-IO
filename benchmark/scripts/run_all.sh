#!/bin/bash

# 运行所有性能测试
# 按照测试矩阵执行完整的性能测试套件

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
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/results"
LOG_DIR="$RESULTS_DIR/logs"

# 测试配置
TEST_TYPES=("query" "sync" "async" "stream")
SERVICES=("java" "golang" "python" "rust")
CONCURRENCY_LEVELS=("single" "low" "medium" "high")
DATA_SIZES=("1000000" "2000000" "5000000" "10000000" "20000000")

# 测试时长配置
DURATION_SHORT="10s"
DURATION_MEDIUM="30s"
DURATION_LONG="60s"

# 日志函数
log_header() {
    echo -e "\n${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}========================================${NC}\n"
}

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

# 初始化
init() {
    log_header "初始化测试环境"
    
    # 创建目录
    mkdir -p "$RESULTS_DIR"
    mkdir -p "$LOG_DIR"
    
    # 创建测试报告目录
    local timestamp=$(date +%Y%m%d_%H%M%S)
    REPORT_DIR="$RESULTS_DIR/report_$timestamp"
    mkdir -p "$REPORT_DIR"
    
    log_success "测试报告将保存到: $REPORT_DIR"
    
    # 检查服务是否运行
    check_services
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    local services_running=0
    local ports=(8080 8081 8082 8083)
    local service_names=("Java" "Golang" "Python" "Rust")
    
    for i in "${!ports[@]}"; do
        local port=${ports[$i]}
        local name=${service_names[$i]}
        
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health" | grep -q "200\|404"; then
            log_success "$name 服务运行中 (端口: $port)"
            ((services_running++))
        else
            log_warning "$name 服务未运行 (端口: $port)"
        fi
    done
    
    if [[ $services_running -eq 0 ]]; then
        log_error "没有服务在运行，请先启动服务"
        exit 1
    fi
    
    log_info "检测到 $services_running 个服务正在运行"
}

# 运行单个测试场景
run_scenario() {
    local test_type=$1
    local service=$2
    local concurrency=$3
    local duration=$4
    local description=$5
    
    log_info "执行: $description"
    
    local output_file="$REPORT_DIR/${test_type}_${service}_${concurrency}.txt"
    
    "$SCRIPT_DIR/benchmark.sh" \
        -t "$test_type" \
        -s "$service" \
        -c "$concurrency" \
        -d "$duration" \
        -o "$output_file"
    
    if [[ $? -eq 0 ]]; then
        log_success "完成: $description"
    else
        log_error "失败: $description"
    fi
    
    # 短暂休息
    sleep 2
}

# 运行并发测试
run_concurrency_tests() {
    log_header "阶段 1: 并发级别测试"
    
    local test_type=$1
    local service=$2
    
    for concurrency in "${CONCURRENCY_LEVELS[@]}"; do
        local description="并发测试 - $test_type - $service - $concurrency"
        run_scenario "$test_type" "$service" "$concurrency" "$DURATION_MEDIUM" "$description"
    done
}

# 运行数据量测试
run_data_size_tests() {
    log_header "阶段 2: 数据量测试"
    
    local test_type=$1
    local service=$2
    local concurrency=$3
    
    for i in "${!DATA_SIZES[@]}"; do
        local size=${DATA_SIZES[$i]}
        local description="数据量测试 - $test_type - $service - $size 条记录"
        
        # 根据数据量调整日期范围
        local start_date="2024-01-01"
        local end_date="2024-12-31"
        
        # TODO: 根据数据量动态调整日期范围
        
        "$SCRIPT_DIR/benchmark.sh" \
            -t "$test_type" \
            -s "$service" \
            -c "$concurrency" \
            -d "$DURATION_LONG" \
            --start-date "$start_date" \
            --end-date "$end_date" \
            -o "$REPORT_DIR/${test_type}_${service}_data_${size}.txt"
        
        log_success "完成: $description"
        sleep 5
    done
}

# 运行筛选条件测试
run_filter_tests() {
    log_header "阶段 3: 筛选条件测试"
    
    local test_type=$1
    local service=$2
    
    # 测试不同筛选条件组合
    local scenarios=(
        "时间范围:2024-01-01:2024-03-31"
        "订单状态:paid:2024-01-01:2024-12-31"
        "金额范围:100:1000:2024-01-01:2024-12-31"
        "组合条件:paid:100:1000:2024-01-01:2024-06-30"
    )
    
    for scenario in "${scenarios[@]}"; do
        IFS=':' read -r name status min_amount max_amount start_date end_date <<< "$scenario"
        
        local description="筛选测试 - $test_type - $service - $name"
        local output_file="$REPORT_DIR/${test_type}_${service}_filter_${name// /_}.txt"
        
        "$SCRIPT_DIR/benchmark.sh" \
            -t "$test_type" \
            -s "$service" \
            -c "medium" \
            -d "$DURATION_MEDIUM" \
            --start-date "$start_date" \
            --end-date "$end_date" \
            --status "$status" \
            --min-amount "$min_amount" \
            --max-amount "$max_amount" \
            -o "$output_file"
        
        log_success "完成: $description"
        sleep 2
    done
}

# 运行完整测试套件
run_full_suite() {
    log_header "运行完整测试套件"
    
    local start_time=$(date +%s)
    
    # 1. 查询接口测试
    log_info "=== 查询接口测试 ==="
    for service in "${SERVICES[@]}"; do
        run_concurrency_tests "query" "$service"
    done
    
    # 2. 同步导出测试
    log_info "=== 同步导出测试 ==="
    for service in "${SERVICES[@]}"; do
        run_concurrency_tests "sync" "$service"
        run_data_size_tests "sync" "$service" "low"
    done
    
    # 3. 异步导出测试
    log_info "=== 异步导出测试 ==="
    for service in "${SERVICES[@]}"; do
        run_concurrency_tests "async" "$service"
    done
    
    # 4. 流式导出测试
    log_info "=== 流式导出测试 ==="
    for service in "${SERVICES[@]}"; do
        run_concurrency_tests "stream" "$service"
        run_data_size_tests "stream" "$service" "low"
    done
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_header "测试完成"
    log_info "总耗时: $duration 秒"
    log_info "测试报告: $REPORT_DIR"
}

# 运行快速测试
run_quick_test() {
    log_header "运行快速测试"
    
    # 只测试查询接口 - 所有服务 - 中等并发
    for service in "${SERVICES[@]}"; do
        run_scenario "query" "$service" "medium" "$DURATION_SHORT" "快速测试 - $service"
    done
}

# 生成测试报告
generate_report() {
    log_header "生成测试报告"
    
    local report_file="$REPORT_DIR/summary.md"
    
    cat > "$report_file" << EOF
# 性能测试报告

**测试时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 测试概览

### 测试环境
- 操作系统: $(uname -s)
- 内核版本: $(uname -r)
- CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || cat /proc/cpuinfo | grep "model name" | head -1 | cut -d':' -f2)
- 内存: $(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024/1024 " GB"}' || free -h | grep Mem | awk '{print $2}')

### 测试配置
- 并发级别: ${CONCURRENCY_LEVELS[@]}
- 数据量档位: ${DATA_SIZES[@]}
- 测试时长: 短($DURATION_SHORT), 中($DURATION_MEDIUM), 长($DURATION_LONG)

## 测试结果

EOF
    
    # 解析测试结果
    for result_file in "$REPORT_DIR"/*.txt; do
        if [[ -f "$result_file" ]]; then
            local filename=$(basename "$result_file")
            echo "### $filename" >> "$report_file"
            echo "\`\`\`" >> "$report_file"
            grep -A 20 "Summary" "$result_file" >> "$report_file" 2>/dev/null || echo "无详细数据" >> "$report_file"
            echo "\`\`\`" >> "$report_file"
            echo "" >> "$report_file"
        fi
    done
    
    log_success "测试报告已生成: $report_file"
}

# 主函数
main() {
    local mode=${1:-"full"}
    
    case $mode in
        full)
            init
            run_full_suite
            generate_report
            ;;
        quick)
            init
            run_quick_test
            generate_report
            ;;
        concurrency)
            init
            local test_type=${2:-"query"}
            local service=${3:-"java"}
            run_concurrency_tests "$test_type" "$service"
            generate_report
            ;;
        data-size)
            init
            local test_type=${2:-"sync"}
            local service=${3:-"java"}
            run_data_size_tests "$test_type" "$service" "low"
            generate_report
            ;;
        filter)
            init
            local test_type=${2:-"query"}
            local service=${3:-"java"}
            run_filter_tests "$test_type" "$service"
            generate_report
            ;;
        *)
            echo "用法: $0 {full|quick|concurrency|data-size|filter}"
            echo ""
            echo "测试模式:"
            echo "  full        - 运行完整测试套件"
            echo "  quick       - 运行快速测试"
            echo "  concurrency - 运行并发测试 (可选: test_type service)"
            echo "  data-size   - 运行数据量测试 (可选: test_type service)"
            echo "  filter      - 运行筛选条件测试 (可选: test_type service)"
            exit 1
            ;;
    esac
}

main "$@"
