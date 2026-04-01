# 监控系统配置

多语言基准测试系统的监控解决方案，基于 Prometheus + Grafana + cAdvisor 构建。

## 目录结构

```
monitor/
├── prometheus.yml           # Prometheus 主配置文件
├── datasources/
│   └── prometheus.yml       # Grafana 数据源配置
├── dashboards/
│   ├── dashboard.yml        # Grafana Dashboard 配置
│   └── benchmark-dashboard.json  # 自定义监控面板
└── README.md               # 本文档
```

## 监控组件

### 1. Prometheus
- **端口**: 9090
- **功能**: 时序数据库，负责指标采集和存储
- **配置**: 
  - 抓取间隔: 15s
  - 数据保留: 30d
  - 抓取目标: cAdvisor、PostgreSQL Exporter、各后端服务

### 2. cAdvisor
- **端口**: 8084
- **功能**: 容器资源监控
- **监控指标**:
  - CPU 使用率
  - 内存使用
  - 网络 I/O
  - 磁盘 I/O

### 3. Grafana
- **端口**: 3000
- **默认账号**: admin / admin123
- **功能**: 可视化监控面板
- **数据源**: Prometheus
- **Dashboard**: 自动加载 Benchmark 监控面板

### 4. PostgreSQL Exporter
- **端口**: 9187
- **功能**: PostgreSQL 数据库监控
- **监控指标**:
  - 连接数
  - 查询性能
  - 事务数

## 监控面板

### 容器资源监控
- 容器 CPU 使用率
- 容器内存使用
- 容器网络 I/O
- 容器磁盘 I/O

### 数据库监控
- PostgreSQL 连接数
- PostgreSQL 查询性能
- PostgreSQL 事务数

### 应用性能监控
- 请求响应时间 (P50/P95/P99)
- QPS (每秒请求数)
- 错误率

### 多语言服务对比
- 平均响应时间对比
- QPS 对比
- 错误率对比
- 内存使用对比

## 快速启动

### 1. 启动监控服务

```bash
# 启动所有服务（包括监控）
docker-compose up -d

# 仅启动监控服务
docker-compose up -d prometheus cadvisor grafana postgres_exporter
```

### 2. 访问监控界面

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin / admin123)
- **cAdvisor**: http://localhost:8084

### 3. 查看 Dashboard

1. 打开 Grafana: http://localhost:3000
2. 登录后自动跳转到 Dashboard
3. 选择 "Benchmark 监控面板"

## 配置说明

### Prometheus 配置 (prometheus.yml)

```yaml
global:
  scrape_interval: 15s      # 抓取间隔
  evaluation_interval: 15s  # 规则评估间隔

scrape_configs:
  - job_name: 'prometheus'  # 自身监控
  - job_name: 'cadvisor'    # 容器监控
  - job_name: 'postgres'    # 数据库监控
  - job_name: 'java-api'    # Java 服务
  - job_name: 'golang-api'  # Golang 服务
  - job_name: 'python-api'  # Python 服务
  - job_name: 'rust-api'    # Rust 服务
```

### Grafana 数据源配置 (datasources/prometheus.yml)

自动配置 Prometheus 数据源，无需手动添加。

### Dashboard 配置 (dashboards/dashboard.yml)

自动加载 Dashboard JSON 文件，无需手动导入。

## 应用指标集成

### Java (Spring Boot)

需要在 `build.gradle` 添加依赖：

```gradle
implementation 'org.springframework.boot:spring-boot-starter-actuator'
implementation 'io.micrometer:micrometer-registry-prometheus'
```

配置 `application.yml`：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  metrics:
    tags:
      application: java-api
```

### Golang

使用 `prometheus/client_golang` 库：

```go
import (
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
    http.Handle("/metrics", promhttp.Handler())
}
```

### Python (FastAPI)

使用 `prometheus-fastapi-instrumentator`：

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### Rust (Actix-web)

使用 `actix-web-prom`：

```rust
use actix_web_prom::PrometheusMetricsBuilder;

let prometheus = PrometheusMetricsBuilder::new("api")
    .endpoint("/metrics")
    .build()
    .unwrap();
```

## 告警配置（可选）

可以在 Prometheus 中配置告警规则，示例：

```yaml
# alert.rules.yml
groups:
  - name: benchmark_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
```

## 性能优化建议

### Prometheus
- 调整数据保留时间：`--storage.tsdb.retention.time=30d`
- 增加内存限制：`--storage.tsdb.retention.size=10GB`
- 使用远程存储长期保存数据

### Grafana
- 配置 Dashboard 自动刷新间隔
- 使用变量动态切换服务
- 设置合理的查询时间范围

### cAdvisor
- 监控大量容器时增加资源限制
- 调整采集频率避免性能影响

## 故障排查

### Prometheus 无法抓取指标

1. 检查目标服务是否运行：`docker-compose ps`
2. 检查网络连接：`docker-compose exec prometheus ping java-api`
3. 查看 Prometheus targets 页面：http://localhost:9090/targets

### Grafana 无法显示数据

1. 检查数据源配置：Settings -> Data Sources
2. 测试数据源连接
3. 查看 Dashboard 查询语句是否正确

### 指标数据缺失

1. 确认应用已集成 Prometheus 客户端库
2. 检查 `/metrics` 端点是否可访问
3. 查看 Prometheus 日志：`docker-compose logs prometheus`

## 监控最佳实践

1. **指标命名规范**
   - 使用小写和下划线
   - 包含单位信息（如 `_seconds`, `_bytes`）
   - 添加有意义的标签

2. **Dashboard 设计**
   - 分组相关指标
   - 使用合理的图表类型
   - 添加说明文档

3. **告警策略**
   - 设置合理的阈值
   - 避免告警疲劳
   - 分级告警（warning/critical）

4. **数据保留**
   - 根据需求调整保留时间
   - 定期清理历史数据
   - 考虑使用远程存储

## 参考资源

- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [cAdvisor GitHub](https://github.com/google/cadvisor)
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)
