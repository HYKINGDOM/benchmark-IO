#!/bin/bash

# 测试结果数据采集和分析脚本
# 收集、解析和汇总性能测试结果

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
ANALYSIS_DIR="$RESULTS_DIR/analysis"

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

# 初始化
init() {
    mkdir -p "$ANALYSIS_DIR"
    log_info "分析结果将保存到: $ANALYSIS_DIR"
}

# 解析 wrk 输出
parse_wrk_output() {
    local file=$1
    
    if [[ ! -f "$file" ]]; then
        log_error "文件不存在: $file"
        return 1
    fi
    
    local result={}
    
    # 提取关键指标
    local requests=$(grep "requests in" "$file" | awk '{print $1}')
    local duration=$(grep "requests in" "$file" | awk '{print $4}')
    local rps=$(grep "Requests/sec" "$file" | awk '{print $2}')
    local avg_latency=$(grep "Avg" "$file" | awk '{print $2}')
    local max_latency=$(grep "Max" "$file" | awk '{print $2}')
    local p50=$(grep "50%" "$file" | awk '{print $2}')
    local p75=$(grep "75%" "$file" | awk '{print $2}')
    local p90=$(grep "90%" "$file" | awk '{print $2}')
    local p99=$(grep "99%" "$file" | awk '{print $2}')
    
    # 输出 JSON 格式
    cat << EOF
{
    "file": "$(basename "$file")",
    "total_requests": $requests,
    "duration": "$duration",
    "requests_per_sec": $rps,
    "avg_latency": "$avg_latency",
    "max_latency": "$max_latency",
    "p50": "$p50",
    "p75": "$p75",
    "p90": "$p90",
    "p99": "$p99"
}
EOF
}

