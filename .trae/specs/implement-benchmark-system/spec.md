# 百万级数据导出跨语言性能基准测试系统 Spec

## Why
构建一个完整的基准测试平台，对比 Java、Golang、Python、Rust 四种语言在百万级数据导出场景下的性能表现，为技术选型提供数据支撑。

## What Changes
- 创建 PostgreSQL 17+ 数据库及优化的表结构设计
- 实现 2000 万条订单测试数据的生成工具
- 开发 Vue.js 前端服务（数据查询、导出、任务管理）
- 开发 4 个后端服务（Java/Spring Boot、Golang/Gin、Python/FastAPI、Rust/Actix-web）
- 实现三种导出方式（同步、异步、流式）
- 实现 SSE 实时进度推送
- 配置 Docker Compose 容器编排
- 实现性能监控和结果可视化

## Impact
- Affected specs: 新建完整项目
- Affected code: 全新代码库

---

## ADDED Requirements

### Requirement: 数据库基础设施
系统 SHALL 提供 PostgreSQL 17+ 数据库服务，包含优化的容器配置。

#### Scenario: 数据库启动
- **WHEN** 执行 docker-compose up
- **THEN** PostgreSQL 服务正常启动，端口 5432 可访问

#### Scenario: 表结构初始化
- **WHEN** 数据库首次启动
- **THEN** 自动创建 orders 表，包含 30 个字段，7 个索引

### Requirement: 测试数据生成
系统 SHALL 提供数据生成工具，支持生成 2000 万条订单记录。

#### Scenario: 初始数据生成
- **WHEN** 执行数据生成命令
- **THEN** 生成 2000 万条符合规则的订单数据
- **AND** 时间分布符合 2020-2024 年占比要求
- **AND** 订单状态分布符合预设比例

#### Scenario: 增量数据生成
- **WHEN** 指定时间范围生成数据
- **THEN** 仅生成该时间范围内的订单数据

### Requirement: 前端服务
系统 SHALL 提供 Vue.js 前端界面，支持数据查询和导出操作。

#### Scenario: 数据查询
- **WHEN** 用户输入查询条件
- **THEN** 返回分页结果，默认每页 20 条

#### Scenario: 数据导出
- **WHEN** 用户选择导出条件和格式
- **THEN** 支持同步/异步/流式三种导出方式
- **AND** 支持 CSV 和 Excel 两种格式

#### Scenario: 异步任务管理
- **WHEN** 用户发起异步导出
- **THEN** 返回任务 ID
- **AND** 通过 SSE 实时推送进度
- **AND** 支持页面刷新后查询任务状态

### Requirement: API 认证
系统 SHALL 通过 API Key 进行身份验证，不做登录认证。

#### Scenario: 请求认证
- **WHEN** 前端发起 API 请求
- **THEN** 请求头包含 X-API-Key
- **AND** 服务端验证 API Key 有效性

### Requirement: Java 后端服务
系统 SHALL 提供 Java 后端服务，技术栈符合规范要求。

#### Scenario: 服务启动
- **WHEN** 执行 docker-compose up
- **THEN** Java 服务在端口 8080 启动
- **AND** 使用 JDK 25 + Spring Boot 4+ + JOOQ + HikariCP

#### Scenario: 导出功能
- **WHEN** 调用导出接口
- **THEN** 支持同步/异步/流式三种方式
- **AND** 使用 Apache POI 生成 Excel

### Requirement: Golang 后端服务
系统 SHALL 提供 Golang 后端服务，技术栈符合规范要求。

#### Scenario: 服务启动
- **WHEN** 执行 docker-compose up
- **THEN** Golang 服务在端口 8081 启动
- **AND** 使用最新 Go + Gin + GORM

#### Scenario: 导出功能
- **WHEN** 调用导出接口
- **THEN** 支持同步/异步/流式三种方式
- **AND** 使用 excelize 生成 Excel

### Requirement: Python 后端服务
系统 SHALL 提供 Python 后端服务，技术栈符合规范要求。

#### Scenario: 服务启动
- **WHEN** 执行 docker-compose up
- **THEN** Python 服务在端口 8082 启动
- **AND** 使用最新 Python + FastAPI + Tortoise ORM + gunicorn + Uvicorn

#### Scenario: 导出功能
- **WHEN** 调用导出接口
- **THEN** 支持同步/异步/流式三种方式
- **AND** 使用 openpyxl 生成 Excel

### Requirement: Rust 后端服务
系统 SHALL 提供 Rust 后端服务，技术栈符合规范要求。

#### Scenario: 服务启动
- **WHEN** 执行 docker-compose up
- **THEN** Rust 服务在端口 8083 启动
- **AND** 使用最新 Rust + Actix-web + Diesel + Tokio

#### Scenario: 导出功能
- **WHEN** 调用导出接口
- **THEN** 支持同步/异步/流式三种方式
- **AND** 使用 xlsxwriter 生成 Excel

### Requirement: RESTful API 接口
系统 SHALL 提供统一的 RESTful API 接口，四个后端服务接口一致。

#### Scenario: 查询接口
- **WHEN** GET /api/v1/orders
- **THEN** 支持分页、时间范围、状态、金额、用户ID、订单编号筛选

#### Scenario: 同步导出接口
- **WHEN** POST /api/v1/exports/sync
- **THEN** 返回文件流

#### Scenario: 异步导出接口
- **WHEN** POST /api/v1/exports/async
- **THEN** 返回任务 ID 和状态

#### Scenario: 任务状态查询
- **WHEN** GET /api/v1/exports/tasks/{task_id}
- **THEN** 返回任务进度和下载链接

#### Scenario: SSE 进度推送
- **WHEN** GET /api/v1/exports/sse/{task_id}
- **THEN** 返回 SSE 事件流

#### Scenario: 文件下载
- **WHEN** GET /api/v1/exports/download/{token}
- **THEN** 返回文件流

#### Scenario: 流式导出
- **WHEN** POST /api/v1/exports/stream
- **THEN** 返回 SSE 流式数据

### Requirement: 容器编排
系统 SHALL 使用 Docker Compose 编排所有服务。

#### Scenario: 一键启动
- **WHEN** 执行 docker-compose up -d
- **THEN** 所有服务按依赖顺序启动
- **AND** 端口映射正确

### Requirement: 性能测试
系统 SHALL 支持多维度性能测试。

#### Scenario: 并发测试
- **WHEN** 执行压测脚本
- **THEN** 支持单用户、低并发(5-10)、中并发(20-50)、高并发(100+)测试

#### Scenario: 数据量测试
- **WHEN** 执行导出测试
- **THEN** 支持 100万、200万、500万、1000万、2000万 数据量

### Requirement: 监控与评估
系统 SHALL 提供性能监控和结果可视化。

#### Scenario: 资源监控
- **WHEN** 测试运行中
- **THEN** 采集 CPU、内存、网络 I/O、数据库连接数

#### Scenario: 结果输出
- **WHEN** 测试完成
- **THEN** 自动生成可视化图表
- **AND** 包含响应时间(P50/P90/P95/P99)、吞吐量(QPS)、数据导出速率
