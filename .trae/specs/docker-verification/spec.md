# Docker 端到端验证 Spec

## Why

benchmark-IO 项目已完成全部代码开发（Java/Golang/Python/Rust 后端 + Vue 前端 + 数据生成工具 + PostgreSQL），但尚未在本地 Docker 环境中进行完整的端到端验证。需要按步骤依次验证每个服务的 Docker 构建与启动，确保所有服务能正常运行、端口可达、数据库连接正常，为后续性能基准测试奠定基础。

## What Changes

- **不修改任何业务代码**，仅进行 Docker 环境下的构建、启动、验证操作
- 按顺序执行 4 个阶段的验证：数据库 → 数据生成 → 后端服务（逐个）→ 前端
- 验证通过后及时关闭非必要容器以节省内存资源
- 所有构建尽量在 Docker 内完成（multi-stage build），避免本地依赖问题

## Impact

- Affected specs: 无（纯验证操作）
- Affected code: 涉及以下服务的 Dockerfile 与 docker-compose.yml 配置：
  - `postgres` (端口 5432)
  - `data-generator` (init/generate_data)
  - `java-api` (端口 8080)
  - `golang-api` (端口 8081)
  - `python-api` (端口 8082)
  - `rust-api` (端口 8083)
  - `frontend` (端口 80)

---

## ADDED Requirements

### Requirement: PostgreSQL 数据库启动验证

系统 SHALL 能通过 Docker Compose 启动 PostgreSQL 17 数据库服务，且：

- **WHEN** 执行 `docker compose up -d postgres`
- **THEN** 数据库容器健康检查通过（`pg_isready`），端口 5432 可访问，init.sql 自动执行完成，`orders` 表及索引已创建

### Requirement: 数据生成脚本验证

系统 SHALL 能在 Docker 容器内执行数据生成脚本并成功写入数据库：

- **WHEN** 数据库就绪后，使用 `docker compose run --rm data-generator` 执行数据生成
- **THEN** 脚本正常完成，数据库中 orders 表有数据插入（可通过 SQL 查询确认行数）

### Requirement: 后端服务逐一构建与验证

系统 SHALL 能在 Docker 中依次构建并启动各后端服务，每个服务验证通过后可关闭：

#### Scenario: Java 服务验证
- **WHEN** 执行 `docker compose build java-api && docker compose up -d java-api`
- **THEN** 容器启动成功，健康检查通过，端口 8080 可访问，GET /actuator/health 返回 UP，API Key 认证正常，能查询数据库中的订单数据

#### Scenario: Golang 服务验证
- **WHEN** 执行 `docker compose build golang-api && docker compose up -d golang-api`
- **THEN** 容器启动成功，健康检查通过，端口 8081 可访问，GET /health 返回正常，API Key 认证正常，能查询数据库中的订单数据

#### Scenario: Python 服务验证
- **WHEN** 执行 `docker compose build python-api && docker compose up -d python-api`
- **THEN** 容器启动成功，健康检查通过，端口 8082 可访问，GET /health 返回正常，API Key 认证正常，能查询数据库中的订单数据

#### Scenario: Rust 服务验证
- **WHEN** 执行 `docker compose build rust-api && docker compose up -d rust-api`
- **THEN** 容器启动成功，健康检查通过，端口 8083 可访问，GET /health 返回正常，API Key 认证正常，能查询数据库中的订单数据

### Requirement: 前端服务构建与验证

系统 SHALL 能在 Docker 中构建前端服务并通过浏览器访问：

- **WHEN** 至少一个后端服务运行时，执行 `docker compose build frontend && docker compose up -d frontend`
- **THEN** Nginx 容器启动成功，端口 80 可访问，前端页面正常渲染，能切换后端服务并查询订单数据

### Requirement: 验证后资源清理

系统 SHALL 在每步验证完成后支持关闭非必要容器以释放内存：

- **WHEN** 某个后端服务验证完毕
- **THEN** 可通过 `docker compose stop <service>` 关闭该服务容器，数据库保持运行供后续服务验证使用
- **WHEN** 全部验证完成
- **THEN** 可通过 `docker compose down` 关闭所有服务