# 收集所有测试结果
collect_results() {
    log_info "收集测试结果..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local summary_file="$ANALYSIS_DIR/summary_$timestamp.json"
    local csv_file="$ANALYSIS_DIR/results_$timestamp.csv"
    
    # 创建 CSV 表头
    echo "test_type,service,concurrency,total_requests,duration,rps,avg_latency,max_latency,p50,p75,p90,p99" > "$csv_file"
    
    # 开始 JSON 数组
    echo "[" > "$summary_file"
    
    local first=true
    
    # 遍历所有测试结果文件
    for result_file in "$RESULTS_DIR"/*.txt; do
        if [[ -f "$result_file" ]]; then
            local filename=$(basename "$result_file")
            
            # 解析文件名获取测试信息
            IFS='_' read -r test_type service concurrency timestamp <<< "${filename%.txt}"
            
            # 解析结果
            local parsed=$(parse_wrk_output "$result_file")
            
            # 添加到 JSON
            if [[ "$first" == "true" ]]; then
                first=false
            else
                echo "," >> "$summary_file"
            fi
            echo "$parsed" >> "$summary_file"
            
            # 添加到 CSV
            local requests=$(echo "$parsed" | grep "total_requests" | awk -F'"' '{print $2}')
            local duration=$(echo "$parsed" | grep "duration" | awk -F'"' '{print $2}')
            local rps=$(echo "$parsed" | grep "requests_per_sec" | awk -F'"' '{print $2}')
            local avg=$(echo "$parsed" | grep "avg_latency" | awk -F'"' '{print $2}')
            local max=$(echo "$parsed" | grep "max_latency" | awk -F'"' '{print $2}')
            local p50=$(echo "$parsed" | grep '"p50"' | awk -F'"' '{print $2}')
            local p75=$(echo "$parsed" | grep "p75" | awk -F'"' '{print $2}')
            local p90=$(echo "$parsed" | grep "p90" | awk -F'"' '{print $2}')
            local p99=$(echo "$parsed" | grep '"p99"' | awk -F'"' '{print $2}')
            
            echo "$test_type,$service,$concurrency,$requests,$duration,$rps,$avg,$max,$p50,$p75,$p90,$p99" >> "$csv_file"
            
            log_success "已收集: $filename"
        fi
    done
    
    # 结束 JSON 数组
    echo "]" >> "$summary_file"
    
    log_success "结果已保存到:"
    log_info "  JSON: $summary_file"
    log_info "  CSV: $csv_file"
}

# 生成性能对比报告
generate_comparison_report() {
    log_info "生成性能对比报告..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="$ANALYSIS_DIR/comparison_$timestamp.md"
    
    cat > "$report_file" << EOF
# 性能对比报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 1. 查询接口性能对比

### 1.1 不同服务对比（中等并发）

| 服务 | QPS | 平均延迟(ms) | P99延迟(ms) |
|------|-----|-------------|------------|
EOF
    
    # 从最新的 CSV 文件中提取数据
    local latest_csv=$(ls -t "$ANALYSIS_DIR"/results_*.csv 2>/dev/null | head -1)
    
    if [[ -f "$latest_csv" ]]; then
        # 查询接口 - 中等并发
        grep "^query,.*,medium," "$latest_csv" | while IFS=',' read -r test_type service concurrency total_requests duration rps avg max p50 p75 p90 p99; do
            echo "| $service | $rps | $avg | $p99 |" >> "$report_file"
        done
    fi
    
    cat >> "$report_file" << EOF

### 1.2 不同并发级别对比（Java服务）

| 并发级别 | QPS | 平均延迟(ms) | P99延迟(ms) |
|----------|-----|-------------|------------|
EOF
    
    if [[ -f "$latest_csv" ]]; then
        grep "^query,java," "$latest_csv" | while IFS=',' read -r test_type service concurrency total_requests duration rps avg max p50 p75 p90 p99; do
            echo "| $concurrency | $rps | $avg | $p99 |" >> "$report_file"
        done
    fi
    
    cat >> "$report_file" << EOF

## 2. 导出接口性能对比

### 2.1 同步导出性能

| 服务 | 并发 | QPS | 平均延迟(ms) | P99延迟(ms) |
|------|------|-----|-------------|------------|
EOF
    
    if [[ -f "$latest_csv" ]]; then
        grep "^sync," "$latest_csv" | while IFS=',' read -r test_type service concurrency total_requests duration rps avg max p50 p75 p90 p99; do
            echo "| $service | $concurrency | $rps | $avg | $p99 |" >> "$report_file"
        done
    fi
    
    cat >> "$report_file" << EOF

### 2.2 异步导出性能

| 服务 | 并发 | QPS | 平均延迟(ms) | P99延迟(ms) |
|------|------|-----|-------------|------------|
EOF
    
    if [[ -f "$latest_csv" ]]; then
        grep "^async," "$latest_csv" | while IFS=',' read -r test_type service concurrency total_requests duration rps avg max p50 p75 p90 p99; do
            echo "| $service | $concurrency | $rps | $avg | $p99 |" >> "$report_file"
        done
    fi
    
    cat >> "$report_file" << EOF

### 2.3 流式导出性能

| 服务 | 并发 | QPS | 平均延迟(ms) | P99延迟(ms) |
|------|------|-----|-------------|------------|
EOF
    
    if [[ -f "$latest_csv" ]]; then
        grep "^stream," "$latest_csv" | while IFS=',' read -r test_type service concurrency total_requests duration rps avg max p50 p75 p90 p99; do
            echo "| $service | $concurrency | $rps | $avg | $p99 |" >> "$report_file"
        done
    fi
    
    cat >> "$report_file" << EOF

## 3. 性能分析

### 3.1 最佳性能服务

- **查询接口**: 待分析
- **同步导出**: 待分析
- **异步导出**: 待分析
- **流式导出**: 待分析

### 3.2 性能瓶颈分析

待补充...

### 3.3 优化建议

待补充...

---
*报告由自动化脚本生成*
EOF
    
    log_success "对比报告已生成: $report_file"
}

# 清理旧结果
cleanup_old_results() {
    log_info "清理旧的测试结果..."
    
    local keep_days=${1:-7}
    local count=0
    
    # 清理 7 天前的结果
    find "$RESULTS_DIR" -name "*.txt" -type f -mtime +$keep_days | while read -r file; do
        rm -f "$file"
        ((count++))
    done
    
    log_success "已清理 $count 个旧文件"
}

# 导出结果到 Excel
export_to_excel() {
    log_info "导出结果到 Excel..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local excel_file="$ANALYSIS_DIR/results_$timestamp.xlsx"
    
    # 检查是否有 Python 和 pandas
    if command -v python3 &> /dev/null && python3 -c "import pandas" 2>/dev/null; then
        local latest_csv=$(ls -t "$ANALYSIS_DIR"/results_*.csv 2>/dev/null | head -1)
        
        if [[ -f "$latest_csv" ]]; then
            python3 << EOF
import pandas as pd
import sys

try:
    df = pd.read_csv("$latest_csv")
    
    # 创建 Excel writer
    with pd.ExcelWriter("$excel_file", engine='openpyxl') as writer:
        # 按测试类型分组
        for test_type in df['test_type'].unique():
            df_type = df[df['test_type'] == test_type]
            df_type.to_excel(writer, sheet_name=test_type, index=False)
        
        # 添加汇总表
        df.to_excel(writer, sheet_name='all_results', index=False)
    
    print("Excel 文件已生成: $excel_file")
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    sys.exit(1)
EOF
            
            if [[ $? -eq 0 ]]; then
                log_success "Excel 文件已生成: $excel_file"
            else
                log_warning "Excel 导出失败，请检查 pandas 和 openpyxl 是否安装"
            fi
        else
            log_warning "未找到 CSV 文件"
        fi
    else
        log_warning "未安装 Python 或 pandas，跳过 Excel 导出"
        log_info "安装方法: pip install pandas openpyxl"
    fi
}

# 主函数
main() {
    local action=${1:-"collect"}
    
    init
    
    case $action in
        collect)
            collect_results
            ;;
        compare)
            generate_comparison_report
            ;;
        export)
            export_to_excel
            ;;
        cleanup)
            local days=${2:-7}
            cleanup_old_results "$days"
            ;;
        all)
            collect_results
            generate_comparison_report
            export_to_excel
            ;;
        *)
            echo "用法: $0 {collect|compare|export|cleanup|all}"
            echo ""
            echo "操作:"
            echo "  collect - 收集测试结果"
            echo "  compare - 生成对比报告"
            echo "  export  - 导出为 Excel"
            echo "  cleanup - 清理旧结果 (可选: 保留天数，默认7天)"
            echo "  all     - 执行所有操作"
            exit 1
            ;;
    esac
}

main "$@"
