# Python 后端服务 (FastAPI)

基于 FastAPI + Gunicorn 的订单查询与数据导出 API 服务。

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11 | 运行时 |
| FastAPI | 0.100+ | 异步 Web 框架 |
| Tortoise ORM | - | 异步 ORM |
| asyncpg | - | 异步 PostgreSQL 驱动 |
| openpyxl | - | Excel 处理 |
| uvicorn | - | ASGI 服务器 |
| Gunicorn | - | WSGI 进程管理 |

## 项目结构

```
python/
├── app/
│   ├── main.py                # FastAPI 应用入口、生命周期
│   ├── config.py              # Pydantic Settings 配置
│   ├── models/
│   │   └── order.py           # Tortoise Model 定义
│   ├── api/
│   │   ├── __init__.py
│   │   ├── orders.py          # 订单路由
│   │   └── exports.py         # 导出路由
│   ├── middleware/
│   │   └── auth.py            # API Key 中间件
│   ├── services/
│   │   ├── order_service.py   # 订单服务
│   │   └── export_service.py  # 导出服务
│   └── utils/
│       ├── csv_writer.py      # CSV 写入
│       └── excel_writer.py    # Excel 写入
├── requirements.txt
├── gunicorn.conf.py            # Gunicorn 配置
└── Dockerfile                  # Python slim + pip 国内源
```

## 本地开发

```bash
cd python

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行
DATABASE_URL="postgres://benchmark:benchmark123@localhost:5432/benchmark" \
API_KEYS="benchmark-api-key-2024" \
PORT=8082 \
uvicorn app.main:app --host 0.0.0.0 --port 8082 --reload
```

## Docker 构建

```bash
docker compose build python-api
docker compose up -d python-api

# 验证
curl http://localhost:8082/health
```

## 关键接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/docs` | Swagger UI (FastAPI 自动生成) |
| GET | `/api/v1/orders?page=1&size=20` | 分页查询 |
| POST | `/api/v1/exports/sync` | 同步导出 |
| POST | `/api/v1/exports/async` | 异步导出 |
| GET | `/api/v1/exports/tasks/{id}` | 任务状态 |
| GET | `/api/v1/exports/sse/{id}` | SSE 推送 |

## 已知修复记录

1. **Tortoise minsize/maxsize 不支持**: 参数在当前版本无效 → 移除该参数
2. **generate_schemas 冲突**: 与 init.sql 已有表冲突 → 注释掉自动建表
3. **端口映射错误**: gunicorn 默认监听 8000，docker-compose 映射 8082 → 设置 `PORT=8082`
4. **API Key 不匹配**: 配置默认值为 `test-api-key-1` → 设置 `API_KEYS=${API_KEY}`
5. **pip 安装慢**: 默认源速度慢 → 使用清华镜像 `pypi.tuna.tsinghua.edu.cn`
6. **apt-get 网络不稳定** → 添加 3 次重试机制

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | - | PostgreSQL 连接串 |
| `API_KEY` | test-api-key-1 | 单个 API Key |
| `API_KEYS` | test-api-key-1 | API Keys（逗号分隔） |
| `PORT` | 8000 | Gunicorn 监听端口 |
| `WORKERS` | 4 | Gunicorn Worker 数量 |
