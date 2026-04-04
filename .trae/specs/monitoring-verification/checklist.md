# Checklist

## Phase 1: Prometheus 验证

- [x] prom/prometheus:latest 镜像存在于本地
- [x] Prometheus 容器成功创建并启动
- [x] Prometheus 健康检查通过（GET /-/healthy → 200）
- [x] 端口 9090 从宿主机可访问
- [x] Prometheus 配置文件正确加载（7 个 scrape job）
- [x] Prometheus 自身 target 状态为 up
- [x] Prometheus Web UI 可通过浏览器访问 http://localhost:9090

## Phase 2: PostgreSQL Exporter 验证

- [x] prometheuscommunity/postgres-exporter:latest 镜像存在于本地
- [x] postgres_exporter 容器成功创建并启动
- [x] 端口 9187 从宿主机可访问
- [x] GET /metrics 返回 HTTP 200 且含 pg_ 指标
- [x] Prometheus targets 中 postgres job 状态为 up

## Phase 3: cAdvisor 验证

- [x] cAdvisor 镜像存在且容器启动成功（自定义 macOS exporter）
- [x] 端口 8084 从宿主机可访问
- [x] GET /metrics 返回 HTTP 200 且含 container_* 指标
- [x] Prometheus targets 中 cadvisor job 状态为 up

## Phase 4: Grafana 验证

- [x] grafana/grafana:latest 镜像存在且容器启动成功
- [x] 端口 3000 从宿主机可访问
- [x] 登录页可访问（admin/admin123）
- [x] Prometheus 数据源自动 provision 且连接正常
- [x] Benchmark Dashboard 已自动加载（18 个面板）

## Phase 5: 基础端到端联动验证

- [x] PostgreSQL 数据库运行中且有数据
- [x] Prometheus 能查询 pg_stat_database_xact_commit 等 PG 指标
- [x] Prometheus 能查询 container_memory_usage_bytes 等容器指标
- [x] Grafana Dashboard 数据库+容器面板有数据

## Phase 6: Java 后端监控验证

- [x] Java 服务镜像存在（671MB）
- [x] Java 容器启动成功（docker compose up -d java-api）
- [x] Java 健康检查通过（/actuator/health → UP）
- [x] Java 端口 8080 可访问
- [x] Java 订单查询接口返回正常数据（10000 条总记录）
- [x] Prometheus target java-api 状态为 up
- [x] Prometheus 能查询到 java-api 的 /actuator/prometheus 指标（up=1, JVM memory）

## Phase 7: Golang 后端监控验证

- [x] Golang 容器运行正常（/health → ok，unhealthy 因缺 curl 但服务正常）
- [x] Golang 端口 8081 可访问
- [x] Golang 订单查询接口返回正常数据（10000 条）
- [x] Prometheus target golang-api 状态为 up
- [x] Prometheus 能查询到 golang-api 的 /metrics 指标（go_goroutines=7 等）

## Phase 8: Python 后端监控验证

- [x] Python 容器运行正常（/health → healthy）
- [x] Python 端口 8082 可访问
- [x] Python 订单查询接口返回正常数据（10000 条）
- [x] Prometheus target python-api 状态为 up
- [x] Prometheus 能查询到 python-api 的 /metrics 指标（46 个指标序列）

## Phase 9: Rust 后端监控验证

- [x] Rust 容器运行正常（/health → OK）
- [x] Rust 端口 8083 可访问
- [x] Rust 订单查询接口返回正常数据（Total: 10000）
- [x] Prometheus target rust-api 状态为 up
- [x] Prometheus 能查询到 rust-api 的 /metrics 数据（HTTP 200, prometheus gather 已集成）

## Phase 10: 全量监控数据验证

- [x] Prometheus 全部 7 个 targets 为 **up**（prometheus/postgres/cadvisor/java-api/golang-api/python-api/rust-api）— **100%**
- [x] 各后端服务的 up 指标均为 1（Java/Golang/Python/Rust 全部在线）
- [x] PG 指标正常：pg_stat_database_xact_commit = 101,269 次
- [x] 容器指标正常：container_memory_usage_bytes = 521 MB（10 个容器序列）
- [x] Grafana Dashboard「Benchmark 监控面板」已加载（uid=benchmark-dashboard）
- [x] Grafana Prometheus 数据源连接正常（proxy 模式 @ http://prometheus:9090）
- [x] 各服务关键指标快照已记录

## Phase 11: 文档收尾

- [x] tasks.md 所有任务标记为已完成
- [x] checklist.md 所有检查项已勾选
- [x] 监控验证完整报告已生成
