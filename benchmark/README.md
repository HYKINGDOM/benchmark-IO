# 性能测试脚本使用指南

## 目录结构

```
benchmark/
├── scripts/
│   ├── benchmark.sh           # 主测试脚本
│   ├── query_test.lua         # wrk 查询测试脚本
│   ├── export_sync_test.lua   # wrk 同步导出测试脚本
│   ├── export_async_test.lua  # wrk 异步导出测试脚本
│   ├── export_stream_test.lua # wrk 流式导出测试脚本
│   ├── run_all.sh             # 运行所有测试
│   └── collect_results.sh     # 收集测试结果
├── results/                   # 测试结果目录
└── README.md                  # 本文档
```

## 前置要求

### 安装 wrk

**macOS:**
```bash
brew install wrk
```

**Ubuntu/Debian:**
```bash
sudo apt-get install wrk
```

**CentOS/RHEL:**
```bash
sudo yum install wrk
```

### 验证安装

```bash
wrk --version
```

## 快速开始

### 1. 启动后端服务

确保至少有一个后端服务正在运行：

```bash
# Java (端口 8080)
cd java && ./gradlew bootRun

# Golang (端口 8081)
cd golang && go run cmd/main.go

# Python (端口 8082)
cd python && python app/main.py

# Rust (端口 8083)
cd rust && cargo run
```

### 2. 运行快速测试

```bash
cd benchmark/scripts
./run_all.sh quick
```

### 3. 运行完整测试套件

```bash
./run_all.sh full
```

## 详细使用说明

### benchmark.sh - 单个测试

#### 基本用法

```bash
./benchmark.sh -t <test_type> -s <service> -c <concurrency> [options]
```

#### 参数说明

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `-t, --test-type` | 测试类型 | `query`, `sync`, `async`, `stream` |
| `-s, --service` | 服务类型 | `java`, `golang`, `python`, `rust`, `all` |
| `-c, --concurrency` | 并发级别 | `single` (1), `low` (10), `medium` (50), `high` (100) |
| `-d, --duration` | 测试时长 | 默认: `30s` |
| `-n, --data-size` | 数据量 | `1000000`, `2000000`, `5000000`, `10000000`, `20000000` |
| `--start-date` | 开始日期 | 格式: `YYYY-MM-DD` |
| `--end-date` | 结束日期 | 格式: `YYYY-MM-DD` |
| `--status` | 订单状态 | `pending`, `paid`, `cancelled`, `refunded`, `completed` |
| `--min-amount` | 最小金额 | 数字 |
| `--max-amount` | 最大金额 | 数字 |
| `--user-id` | 用户ID | 字符串 |
| `--region` | 地区 | 字符串 |
| `--format` | 导出格式 | `csv`, `excel` (默认: `csv`) |
| `-o, --output` | 输出文件 | 文件路径 |

#### 示例

**查询接口测试 - Java服务 - 高并发:**
```bash
./benchmark.sh -t query -s java -c high
```

**同步导出测试 - 所有服务 - 中等并发:**
```bash
./benchmark.sh -t sync -s all -c medium
```

**异步导出测试 - Golang服务 - 低并发 - 指定日期范围:**
```bash
./benchmark.sh -t async -s golang -c low \
    --start-date 2024-01-01 \
    --end-date 2024-06-30
```

**流式导出测试 - Python服务 - 单用户 - 指定数据量:**
```bash
./benchmark.sh -t stream -s python -c single -n 5000000
```

**带筛选条件的查询测试:**
```bash
./benchmark.sh -t query -s rust -c medium \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --status paid \
    --min-amount 100 \
    --max-amount 1000 \
    --region "北京"
```

### run_all.sh - 批量测试

#### 基本用法

```bash
./run_all.sh <mode> [options]
```

#### 测试模式

| 模式 | 说明 |
|------|------|
| `full` | 运行完整测试套件（所有测试类型、所有服务、所有并发级别） |
| `quick` | 运行快速测试（查询接口、所有服务、中等并发） |
| `concurrency` | 运行并发测试（可选: test_type service） |
| `data-size` | 运行数据量测试（可选: test_type service） |
| `filter` | 运行筛选条件测试（可选: test_type service） |

#### 示例

**运行完整测试套件:**
```bash
./run_all.sh full
```

**运行快速测试:**
```bash
./run_all.sh quick
```

**运行查询接口的并发测试（Java服务）:**
```bash
./run_all.sh concurrency query java
```

**运行同步导出的数据量测试（Golang服务）:**
```bash
./run_all.sh data-size sync golang
```

### collect_results.sh - 结果收集

#### 基本用法

```bash
./collect_results.sh <action> [options]
```

#### 操作类型

| 操作 | 说明 |
|------|------|
| `collect` | 收集测试结果（生成 JSON 和 CSV） |
| `compare` | 生成性能对比报告 |
| `export` | 导出结果为 Excel |
| `cleanup` | 清理旧结果（可选: 保留天数，默认7天） |
| `all` | 执行所有操作 |

