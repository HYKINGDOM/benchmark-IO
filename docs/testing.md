# 测试指南

本文档详细说明百万级数据导出跨语言性能基准测试系统的测试方法和流程。

## 目录

- [测试环境准备](#测试环境准备)
- [测试工具](#测试工具)
- [测试场景](#测试场景)
- [测试执行](#测试执行)
- [结果分析](#结果分析)
- [性能基准](#性能基准)
- [最佳实践](#最佳实践)

## 测试环境准备

### 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 4 核 | 8 核+ |
| 内存 | 8 GB | 16 GB+ |
| 磁盘 | 50 GB | 100 GB SSD |
| 网络 | 100 Mbps | 1 Gbps |

### 环境检查

```bash
# 检查 Docker 版本
docker --version
docker compose version

# 检查系统资源
free -h
df -h

# 检查端口占用
netstat -tlnp | grep -E '80|5432|8080|8081|8082|8083|9090|3000'
```

### 启动服务

```bash
# 启动所有服务
./scripts/start.sh start

# 验证服务状态
./scripts/start.sh status

# 验证服务健康
curl http://localhost:8080/actuator/health
curl http://localhost:8081/health
curl http://localhost:8082/health
curl http://localhost:8083/health
```

### 生成测试数据

```bash
# 生成 200 万条测试数据
./scripts/start.sh generate-data 2000000

# 验证数据量
docker compose exec postgres psql -U benchmark -c "SELECT count(*) FROM orders;"
```

## 测试工具

### wrk

HTTP 基准测试工具，用于高并发性能测试。

#### 安装

```bash
# macOS
brew install wrk

# Ubuntu
sudo apt-get install wrk

# CentOS
sudo yum install wrk
```

#### 验证安装

```bash
wrk --version
```

### curl

用于 API 功能测试和单次请求测试。

### jq

JSON 处理工具，用于格式化输出。

```bash
# macOS
brew install jq

# Ubuntu
sudo apt-get install jq
```

## 测试场景

### 1. 查询接口性能测试

测试订单查询接口在不同并发级别下的性能表现。

#### 测试指标

- QPS (Queries Per Second)
- 平均延迟
- P50/P75/P90/P99 延迟
- 错误率

#### 测试参数

| 并发级别 | 连接数 | 线程数 | 持续时间 |
|---------|--------|--------|---------|
| 单用户 | 1 | 1 | 30s |
| 低并发 | 10 | 4 | 30s |
| 中等并发 | 50 | 8 | 30s |
| 高并发 | 100 | 16 | 30s |

### 2. 同步导出性能测试

测试同步导出在不同数据量下的性能表现。

#### 测试指标

- 导出时间
- 导出速度 (条/秒)
- 内存占用
- 文件大小

#### 测试参数

| 数据量 | 格式 | 说明 |
|--------|------|------|
| 1 万条 | CSV/Excel | 基准测试 |
| 10 万条 | CSV/Excel | 中等数据量 |
| 50 万条 | CSV/Excel | 大数据量 |
| 100 万条 | CSV/Excel | 超大数据量 |

### 3. 异步导出性能测试

测试异步导出的任务处理能力和资源占用。

#### 测试指标

- 任务创建时间
- 任务处理时间
- 内存占用峰值
- 并发任务数

### 4. 流式导出性能测试

测试流式导出的性能和稳定性。

#### 测试指标

- 首字节时间
- 传输速度
- 内存占用
- 稳定性

## 测试执行

### 使用测试脚本

项目提供了完整的测试脚本，位于 `benchmark/scripts/` 目录。

#### 快速测试

```bash
cd benchmark/scripts

# 运行快速测试（查询接口，所有服务，中等并发）
./run_all.sh quick
```

#### 完整测试

```bash
# 运行完整测试套件
./run_all.sh full
```

#### 单项测试

```bash
# 查询接口测试 - Java 服务 - 高并发
./benchmark.sh -t query -s java -c high

# 同步导出测试 - 所有服务 - 低并发
./benchmark.sh -t sync -s all -c low

# 异步导出测试 - Golang 服务 - 中等并发
./benchmark.sh -t async -s golang -c medium

# 流式导出测试 - Python 服务 - 单用户
./benchmark.sh -t stream -s python -c single
```

#### 带筛选条件测试

```bash
# 带时间范围筛选
./benchmark.sh -t query -s java -c medium \
    --start-date 2024-01-01 \
    --end-date 2024-06-30

# 带状态筛选
./benchmark.sh -t query -s rust -c medium \
    --status paid

# 带金额范围筛选
./benchmark.sh -t query -s golang -c medium \
    --min-amount 100 \
    --max-amount 1000

# 组合筛选
./benchmark.sh -t query -s python -c medium \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --status paid \
    --min-amount 100 \
    --max-amount 10000 \
    --region "北京"
```

### 手动测试

#### 查询接口测试

```bash
# 单次请求测试
curl -H "X-API-Key: benchmark-api-key-2024" \
  "http://localhost:8080/api/v1/orders?page=1&pageSize=20"

# 使用 wrk 进行压力测试
wrk -t4 -c50 -d30s \
  -H "X-API-Key: benchmark-api-key-2024" \
  "http://localhost:8080/api/v1/orders?page=1&pageSize=20"
```

#### 同步导出测试

```bash
# CSV 导出
time curl -X POST \
  -H "X-API-Key: benchmark-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"format":"csv","limit":100000}' \
  http://localhost:8080/api/v1/exports/sync \
  --output test.csv

# Excel 导出
time curl -X POST \
  -H "X-API-Key: benchmark-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"format":"xlsx","limit":100000}' \
  http://localhost:8080/api/v1/exports/sync \
  --output test.xlsx
```

#### 异步导出测试

```bash
# 创建异步导出任务
TASK_ID=$(curl -s -X POST \
  -H "X-API-Key: benchmark-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"format":"csv","limit":1000000}' \
  http://localhost:8080/api/v1/exports/async | jq -r '.data.taskId')

echo "Task ID: $TASK_ID"

# 查询任务状态
curl -H "X-API-Key: benchmark-api-key-2024" \
  "http://localhost:8080/api/v1/exports/tasks/$TASK_ID" | jq

# 等待任务完成并下载
while true; do
  STATUS=$(curl -s -H "X-API-Key: benchmark-api-key-2024" \
    "http://localhost:8080/api/v1/exports/tasks/$TASK_ID" | jq -r '.data.status')
  
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "completed" ]; then
    TOKEN=$(curl -s -H "X-API-Key: benchmark-api-key-2024" \
      "http://localhost:8080/api/v1/exports/tasks/$TASK_ID" | jq -r '.data.downloadToken')
    
    curl -H "X-API-Key: benchmark-api-key-2024" \
      "http://localhost:8080/api/v1/exports/download/$TOKEN" \
      --output async_export.csv
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Task failed"
    break
  fi
  
  sleep 2
done
```

#### 流式导出测试

```bash
# 流式导出
time curl -X POST \
  -H "X-API-Key: benchmark-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"format":"csv","limit":1000000}' \
  http://localhost:8080/api/v1/exports/stream \
  --output stream_export.csv
```

### 并发测试

#### 多服务并发测试

```bash
# 并发测试所有服务
for service in java golang python rust; do
  for i in {1..10}; do
    curl -s -H "X-API-Key: benchmark-api-key-2024" \
      "http://localhost:808$((8080 + $(echo $service | sed 's/java/0/;s/golang/1/;s/python/2/;s/rust/3/')))/api/v1/orders?page=1&pageSize=20" \
      > /dev/null &
  done
done
wait
```

## 结果分析

### 收集测试结果

```bash
cd benchmark/scripts

# 收集所有测试结果
./collect_results.sh collect

# 生成性能对比报告
./collect_results.sh compare

# 导出为 Excel
./collect_results.sh export

# 执行所有操作
./collect_results.sh all
```

### 结果文件

测试结果保存在 `benchmark/results/` 目录：

```
benchmark/results/
├── query_java_medium_20240101_120000.txt    # 原始 wrk 输出
├── sync_golang_low_20240101_120100.txt
├── analysis/
│   ├── results_20240101_120000.csv          # CSV 格式结果
│   ├── summary_20240101_120000.json         # JSON 格式汇总
│   └── comparison_20240101_120000.md        # 性能对比报告
└── charts/
    └── performance_chart.png                 # 性能图表
```

### 分析指标

#### 查询接口

| 指标 | 说明 | 计算方式 |
|------|------|---------|
| QPS | 每秒查询数 | 请求数 / 总时间 |
| 平均延迟 | 平均响应时间 | 所有请求延迟的平均值 |
| P50 延迟 | 50% 请求的延迟 | 第 50 百分位 |
| P99 延迟 | 99% 请求的延迟 | 第 99 百分位 |
| 错误率 | 失败请求比例 | 失败请求数 / 总请求数 |

#### 导出接口

| 指标 | 说明 | 计算方式 |
|------|------|---------|
| 导出时间 | 完成导出的总时间 | 结束时间 - 开始时间 |
| 导出速度 | 每秒导出记录数 | 记录数 / 导出时间 |
| 文件大小 | 导出文件大小 | 文件字节数 |
| 内存峰值 | 导出过程最大内存 | 监控系统记录 |

### 查看结果

```bash
# 查看最新测试结果
ls -lt benchmark/results/*.txt | head -5

# 查看特定测试结果
cat benchmark/results/query_java_medium_*.txt

# 查看性能对比报告
cat benchmark/results/analysis/comparison_*.md

# 使用 Excel 查看
open benchmark/results/analysis/results_*.xlsx
```

## 性能基准

### 查询接口基准

| 服务 | 并发级别 | 目标 QPS | 目标 P99 延迟 |
|------|---------|---------|--------------|
| Java | medium | > 1000 | < 100ms |
| Golang | medium | > 1200 | < 80ms |
| Python | medium | > 800 | < 120ms |
| Rust | medium | > 1500 | < 60ms |

### 导出接口基准

| 服务 | 导出方式 | 数据量 | 目标时间 | 目标速度 |
|------|---------|--------|---------|---------|
| Java | 同步 | 10 万条 | < 10s | > 10000 条/秒 |
| Golang | 同步 | 10 万条 | < 8s | > 12500 条/秒 |
| Python | 同步 | 10 万条 | < 12s | > 8300 条/秒 |
| Rust | 同步 | 10 万条 | < 6s | > 16600 条/秒 |

### 资源使用基准

| 服务 | CPU 使用率 | 内存使用 | 说明 |
|------|-----------|---------|------|
| Java | < 80% | < 1.5 GB | 高负载下 |
| Golang | < 70% | < 500 MB | 高负载下 |
| Python | < 85% | < 1 GB | 高负载下 |
| Rust | < 60% | < 300 MB | 高负载下 |

## 最佳实践

### 测试前准备

1. **清理环境**

```bash
# 清理旧数据
docker compose exec postgres psql -U benchmark -c "TRUNCATE orders CASCADE;"

# 重启服务
./scripts/start.sh restart
```

2. **检查系统资源**

```bash
# 检查内存
free -h

# 检查磁盘
df -h

# 检查 CPU
top -l 1 | head -n 10
```

3. **预热服务**

```bash
# 发送预热请求
for i in {1..10}; do
  curl -s -H "X-API-Key: benchmark-api-key-2024" \
    "http://localhost:8080/api/v1/orders?page=1&pageSize=20" > /dev/null
done
```

### 测试执行

1. **从低并发开始**

   先进行低并发测试，确保服务正常，再逐步增加并发。

2. **保持测试间隔**

   每次测试之间等待 30-60 秒，让系统恢复稳定状态。

3. **监控系统状态**

```bash
# 实时监控容器资源
docker stats

# 查看服务日志
./scripts/start.sh logs -f java-api
```

4. **记录异常情况**

   记录测试过程中的错误、超时等异常情况。

### 结果分析

1. **关注 P99 延迟**

   P99 延迟更能反映系统的稳定性。

2. **对比不同服务**

   在相同条件下对比不同服务的性能差异。

3. **分析瓶颈**

   通过监控数据分析性能瓶颈（CPU、内存、I/O、网络）。

4. **多次测试取平均值**

   每个测试场景至少执行 3 次，取平均值。

### 测试报告

测试完成后，生成详细的测试报告，包括：

1. 测试环境信息
2. 测试场景说明
3. 性能数据对比
4. 资源使用情况
5. 性能瓶颈分析
6. 优化建议

## 故障排查

### wrk 安装失败

```bash
# macOS
brew install wrk

# 如果失败，尝试从源码编译
git clone https://github.com/wg/wrk.git
cd wrk
make
sudo cp wrk /usr/local/bin/
```

### 服务未启动

```bash
# 检查服务状态
docker compose ps

# 查看服务日志
docker compose logs java-api

# 重启服务
docker compose restart java-api
```

### 连接被拒绝

```bash
# 检查端口
netstat -tlnp | grep 8080

# 检查防火墙
sudo ufw status

# 检查 Docker 网络
docker network ls
docker network inspect benchmark-network
```

### 性能异常低

1. 检查数据库连接池配置
2. 检查系统资源使用
3. 检查网络延迟
4. 查看服务日志是否有错误

### 内存溢出

```bash
# 调整内存限制
# 编辑 docker-compose.yml 中的 deploy.resources

# 调整 JVM 参数
# 编辑 .env 文件
JAVA_OPTS=-Xms512m -Xmx1024m
```

## 附录

### wrk 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| -t | 线程数 | -t4 |
| -c | 连接数 | -c50 |
| -d | 持续时间 | -d30s |
| -H | 请求头 | -H "X-API-Key: xxx" |
| -s | Lua 脚本 | -s script.lua |
| --timeout | 超时时间 | --timeout 30s |

### 测试脚本参数

```bash
# benchmark.sh 参数
-t, --test-type      # 测试类型: query, sync, async, stream
-s, --service        # 服务: java, golang, python, rust, all
-c, --concurrency    # 并发级别: single, low, medium, high
-d, --duration       # 持续时间
-n, --data-size      # 数据量
--start-date         # 开始日期
--end-date           # 结束日期
--status             # 订单状态
--min-amount         # 最小金额
--max-amount         # 最大金额
--user-id            # 用户 ID
--region             # 地区
--format             # 导出格式
-o, --output         # 输出文件
```

### 性能测试清单

- [ ] 环境准备完成
- [ ] 服务启动正常
- [ ] 测试数据生成完成
- [ ] 查询接口测试完成
- [ ] 同步导出测试完成
- [ ] 异步导出测试完成
- [ ] 流式导出测试完成
- [ ] 结果收集完成
- [ ] 性能报告生成完成
