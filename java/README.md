# Java 后端服务 (Spring Boot)

基于 Spring Boot 3.2 的订单查询与数据导出 API 服务。

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Java | 21 (JDK) | LTS 版本 |
| Spring Boot | 3.2.x | 应用框架 |
| Gradle | 8.12 | 构建工具 |
| JOOQ | 3.x | 类型安全 SQL 构建 |
| HikariCP | 内置 | 数据库连接池 |
| Apache POI | SXSSF | 流式 Excel 写入 |

## 项目结构

```
java/
├── src/main/java/com/benchmark/
│   ├── BenchmarkApplication.java   # 启动类
│   ├── config/
│   │   ├── DatabaseConfig.java     # JOOQ + DataSource 配置
│   │   ├── AsyncConfig.java        # 异步线程池
│   │   └── WebConfig.java          # CORS/WebMvc 配置
│   ├── controller/
│   │   ├── ExportController.java   # 导出接口（同步/异步/流式/SSE）
│   │   └── OrderController.java    # 订单查询接口
│   ├── middleware/
│   │   └── auth.java               # API Key 认证中间件
│   ├── model/
│   │   ├── Order.java              # 订单实体 (30 字段, Lombok Builder)
│   │   ├── Task.java               # 异步任务模型
│   │   ├── ExportRequest.java      # 导出请求 DTO
│   │   └── PageResponse.java       # 分页响应
│   ├── repository/
│   │   └── OrderRepository.java    # JOOQ 数据访问层
│   ├── service/
│   │   ├── OrderService.java       # 订单业务逻辑
│   │   ├── ExportService.java      # 导出逻辑（CSV/Excel）
│   │   └── AsyncTaskService.java   # 异步任务管理
│   └── util/
│       ├── CsvWriter.java          # CSV 文件写入
│       └── ExcelWriter.java         # SXSSF Excel 写入
├── build.gradle
├── settings.gradle
└── Dockerfile                      # 多阶段构建
```

## 本地开发

```bash
cd java

# 设置环境变量
export SPRING_PROFILES_ACTIVE=docker
export DATABASE_URL=jdbc:postgresql://localhost:5432/benchmark
export DATABASE_USERNAME=benchmark
export DATABASE_PASSWORD=benchmark123
export API_KEY=benchmark-api-key-2024

# 运行
./gradlew bootRun

# 或 IDEA 直接运行 BenchmarkApplication
```

## Docker 构建

```bash
docker compose build java-api
docker compose up -d java-api

# 验证
curl http://localhost:8080/actuator/health
```

## 关键接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/actuator/health` | 健康检查 → `{"status":"UP"}` |
| GET | `/api/v1/orders?page=1&size=20` | 分页查询订单 |
| POST | `/api/v1/exports/sync` | 同步导出 |
| POST | `/api/v1/exports/async` | 异步导出任务 |
| GET | `/api/v1/exports/tasks/{id}` | 任务状态 |
| GET | `/api/v1/exports/sse/{id}` | SSE 进度推送 |

## 已知修复记录

1. **JDK21 Record 冲突**: `java.lang.Record` 与 `org.jooq.Record` 歧义 → 显式导入 JOOQ 类
2. **时间类型转换**: JDBC `Timestamp` → `LocalDateTime` 添加 `toLocalDateTime()` 方法
3. **数值类型转换**: PostgreSQL `smallint`(Short) → Integer 添加 `toInt()` 方法
4. **ExcelWriter SXSSF**: `getSXSSFSheet()` API 变更 → 移除直接写入，改为调用方处理
5. **Cursor 泛型**: `Cursor<Record>` 类型不匹配 → 改为 `Cursor<?>`
6. **基础镜像**: `gradle:8.5-jdk21-alpine` arm64 不存在 → 改用 `gradle:8.12-jdk21`
7. **运行时镜像**: `eclipse-temurin:21-jre-alpine` 镜像源 403 → 改用完整版

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SPRING_PROFILES_ACTIVE` | docker | Spring Profile |
| `DATABASE_URL` | - | JDBC 连接串 |
| `DATABASE_USERNAME` | benchmark | DB 用户名 |
| `DATABASE_PASSWORD` | benchmark123 | DB 密码 |
| `API_KEY` | benchmark-api-key-2024 | API 认证密钥 |
| `JAVA_OPTS` | -Xms512m -Xmx1024m | JVM 参数 |