#### 示例

**收集所有测试结果:**
```bash
./collect_results.sh collect
```

**生成性能对比报告:**
```bash
./collect_results.sh compare
```

**导出为 Excel:**
```bash
./collect_results.sh export
```

**清理 7 天前的旧结果:**
```bash
./collect_results.sh cleanup 7
```

**执行所有操作:**
```bash
./collect_results.sh all
```

## 测试场景

### 1. 并发级别测试

测试不同并发级别下的系统性能：

- **单用户** (single): 1 个并发连接
- **低并发** (low): 10 个并发连接
- **中等并发** (medium): 50 个并发连接
- **高并发** (high): 100 个并发连接

### 2. 数据量测试

测试不同数据量下的导出性能：

- 100万条记录
- 200万条记录
- 500万条记录
- 1000万条记录
- 2000万条记录

### 3. 筛选条件测试

测试不同筛选条件组合下的查询性能：

- 时间范围筛选
- 订单状态筛选
- 金额范围筛选
- 多条件组合筛选

## 测试指标

### 关键指标

- **QPS (Queries Per Second)**: 每秒查询数
- **延迟分布**:
  - 平均延迟 (Avg)
  - 最大延迟 (Max)
  - P50 延迟 (50% 请求的延迟)
  - P75 延迟 (75% 请求的延迟)
  - P90 延迟 (90% 请求的延迟)
  - P99 延迟 (99% 请求的延迟)

### 性能基准

建议的性能基准：

| 测试类型 | 并发级别 | 目标 QPS | 目标 P99 延迟 |
|---------|---------|---------|--------------|
| 查询接口 | medium | > 1000 | < 100ms |
| 同步导出 | low | > 10 | < 5000ms |
| 异步导出 | medium | > 50 | < 100ms |
| 流式导出 | low | > 20 | < 3000ms |

## 结果分析

### 测试结果文件

测试结果保存在 `results/` 目录：

- `*.txt`: 原始 wrk 输出
- `analysis/*.json`: JSON 格式的汇总结果
- `analysis/*.csv`: CSV 格式的结果数据
- `analysis/*.md`: 性能对比报告
- `analysis/*.xlsx`: Excel 格式的结果（需要安装 pandas）

### 查看结果

**查看最新测试结果:**
```bash
ls -lt results/*.txt | head -5
cat results/query_java_medium_*.txt
```

**查看性能对比报告:**
```bash
cat results/analysis/comparison_*.md
```

**使用 Excel 查看:**
```bash
open results/analysis/results_*.xlsx
```

## 最佳实践

### 1. 测试前准备

- 确保数据库有足够的测试数据
- 确保服务已启动并正常运行
- 关闭不必要的后台进程
- 确保系统资源充足

### 2. 测试执行

- 从低并发开始，逐步增加并发
- 每次测试之间留出间隔时间
- 监控系统资源使用情况
- 记录异常情况

### 3. 结果分析

- 对比不同服务的性能差异
- 分析性能瓶颈
- 关注 P99 延迟
- 检查错误率

### 4. 性能优化

- 根据测试结果识别瓶颈
- 针对性优化
- 重新测试验证效果
- 持续监控

## 故障排查

### wrk 未安装

```bash
# macOS
brew install wrk

# Ubuntu
sudo apt-get install wrk
```

### 服务未启动

```bash
# 检查服务状态
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
curl http://localhost:8083/health
```

### 连接被拒绝

- 检查服务端口是否正确
- 检查防火墙设置
- 检查服务日志

### 性能异常低

- 检查数据库连接池配置
- 检查系统资源（CPU、内存、磁盘 I/O）
- 检查网络延迟
- 检查日志是否有错误

## 高级用法

### 自定义 Lua 脚本

可以修改 `scripts/*.lua` 文件来自定义测试场景：

```lua
-- 修改请求参数
local start_date = os.getenv("start_date") or "2024-01-01"

-- 修改延迟时间
function delay()
    return math.random(100, 500)
end
```

### 自定义测试配置

修改 `benchmark.sh` 中的配置：

```bash
# 修改默认测试时长
DEFAULT_DURATION="60s"

# 修改并发级别
CONCURRENCY_LEVELS["high"]=200
```

### 集成到 CI/CD

```bash
#!/bin/bash
# CI/CD 脚本示例

# 启动服务
./start_services.sh

# 运行快速测试
cd benchmark/scripts
./run_all.sh quick

# 收集结果
./collect_results.sh all

# 检查性能是否达标
python3 check_performance.py results/analysis/results_*.csv
```

## 参考资料

- [wrk GitHub](https://github.com/wg/wrk)
- [wrk Lua 脚本文档](https://github.com/wg/wrk/blob/master/SCRIPTING)
- [性能测试最佳实践](https://martinfowler.com/articles/performance-testing-patterns/)

## 许可证

MIT License
