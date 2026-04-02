# Checklist

## Phase 1: 数据库环境准备

- [ ] Docker Engine 运行正常，`docker info` 可执行
- [ ] PostgreSQL 容器成功创建并启动（`docker compose up -d postgres`）
- [ ] PostgreSQL 健康检查通过（healthy 状态）
- [ ] 端口 5432 可从宿主机访问
- [ ] init.sql 自动执行完成，orders 表已创建（30 字段）
- [ ] orders 表索引已创建（7 个索引）
- [ ] 可使用 benchmark/benchmark123 凭证连接数据库

## Phase 2: 数据生成验证

- [ ] data-generator 镜像构建成功（无报错）
- [ ] 数据生成脚本在容器内执行完成（exit code 0）
- [ ] 容器日志显示数据生成过程正常（无异常堆栈）
- [ ] 数据库 orders 表中有数据（SELECT COUNT(*) > 0）
- [ ] 生成的数据符合字段规则（抽样检查订单号格式、状态分布等）

## Phase 3: 后端服务验证

### Java 服务 (端口 8080)
- [ ] Java 服务 Docker 镜像构建成功（Gradle build + JAR 打包）
- [ ] Java 容器启动成功，无崩溃重启
- [ ] Java 健康检查通过（GET /actuator/health → UP）
- [ ] 端口 8080 从宿主机可访问
- [ ] API Key 认证生效（无 key 返回 401/403，有 key 正常响应）
- [ ] GET /api/v1/orders 接口返回订单数据（JSON 格式正确）
- [ ] 服务日志无严重错误

### Golang 服务 (端口 8081)
- [ ] Golang 服务 Docker 镜像构建成功（CGO交叉编译）
- [ ] Golang 容器启动成功，无崩溃重启
- [ ] Golang 健康检查通过（GET /health → 正常）
- [ ] 端口 8081 从宿主机可访问
- [ ] API Key 认证生效
- [ ] GET /api/v1/orders 接口返回订单数据
- [ ] 服务日志无严重错误

### Python 服务 (端口 8082)
- [ ] Python 服务 Docker 镜像构建成功（依赖安装 + 应用部署）
- [ ] Python 容器启动成功，无崩溃重启
- [ ] Python 健康检查通过（GET /health → 正常）
- [ ] 端口 8082 从宿主机可访问
- [ ] API Key 认证生效
- [ ] GET /api/v1/orders 接口返回订单数据
- [ ] 服务日志无严重错误

### Rust 服务 (端口 8083)
- [ ] Rust 服务 Docker 镜像构建成功（Cargo 编译）
- [ ] Rust 容器启动成功，无崩溃重启
- [ ] Rust 健康检查通过（GET /health → 正常）
- [ ] 端口 8083 从宿主机可访问
- [ ] API Key 认证生效
- [ ] GET /api/v1/orders 接口返回订单数据
- [ ] 服务日志无严重错误

## Phase 4: 前端服务验证

- [ ] 前端 Docker 镜像构建成功（npm build + Nginx 部署）
- [ ] 前端容器（Nginx）启动成功
- [ ] 端口 80 从宿主机可访问
- [ ] HTTP GET / 返回 HTML 页面（状态码 200）
- [ ] 静态资源（CSS/JS）可正常加载
- [ ] 前端页面可在浏览器中正常渲染
- [ ] 后端服务切换下拉框可见且可选
- [ ] 切换后端服务后，订单查询接口调用正确的后端地址
- [ ] 订单数据能在前端表格中正确展示

## Phase 5: 清理与环境状态

- [ ] 各服务验证结果已汇总记录
- [ ] 所有容器可正常关闭（`docker compose down`）
- [ ] 数据库数据持久化卷保留完好（下次启动数据仍在）
