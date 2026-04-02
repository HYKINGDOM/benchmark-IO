# 数据生成工具 (Python)

用于生成大规模测试订单数据的命令行工具，支持批量并发写入 PostgreSQL。

## 用途

为基准测试系统生成指定数量的模拟订单数据，支持从几千到两千万级别的数据量。

## 技术栈

| 组件 | 说明 |
|------|------|
| Python | 3.11 运行时 |
| psycopg2 | PostgreSQL 同步驱动 |
| concurrent.futures | 并发写入 |

## 使用方式

### Docker 内执行（推荐）

```bash
# 构建镜像
docker compose build data-generator

# 生成 1 万条数据（验证用）
docker compose run --rm data-generator python main.py generate --total 10000 --workers 2

# 生成 200 万条数据（性能测试）
docker compose run --rm data-generator python main.py generate --total 2000000 --workers 4

# 生成 2000 万条数据（完整测试）
docker compose run --rm data-generator python main.py generate --total 20000000 --workers 4
```

### 本地执行

```bash
cd init/generate_data

pip install -r requirements.txt

DB_HOST=localhost DB_PORT=5432 \
POSTGRES_DB=benchmark POSTGRES_USER=benchmark POSTGRES_PASSWORD=benchmark123 \
python main.py generate --total 10000 --workers 2
```

## 命令参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--total` | 20000000 | 总记录数 |
| `--workers` | 4 | 并发进程数 |
| `--batch-size` | 50000 | 每批插入数量 |

## 生成的数据特征

- **订单号**: ORD + 时间戳 + 6 位随机数
- **用户信息**: 随机生成的姓名、手机号、身份证号、邮箱、地址
- **商品信息**: 10 种分类下的随机商品
- **金额范围**: 单价 10-50000，数量 1-10
- **订单状态分布**:
  - 已支付 ~50%
  - 已完成 ~15%
  - 待支付 ~15%
  - 已取消 ~15%
  - 已退款 ~5%
- **时间范围**: 最近 365 天内随机

## 项目结构

```
init/generate_data/
├── main.py                   # CLI 入口（argparse）
├── generator.py              # 数据生成逻辑（工厂模式）
├── config.py                 # 配置常量
├── db.py                     # 数据库连接管理
├── requirements.txt          # Python 依赖
└── Dockerfile                # Python slim + 网络重试
```

## 注意事项

- 执行前确保 PostgreSQL 已启动且 init.sql 已执行（表结构已创建）
- 大数据量生成时建议增加 `--workers` 但注意数据库连接数限制
- 生成 2000 万条数据预计需要数分钟至十几分钟（取决于硬件）
- 数据生成容器使用 `--rm` 参数，执行完自动清理
