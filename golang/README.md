# Golang 后端服务 (Gin)

基于 Gin Web Framework 的订单查询与数据导出 API 服务。

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Go | latest (1.22+) | 编程语言 |
| Gin | v1.x | Web 框架 |
| GORM | v0.20+ | ORM |
| pgx/pgxpool | v5.x | PostgreSQL 驱动和连接池 |
| excelize | v2.x | Excel 处理 |

## 项目结构

```
golang/
├── cmd/main.go                 # 入口：初始化 DB/GIN/路由
├── internal/
│   ├── config/config.go        # 环境变量配置加载
│   ├── controller/
│   │   ├── export.go           # 导出控制器
│   │   └── order.go            # 订单控制器
│   ├── middleware/auth.go       # API Key 中间件
│   ├── model/
│   │   ├── order.go            # 订单模型 (30 字段)
│   │   └── task.go             # 任务模型
│   ├── repository/order.go     # GORM 数据访问
│   ├── service/
│   │   ├── export.go           # 导出服务 (CSV/Excel)
│   │   ├── order.go            # 订单服务
│   │   └── task.go             # 异步任务服务
│   └── util/
│       ├── csv.go              # CSV 写入
│       └── excel.go            # Excel 写入
├── pkg/response/response.go   # 统一响应格式
├── go.mod
├── go.sum
└── Dockerfile                   # CGO 交叉编译 + multi-stage
```

## 本地开发

```bash
cd golang

# 安装依赖
go mod download

# 运行
DB_HOST=localhost DB_PORT=5432 \
DB_USER=benchmark DB_PASSWORD=benchmark123 \
DB_NAME=benchmark API_KEY=benchmark-api-key-2024 \
go run cmd/main.go

# 或使用 air 热重载
air
```

## Docker 构建

```bash
docker compose build golang-api
docker compose up -d golang-api

# 验证
curl http://localhost:8081/health
```

## 关键接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/v1/orders?page=1&size=20` | 分页查询 |
| POST | `/api/v1/exports/sync` | 同步导出 |
| POST | `/api/v1/exports/async` | 异步导出 |
| GET | `/api/v1/exports/tasks/{id}` | 任务状态 |
| GET | `/api/v1/exports/sse/{id}` | SSE 推送 |

## 已知修复记录

1. **Go 代理超时**: `proxy.golang.org` 不可达 → 设置 `GOPROXY=https://goproxy.io,direct`
2. **Go module 校验失败**: goproxy.cn 缓存损坏 → 使用 goproxy.io 并设置 `GONOSUMCHECK=*`
3. **gin.FormatLog 移除**: 新版 gin 删除此方法 → 使用 `fmt.Sprintf` 手动格式化
4. **未使用导入/变量**: excel.go (`fmt`)、main.go (`os`)、export.go (`data`, `fileName`) → 清理
5. **数据库连接失败**: 使用 `localhost` 而非 Docker 服务名 → docker-compose.yml 补充 `DB_HOST: postgres` 等环境变量

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | - | 完整数据库 URL（含凭据） |
| `DB_HOST` | localhost | 数据库主机 |
| `DB_PORT` | 5432 | 数据库端口 |
| `DB_USER` | benchmark | 用户名 |
| `DB_PASSWORD` | benchmark123 | 密码 |
| `DB_NAME` | benchmark | 数据库名 |
| `API_KEY` | benchmark-api-key-2024 | API 密钥 |
| `GIN_MODE` | release | Gin 运行模式 |
