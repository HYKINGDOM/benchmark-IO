# Vue.js 前端

基于 Vue 3 + Vite 的基准测试前端界面，支持多后端切换和数据导出操作。

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Vue | 3.x | 渐进式框架 |
| Vite | 5.x | 构建工具 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由 |
| Axios | - | HTTP 客户端 |
| Nginx | - | 生产环境服务器 |

## 项目结构

```
frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── main.js                # 应用入口
│   ├── App.vue                # 根组件
│   ├── router/index.js        # 路由配置
│   ├── views/
│   │   ├── Orders.vue         # 订单列表页
│   │   └── Tasks.vue          # 导出任务页
│   ├── components/
│   │   ├── ServiceSelector.vue # 后端服务切换下拉框
│   │   ├── OrderTable.vue     # 订单表格
│   │   ├── ExportPanel.vue    # 导出面板
│   │   └── TaskProgress.vue   # 任务进度条
│   ├── api/
│   │   ├── index.js           # Axios 实例（baseURL 动态切换）
│   │   ├── order.js           # 订单 API
│   │   └── export.js          # 导出 API
│   ├── stores/
│   │   ├── service.js         # 当前选中后端状态
│   │   ├── order.js           # 订单数据状态
│   │   └── export.js          # 导出任务状态
│   └── utils/
│       ├── request.js         # 请求拦截器（注入 API Key）
│       └── sse.js             # SSE 工具函数
├── index.html
├── vite.config.js             # Vite 配置（代理/API Key 注入）
├── nginx.conf                 # Nginx 反向代理配置
├── package.json
└── Dockerfile                 # Node build → Nginx serve
```

## 功能特性

- **多后端切换**: 下拉框动态切换 Java/Golang/Python/Rust 后端
- **订单分页查询**: 支持条件筛选的分页表格
- **数据导出**: 支持 CSV/Excel 格式，同步/异步/流式三种模式
- **实时进度**: SSE 推送显示异步导出进度
- **文件下载**: 导出完成后自动下载

## 本地开发

```bash
cd frontend

# 安装依赖
npm install

# 开发模式（热更新）
VITE_API_KEY=benchmark-api-key-2024 \
VITE_JAVA_API_URL=http://localhost:8080 \
VITE_GOLANG_API_URL=http://localhost:8081 \
VITE_PYTHON_API_URL=http://localhost:8082 \
VITE_RUST_API_URL=http://localhost:8083 \
npm run dev

# 访问 http://localhost:5173
```

## Docker 构建

```bash
docker compose build frontend
docker compose up -d frontend

# 访问 http://localhost
```

## Nginx 配置说明

生产环境使用 Nginx 作为静态文件服务器，配置了：
- SPA 路由 fallback（`try_files $uri $uri/ /index.html`）
- API 反向代理到各后端服务
- Gzip 压缩
- 静态资源缓存策略

## 环境变量（构建时注入）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VITE_API_KEY` | benchmark-api-key-2024 | API 认证密钥 |
| `VITE_JAVA_API_URL` | http://localhost:8080 | Java 后端地址 |
| `VITE_GOLANG_API_URL` | http://localhost:8081 | Golang 后端地址 |
| `VITE_PYTHON_API_URL` | http://localhost:8082 | Python 后端地址 |
| `VITE_RUST_API_URL` | http://localhost:8083 | Rust 后端地址 |
