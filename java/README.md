# Benchmark Java API

Java 后端服务，使用 Spring Boot 3.2 + JOOQ + HikariCP 实现。

## 技术栈

- JDK 21
- Spring Boot 3.2.5
- JOOQ 3.19.7
- HikariCP 5.1.0
- Apache POI 5.2.5
- PostgreSQL 17

## 项目结构

```
java/
├── src/main/java/com/benchmark/
│   ├── BenchmarkApplication.java      # 主应用
│   ├── config/                        # 配置类
│   │   ├── DatabaseConfig.java       # 数据库配置
│   │   ├── AsyncConfig.java          # 异步配置
│   │   └── WebConfig.java            # Web配置
│   ├── controller/                    # 控制器
│   │   ├── OrderController.java      # 订单查询
│   │   └── ExportController.java     # 数据导出
│   ├── service/                       # 服务层
│   │   ├── OrderService.java         # 订单服务
│   │   ├── ExportService.java        # 导出服务
│   │   └── AsyncTaskService.java     # 异步任务服务
│   ├── repository/                    # 数据访问层
│   │   └── OrderRepository.java      # 订单仓库
│   ├── model/                         # 模型类
│   │   ├── Order.java                # 订单实体
│   │   ├── ExportTask.java           # 导出任务
│   │   ├── ApiResponse.java          # API响应
│   │   ├── PageResponse.java         # 分页响应
│   │   ├── OrderQueryRequest.java    # 查询请求
│   │   └── ExportRequest.java        # 导出请求
│   ├── middleware/                    # 中间件
│   │   └── ApiKeyAuthFilter.java     # API Key认证
│   └── util/                          # 工具类
│       ├── CsvWriter.java            # CSV写入器
│       └── ExcelWriter.java          # Excel写入器
├── src/main/resources/
│   └── application.yml               # 应用配置
├── build.gradle                      # Gradle构建文件
├── settings.gradle                   # Gradle设置
└── Dockerfile                        # Docker构建文件
```

## API 接口

### 1. 订单查询

```http
GET /api/v1/orders
Header: X-API-Key: benchmark-api-key-2024
```

**查询参数：**
- page: 页码（默认 1）
- pageSize: 每页条数（默认 20）
- startTime: 开始时间
- endTime: 结束时间
- status: 订单状态
- minAmount: 最小金额
- maxAmount: 最大金额
- userId: 用户ID
- orderNo: 订单编号

### 2. 同步导出

```http
POST /api/v1/exports/sync
Header: X-API-Key: benchmark-api-key-2024
Content-Type: application/json

{
  "format": "csv",
  "limit": 100000,
  "conditions": {
    "startTime": "2024-01-01",
    "endTime": "2024-12-31",
    "status": "已支付"
  }
}
```

### 3. 异步导出

```http
POST /api/v1/exports/async
Header: X-API-Key: benchmark-api-key-2024
Content-Type: application/json

{
  "format": "xlsx",
  "limit": 1000000
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "uuid-xxx-xxx",
    "status": "pending"
  }
}
```

### 4. 任务状态查询

```http
GET /api/v1/exports/tasks/{task_id}
Header: X-API-Key: benchmark-api-key-2024
```

### 5. SSE 进度推送

```http
GET /api/v1/exports/sse/{task_id}
Header: X-API-Key: benchmark-api-key-2024
```

### 6. 文件下载

```http
GET /api/v1/exports/download/{token}
Header: X-API-Key: benchmark-api-key-2024
```

### 7. 流式导出

```http
POST /api/v1/exports/stream
Header: X-API-Key: benchmark-api-key-2024
Content-Type: application/json

{
  "format": "csv",
  "limit": 1000000
}
```

## 本地开发

### 前置要求

- JDK 21+
- Gradle 8.5+
- PostgreSQL 17+

### 运行步骤

1. 设置环境变量：
```bash
export DATABASE_URL=jdbc:postgresql://localhost:5432/benchmark
export DATABASE_USERNAME=benchmark
export DATABASE_PASSWORD=benchmark123
export API_KEY=benchmark-api-key-2024
```

2. 构建项目：
```bash
cd java
gradle clean build
```

3. 运行应用：
```bash
gradle bootRun
```

应用将在 http://localhost:8080 启动。

## Docker 构建

```bash
cd java
docker build -t benchmark-java .
```

## 性能优化

### 数据库连接池

- HikariCP 最大连接数：50
- 最小空闲连接数：10
- 连接超时：30秒
- 空闲超时：5分钟
- 最大生命周期：30分钟

### 异步处理

- 核心线程数：10
- 最大线程数：50
- 队列容量：1000

### 导出优化

- 使用 JOOQ Cursor 流式读取数据
- CSV 使用 Apache Commons CSV
- Excel 使用 Apache POI SXSSF（流式写入）
- 每 1000 条记录更新进度
- 内存中只保留 100 行 Excel 数据

## 监控

- Spring Boot Actuator 健康检查：`/actuator/health`
- Prometheus 指标：`/actuator/prometheus`

## 注意事项

1. 所有 API 请求需要在 Header 中传递 `X-API-Key`
2. 导出文件默认保存在系统临时目录
3. 异步任务状态存储在内存中（生产环境建议使用 Redis）
4. Excel 导出使用流式写入，避免内存溢出
5. 最大导出行数限制为 2000 万行
