# Rust 后端服务 (Actix-web)

基于 Actix-web 的订单查询与数据导出 API 服务。

> ⚠️ **当前状态**: 编译阻塞 — xlsxwriter crate API 重大变更导致 19 个编译错误待修复

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Rust | latest (1.88+) | 需要 edition2024 支持 |
| Actix-web | v4.x | 异步 Web 框架 |
| Diesel | v2.x | ORM / Query Builder |
| r2d2 | v0.8 | 连接池 |
| xlsxwriter | v0.6+ | Excel 处理 (**API 变更中**) |
| serde/serde_json | - | 序列化 |
| chrono | - | 时间处理 |

## 项目结构

```
rust/
├── src/
│   ├── main.rs                # 入口：服务器启动、路由注册
│   ├── models/
│   │   └── mod.rs             # Diesel Schema/Model 定义
│   ├── handlers/
│   │   ├── mod.rs             # 请求处理器
│   │   ├── health.rs          # 健康检查
│   │   ├── order.rs           # 订单查询
│   │   └── export.rs          # 导出功能
│   ├── utils/
│   │   ├── mod.rs
│   │   └── excel.rs           # Excel 写入 (**需适配新 API**)
│   └── db.rs                  # Diesel 连接池初始化
├── migrations/                # Diesel 数据库迁移
├── Cargo.toml
├── .cargo/config.toml         # Cargo 国内镜像 (rsproxy sparse)
└── Dockerfile                  # multi-stage: build + runtime
```

## 当前阻塞问题

### xlsxwriter 0.6.x API 变更详情

xlsxwriter 从 0.5.x 升级到 0.6.x 后，Format 和 Worksheet API 发生了重大变更：

| 旧 API (0.5.x) | 新 API (0.6.x) | 问题类型 |
|------------------|-----------------|---------|
| `workbook.add_format()` | `Format::new()` | E0277 构造函数变更 |
| `.set_font_name().set_bold().chain()` | builder pattern 返回新 Format | E0583 赋值表达式 |
| `.set_font_size(10)` (int) | `.set_font_size(10.0)` (f64) | E0308 类型不匹配 |
| `worksheet.freeze_panes().map_err()` | `freeze_panes()` 返回 `()` | E0599 无 map_err |
| `worksheet.write_string()` 参数签名变化 | - | E0308 参数不匹配 |
| `FormatColor::LightBlue` 等 enum 值 | 可能已重命名 | E0433 未解析导入 |

共 **19 个编译错误**，主要集中在 [src/utils/excel.rs](src/utils/excel.rs)。

## 已完成的修复

1. **Rust 版本升级**: `rust:1.75` → `rust:latest` (支持 edition2024)
2. **Cargo 镜像配置**: 创建 [.cargo/config.toml](.cargo/config.toml) 使用 rsproxy sparse 协议
3. **Cargo.lock 缺失**: Dockerfile 改为只复制 Cargo.toml（自动生成 lock）
4. **libclang 缺失**: apt-get 安装 `libclang-dev`（bindgen 依赖）
5. **SERVER_PORT 配置**: docker-compose.yml 添加 `SERVER_PORT: "8083"`

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | - | PostgreSQL 连接串 |
| `API_KEY` | benchmark-api-key-2024 | API 密钥 |
| `RUST_LOG` | info | 日志级别 |
| `SERVER_PORT` | 8080 | 服务监听端口 |

## 修复建议

要解决编译问题，需要重写 `src/utils/excel.rs` 以适配 xlsxwriter 0.6.x 的新 API。主要改动方向：
- 使用 `Format::new()` 替代 `workbook.add_format()`
- 采用 builder pattern 链式调用构建 Format
- 整数值参数改为浮点数
- `freeze_panes()` 等返回 `()` 的方法不再链式调用 `.map_err()`
