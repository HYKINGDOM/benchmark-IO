# Checklist

## Phase 1: 基础设施搭建

### 项目结构
- [ ] 项目目录结构完整创建
- [ ] docker-compose.yml 文件存在且格式正确

### 数据库
- [ ] PostgreSQL 17+ Docker 镜像配置正确
- [ ] postgresql.conf 性能优化参数配置完成
- [ ] pg_hba.conf 访问控制配置正确
- [ ] init.sql 建表脚本包含 30 个字段
- [ ] init.sql 包含 7 个索引定义（主键、唯一、BTree、复合索引）
- [ ] Docker Compose 中 PostgreSQL 服务配置正确（端口 5432）

### 数据生成
- [ ] 数据生成工具可执行
- [ ] 生成的订单编号格式正确（ORD + 时间戳 + 6位随机数）
- [ ] 用户ID范围正确（1 ~ 20000000）
- [ ] 手机号符合规范（13/14/15/16/17/18/19 开头）
- [ ] 身份证号格式正确（含生日和校验位）
- [ ] 时间分布符合要求（2020年10%/2021年15%/2022年20%/2023年25%/2024年30%）
- [ ] 订单状态分布正确（待支付15%/已支付50%/已取消15%/已退款5%/已完成15%）
- [ ] 支持 2000 万条数据生成
- [ ] 增量数据生成功能正常
- [ ] 数据清理脚本可用

---

## Phase 2: 后端服务

### Java 服务
- [ ] JDK 25 版本配置正确
- [ ] Spring Boot 4+ 依赖配置完成
- [ ] JOOQ 配置正确且代码生成成功
- [ ] HikariCP 连接池配置优化
- [ ] API Key 认证中间件实现
- [ ] GET /api/v1/orders 接口正常（支持所有筛选参数）
- [ ] POST /api/v1/exports/sync 同步导出正常
- [ ] POST /api/v1/exports/async 异步导出正常
- [ ] GET /api/v1/exports/tasks/{task_id} 任务查询正常
- [ ] GET /api/v1/exports/sse/{task_id} SSE 推送正常
- [ ] GET /api/v1/exports/download/{token} 文件下载正常
- [ ] POST /api/v1/exports/stream 流式导出正常
- [ ] CSV 导出功能正常
- [ ] Excel 导出功能正常（Apache POI）
- [ ] 异步任务管理正常（Spring @Async）
- [ ] Dockerfile 构建成功
- [ ] 服务在端口 8080 正常启动

### Golang 服务
- [ ] Go 最新稳定版配置
- [ ] Gin 框架依赖配置完成
- [ ] GORM 配置正确
- [ ] GORM 连接池配置优化
- [ ] API Key 认证中间件实现
- [ ] GET /api/v1/orders 接口正常（支持所有筛选参数）
- [ ] POST /api/v1/exports/sync 同步导出正常
- [ ] POST /api/v1/exports/async 异步导出正常
- [ ] GET /api/v1/exports/tasks/{task_id} 任务查询正常
- [ ] GET /api/v1/exports/sse/{task_id} SSE 推送正常
- [ ] GET /api/v1/exports/download/{token} 文件下载正常
- [ ] POST /api/v1/exports/stream 流式导出正常
- [ ] CSV 导出功能正常
- [ ] Excel 导出功能正常（excelize）
- [ ] 异步任务管理正常（Goroutine + Channel）
- [ ] Dockerfile 构建成功
- [ ] 服务在端口 8081 正常启动

### Python 服务
- [ ] Python 最新版配置
- [ ] FastAPI 依赖配置完成
- [ ] Tortoise ORM 配置正确（原生异步）
- [ ] 数据库连接池配置优化
- [ ] API Key 认证中间件实现
- [ ] GET /api/v1/orders 接口正常（支持所有筛选参数）
- [ ] POST /api/v1/exports/sync 同步导出正常
- [ ] POST /api/v1/exports/async 异步导出正常
- [ ] GET /api/v1/exports/tasks/{task_id} 任务查询正常
- [ ] GET /api/v1/exports/sse/{task_id} SSE 推送正常
- [ ] GET /api/v1/exports/download/{token} 文件下载正常
- [ ] POST /api/v1/exports/stream 流式导出正常
- [ ] CSV 导出功能正常
- [ ] Excel 导出功能正常（openpyxl）
- [ ] 异步任务管理正常（asyncio）
- [ ] gunicorn + Uvicorn 配置正确
- [ ] Dockerfile 构建成功
- [ ] 服务在端口 8082 正常启动

