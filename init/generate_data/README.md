# 订单数据生成工具

用于生成大规模订单测试数据的 Python 工具，支持 2000 万条记录的高效生成。

## 功能特性

- 支持全量数据生成（2000 万条）
- 支持增量数据生成（指定时间范围）
- 符合业务字段规则的随机数据
- 时间分布符合预设比例（2020-2024年）
- 订单状态分布符合预设比例
- 多进程并行生成，高效批量插入
- 数据统计和清理功能

## 数据规则

### 字段规则

| 字段 | 规则 |
|------|------|
| order_id | 自增序列，从 1 开始 |
| order_no | 格式 ORD + 时间戳 + 6位随机数，唯一 |
| user_id | 范围 1 ~ 20,000,000 |
| user_name | 随机中文姓名，2-4 个汉字 |
| user_phone | 符合手机号规范 13/14/15/16/17/18/19 开头 |
| user_id_card | 符合身份证格式，含生日和校验位 |
| user_email | user_{user_id}@example.com |
| user_address | 随机省市区地址 |
| product_id | 范围 1 ~ 100,000 |
| product_name | 随机商品名前缀 + 规格 |
| product_category | 预定义分类池 |
| product_price | 范围 0.01 ~ 9999.99 |
| quantity | 范围 1 ~ 99 |
| total_amount | = product_price * quantity |
| discount_amount | 范围 0 ~ total_amount * 0.3 |
| pay_amount | = total_amount - discount_amount |
| order_status | 待支付/已支付/已取消/已退款/已完成 |
| payment_method | 支付宝/微信/银行卡/其他 |
| payment_time | 在下单时间之后，允许为空 |
| order_source | APP/小程序/Web/H5/线下 |
| shipping_address | 随机省市区详细地址 |
| receiver_name | 随机中文姓名 |
| receiver_phone | 符合手机号规范 |
| logistics_no | 格式 SF/YT/YD + 12位数字，允许为空 |
| delivery_time | 在支付时间之后，允许为空 |
| complete_time | 在发货时间之后，允许为空 |
| remark | 随机生成，可为空 |
| created_at | 范围 2020-01-01 ~ 2024-12-31 |
| updated_at | >= created_at |
| is_deleted | 0-未删除，1-已删除，默认 0 |

### 时间分布

| 年份 | 占比 |
|------|------|
| 2020 | 10% |
| 2021 | 15% |
| 2022 | 20% |
| 2023 | 25% |
| 2024 | 30% |

### 状态分布

| 状态 | 占比 |
|------|------|
| 待支付 | 15% |
| 已支付 | 50% |
| 已取消 | 15% |
| 已退款 | 5% |
| 已完成 | 15% |

## 使用方法

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DB_HOST=localhost
export DB_PORT=5432
export POSTGRES_DB=benchmark
export POSTGRES_USER=benchmark
export POSTGRES_PASSWORD=benchmark123

# 生成 2000 万条数据
python main.py generate --total 20000000

# 生成 100 万条数据，使用 8 个进程
python main.py generate --total 1000000 --workers 8

# 增量生成 2024 年 1 月的数据
python main.py incremental --start 2024-01-01 --end 2024-01-31 --count 100000

# 显示数据统计
python main.py stats

# 清空数据
python main.py clear
```

### Docker 运行

```bash
# 构建镜像
docker build -t benchmark-data-generator .

# 运行容器（连接到 docker 网络）
docker run --rm \
  --network benchmark-network \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e POSTGRES_DB=benchmark \
  -e POSTGRES_USER=benchmark \
  -e POSTGRES_PASSWORD=benchmark123 \
  benchmark-data-generator \
  python main.py generate --total 20000000
```

### Docker Compose 运行

在项目根目录的 `docker-compose.yml` 中添加数据生成服务：

```yaml
  data-generator:
    build:
      context: ./init/generate_data
      dockerfile: Dockerfile
    container_name: benchmark-data-generator
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      POSTGRES_DB: ${POSTGRES_DB:-benchmark}
      POSTGRES_USER: ${POSTGRES_USER:-benchmark}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-benchmark123}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - benchmark-network
    profiles:
      - tools
```

运行命令：

```bash
# 生成数据
docker-compose run --rm data-generator python main.py generate --total 20000000

# 显示统计
docker-compose run --rm data-generator python main.py stats

# 清空数据
docker-compose run --rm data-generator python main.py clear -y
```

## 命令参数

### generate 命令

| 参数 | 短参数 | 默认值 | 说明 |
|------|--------|--------|------|
| --total | -t | 20,000,000 | 总记录数 |
| --batch | -b | 50,000 | 批次大小 |
| --workers | -w | 4 | 并发进程数 |

### incremental 命令

| 参数 | 短参数 | 必填 | 说明 |
|------|--------|------|------|
| --start | -s | 是 | 开始日期 (YYYY-MM-DD) |
| --end | -e | 是 | 结束日期 (YYYY-MM-DD) |
| --count | -c | 是 | 生成数量 |
| --batch | -b | 否 | 批次大小 (默认: 50,000) |
| --workers | -w | 否 | 并发进程数 (默认: 4) |

### clear 命令

| 参数 | 短参数 | 说明 |
|------|--------|------|
| --yes | -y | 跳过确认直接清空 |

## 性能参考

在以下配置下的典型性能：

- CPU: 8 核
- 内存: 16GB
- 数据库: PostgreSQL 17 (本地)
- 批次大小: 50,000
- 并发进程: 4

| 数据量 | 耗时 | 速度 |
|--------|------|------|
| 100 万 | ~30 秒 | ~33,000 条/秒 |
| 500 万 | ~2.5 分钟 | ~33,000 条/秒 |
| 1000 万 | ~5 分钟 | ~33,000 条/秒 |
| 2000 万 | ~10 分钟 | ~33,000 条/秒 |

## 文件结构

```
init/generate_data/
├── config.py       # 配置文件
├── db.py           # 数据库操作
├── generator.py    # 数据生成器
├── main.py         # 主程序
├── requirements.txt # 依赖列表
├── Dockerfile      # Docker 配置
└── README.md       # 使用说明
```

## 注意事项

1. 首次运行会自动创建 `orders` 表
2. 生成过程中支持断点续传（从最大 ID 继续）
3. 建议在数据库负载较低时执行大批量数据生成
4. 清空数据操作不可逆，请谨慎操作
