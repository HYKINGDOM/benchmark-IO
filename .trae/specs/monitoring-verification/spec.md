# 监控服务验证 Spec

## Why

benchmark-IO 项目的 [验证步骤.md](../../docs/验证步骤.md) 明确要求验证监控服务（第3条、第6条），但之前的 docker-verification 仅覆盖了数据库+数据生成+4个后端+前端，未包含 Prometheus/Grafana/cAdvisor/postgres_exporter 四个监控组件的启动与端到端联动验证。

## What Changes

- **不修改任何业务代码**，仅进行 Docker 环境下的监控服务启动、配置验证和端到端联动测试
- 按顺序启动并验证 4 个监控服务：Prometheus → postgres_exporter → cAdvisor → Grafana
- 验证 Prometheus 能正确采集各 target 的指标（自身 + 数据库 exporter + 容器指标）
- 验证 Grafana 能正常连接 Prometheus 数据源并加载 Dashboard
- 验证后端服务启动后能被 Prometheus 正常抓取 metrics

## Impact

- Affected specs: 扩展 docker-verification 覆盖范围
- Affected code/配置:
  - `monitor/prometheus.yml` — scrape 配置（7 个 job）
  - `monitor/datasources/prometheus.yml` — Grafana 数据源
  - `monitor/dashboards/dashboard.yml` + `benchmark-dashboard.json` — Dashboard 定义
  - `docker-compose.yml` — prometheus/postgres_exporter/cadvisor/grafana 服务定义

---

## ADDED Requirements

### Requirement: Prometheus 启动与基础验证

系统 SHALL 能通过 Docker Compose 启动 Prometheus 服务：

- **WHEN** 执行 `docker compose up -d prometheus`
- **THEN** 容器启动成功，端口 9090 可访问，`/-/healthy` 返回 200，配置文件正确加载（7 个 scrape job），自身 target 状态为 up

### Requirement: PostgreSQL Exporter 启动与验证

系统 SHALL 能启动 postgres_exporter 并连接到 PostgreSQL：

- **WHEN** 执行 `docker compose up -d postgres_exporter`
- **THEN** 容器启动成功，端口 9187 可访问，`/metrics` 返回 200 且包含 pg_ 开头的数据库指标

### Requirement: cAdvisor 启动与验证

系统 SHALL 能启动 cAdvisor 并采集容器资源指标：

- **WHEN** 执行 `docker compose up -d cadvisor`
- **THEN** 容器启动成功（需 privileged 模式），端口 8084 可访问，`/metrics` 返回 container_* 相关指标

### Requirement: Grafana 启动与 Dashboard 验证

系统 SHALL 能启动 Grafana 并自动加载预配置的数据源和 Dashboard：

- **WHEN** 执行 `docker compose up -d grafana`
- **THEN** 容器启动成功，端口 3000 可访问，登录页面可打开，Prometheus 数据源连接正常（proxy 模式），Benchmark Dashboard 自动加载并可查询指标

### Requirement: 监控服务端到端联动验证

系统 SHALL 在至少一个后端服务运行时，实现完整的监控数据链路：

- **WHEN** 后端服务运行 + 所有监控服务运行
- **THEN** Prometheus Targets 页面中 postgres job 为 up，Prometheus 能查询到 pg_stat_database_xact_commit 等 PG 指标；Grafana Dashboard 中数据库监控面板有数据显示；容器监控面板显示 benchmark-* 容器的 CPU/内存指标