### Rust 服务
- [ ] Rust 最新稳定版配置
- [ ] Actix-web 依赖配置完成
- [ ] Diesel 配置正确（同步模式）
- [ ] Diesel 连接池配置优化
- [ ] API Key 认证中间件实现
- [ ] GET /api/v1/orders 接口正常（支持所有筛选参数）
- [ ] POST /api/v1/exports/sync 同步导出正常
- [ ] POST /api/v1/exports/async 异步导出正常
- [ ] GET /api/v1/exports/tasks/{task_id} 任务查询正常
- [ ] GET /api/v1/exports/sse/{task_id} SSE 推送正常
- [ ] GET /api/v1/exports/download/{token} 文件下载正常
- [ ] POST /api/v1/exports/stream 流式导出正常
- [ ] CSV 导出功能正常
- [ ] Excel 导出功能正常（xlsxwriter）
- [ ] 异步任务管理正常（Tokio）
- [ ] Dockerfile 构建成功
- [ ] 服务在端口 8083 正常启动

---

## Phase 3: 前端服务

### Vue.js 前端
- [ ] Vue 3 + Vite 项目创建成功
- [ ] Element Plus UI 组件库配置完成
- [ ] Axios HTTP 客户端配置完成
- [ ] Pinia 状态管理配置完成
- [ ] API Key 环境变量配置正确
- [ ] 请求拦截器正确添加 X-API-Key Header
- [ ] 数据查询页面功能完整（筛选条件、分页表格）
- [ ] 同步导出功能正常
- [ ] 异步导出功能正常（任务创建、进度展示）
- [ ] 流式导出功能正常
- [ ] SSE 进度实时推送正常
- [ ] 任务管理页面功能完整（任务列表、状态查询）
- [ ] 文件下载功能正常
- [ ] 后端服务切换功能正常（Java/Golang/Python/Rust）
- [ ] Dockerfile 构建成功（Nginx 部署）
- [ ] 服务在端口 80 正常启动

---

## Phase 4: 监控与测试

### 监控系统
- [ ] Prometheus 容器配置正确
- [ ] cAdvisor 容器资源监控配置正确
- [ ] Grafana 可视化面板配置正确
- [ ] 自定义监控面板模板创建完成
- [ ] Docker Compose 监控服务配置正确

### 性能测试
- [ ] wrk/wrk2 压测脚本可执行
- [ ] 查询接口压测脚本完成
- [ ] 同步导出压测脚本完成
- [ ] 异步导出压测脚本完成
- [ ] 流式导出压测脚本完成
- [ ] 并发测试脚本支持所有级别（单用户/低/中/高）
- [ ] 数据量测试脚本支持所有档位（100万-2000万）
- [ ] 测试结果数据采集正常

### 结果可视化
- [ ] 测试结果解析脚本可用
- [ ] 响应时间图表生成正常（P50/P90/P95/P99）
- [ ] 吞吐量图表生成正常（QPS）
- [ ] 资源消耗图表生成正常
- [ ] 多语言对比图表生成正常
- [ ] 测试报告模板创建完成

---

## Phase 5: 集成与文档

### Docker Compose 集成
- [ ] docker-compose.yml 配置完整
- [ ] 服务依赖关系配置正确（depends_on）
- [ ] 网络隔离配置正确
- [ ] 数据卷挂载配置正确
- [ ] 环境变量文件配置正确
- [ ] 一键启动脚本可用
- [ ] 所有服务可同时启动

### 文档
- [ ] 项目 README.md 编写完成
- [ ] 部署文档编写完成
- [ ] API 接口文档编写完成
- [ ] 测试指南编写完成
- [ ] 性能对比报告模板编写完成

---

## 功能验收

### 核心功能
- [ ] 四个后端服务均可正常启动和响应
- [ ] 前端可正常访问和使用
- [ ] 数据查询功能正常（支持多条件组合筛选）
- [ ] 同步导出功能正常（CSV/Excel）
- [ ] 异步导出功能正常（任务创建/进度查询/下载）
- [ ] 流式导出功能正常
- [ ] SSE 实时进度推送正常
- [ ] API Key 认证正常

### 性能要求
- [ ] 支持 2000 万数据导出
- [ ] 支持 100+ 并发测试
- [ ] 监控数据采集正常
- [ ] 测试报告自动生成
