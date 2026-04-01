# API 接口文档

本文档详细说明百万级数据导出跨语言性能基准测试系统的所有 API 接口。

## 目录

- [概述](#概述)
- [认证](#认证)
- [通用说明](#通用说明)
- [订单查询接口](#订单查询接口)
- [数据导出接口](#数据导出接口)
- [任务管理接口](#任务管理接口)
- [错误码说明](#错误码说明)
- [示例代码](#示例代码)

## 概述

### 基础信息

| 项目 | 说明 |
|------|------|
| 协议 | HTTP/1.1 |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 时间格式 | ISO 8601 (YYYY-MM-DDTHH:mm:ssZ) |

### 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Java API | http://localhost:8080 | Spring Boot 服务 |
| Golang API | http://localhost:8081 | Gin 服务 |
| Python API | http://localhost:8082 | FastAPI 服务 |
| Rust API | http://localhost:8083 | Actix-web 服务 |

### API 基础路径

所有 API 的基础路径为：`/api/v1`

## 认证

### API Key 认证

所有 API 请求需要在 HTTP Header 中携带 API Key：

```http
X-API-Key: benchmark-api-key-2024
```

### 示例

```bash
curl -H "X-API-Key: benchmark-api-key-2024" http://localhost:8080/api/v1/orders
```

### 认证失败响应

```json
{
  "code": 401,
  "message": "Unauthorized: Invalid or missing API key",
  "data": null
}
```

## 通用说明

### 响应格式

所有接口统一返回以下格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 响应数据
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 状态码，0 表示成功，非 0 表示失败 |
| message | string | 响应消息 |
| data | object | 响应数据，失败时可能为 null |

### 分页参数

支持分页的接口使用以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码，从 1 开始 |
| pageSize | integer | 20 | 每页条数，最大 100 |

### 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 1000,
    "page": 1,
    "pageSize": 20,
    "totalPages": 50
  }
}
```

## 订单查询接口

### 1. 查询订单列表

查询订单数据，支持多条件筛选和分页。

#### 请求

```http
GET /api/v1/orders
```

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| pageSize | integer | 否 | 每页条数，默认 20，最大 100 |
| startTime | string | 否 | 开始时间 (YYYY-MM-DD) |
| endTime | string | 否 | 结束时间 (YYYY-MM-DD) |
| status | string | 否 | 订单状态 |
| minAmount | number | 否 | 最小金额 |
| maxAmount | number | 否 | 最大金额 |
| userId | string | 否 | 用户 ID |
| orderNo | string | 否 | 订单编号 |
| region | string | 否 | 地区 |

#### 订单状态枚举

| 值 | 说明 |
|------|------|
| pending | 待支付 |
| paid | 已支付 |
| cancelled | 已取消 |
| refunded | 已退款 |
| completed | 已完成 |

#### 请求示例

```bash
# 基础查询
curl -H "X-API-Key: benchmark-api-key-2024" \
  "http://localhost:8080/api/v1/orders?page=1&pageSize=20"

# 带筛选条件
curl -H "X-API-Key: benchmark-api-key-2024" \
  "http://localhost:8080/api/v1/orders?startTime=2024-01-01&endTime=2024-12-31&status=paid&minAmount=100&maxAmount=1000"
```

#### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "orderId": 1,
        "orderNo": "ORD20240101123456789012",
        "userId": "user_12345",
        "userName": "张三",
        "userPhone": "13800138000",
        "productId": 1001,
        "productName": "iPhone 15 Pro",
        "productCategory": "手机数码",
        "productPrice": 8999.00,
        "quantity": 1,
        "totalAmount": 8999.00,
        "discountAmount": 0.00,
        "payAmount": 8999.00,
        "orderStatus": "paid",
        "paymentMethod": "支付宝",
        "paymentTime": "2024-01-01T10:30:00Z",
        "orderSource": "APP",
        "shippingAddress": "北京市朝阳区xxx",
        "receiverName": "张三",
        "receiverPhone": "13800138000",
        "createdAt": "2024-01-01T10:00:00Z",
        "updatedAt": "2024-01-01T10:30:00Z"
      }
    ],
    "total": 1000000,
    "page": 1,
    "pageSize": 20,
    "totalPages": 50000
  }
}
```

## 数据导出接口

### 2. 同步导出

同步方式导出数据，适用于小数据量场景（建议 < 10 万条）。请求会阻塞直到导出完成。

#### 请求

```http
POST /api/v1/exports/sync
Content-Type: application/json
```

#### 请求体

```json
{
  "format": "csv",
  "limit": 100000,
  "conditions": {
    "startTime": "2024-01-01",
    "endTime": "2024-12-31",
    "status": "paid",
    "minAmount": 100,
    "maxAmount": 10000,
    "userId": "user_123",
    "region": "北京"
  }
}
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 是 | 导出格式：csv 或 xlsx |
| limit | integer | 是 | 导出数据条数，最大 20000000 |
| conditions | object | 否 | 筛选条件 |

#### conditions 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| startTime | string | 开始时间 |
| endTime | string | 结束时间 |
| status | string | 订单状态 |
| minAmount | number | 最小金额 |
| maxAmount | number | 最大金额 |
| userId | string | 用户 ID |
| region | string | 地区 |

#### 请求示例

```bash
curl -X POST \
  -H "X-API-Key: benchmark-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "csv",
    "limit": 100000,
    "conditions": {
      "startTime": "2024-01-01",
      "endTime": "2024-12-31",
      "status": "paid"
    }
  }' \
  http://localhost:8080/api/v1/exports/sync
```

#### 响应示例

成功时直接返回文件流：

```http
HTTP/1.1 200 OK
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="orders_20240101_123456.csv"

order_id,order_no,user_id,user_name,...
1,ORD20240101123456789012,user_12345,张三,...
2,ORD20240101123456789013,user_12346,李四,...
```

### 3. 异步导出

异步方式导出数据，适用于大数据量场景。立即返回任务 ID，后台处理导出任务。

#### 请求

```http
POST /api/v1/exports/async
Content-Type: application/json
```

#### 请求体

```json
{
  "format": "xlsx",
  "limit": 1000000,
  "conditions": {
    "startTime": "2024-01-01",
    "endTime": "2024-12-31"
  }
}
```

#### 参数说明

与同步导出相同。

#### 请求示例

```bash
curl -X POST \
  -H "X-API-Key: benchmark-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "xlsx",
    "limit": 1000000
  }' \
  http://localhost:8080/api/v1/exports/async
```

#### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending"
  }
}
```

### 4. 流式导出

流式方式导出数据，边查询边传输，适用于大数据量场景，内存占用低。

#### 请求

```http
POST /api/v1/exports/stream
Content-Type: application/json
```

#### 请求体

与同步导出相同。

#### 请求示例

```bash
curl -X POST \
  -H "X-API-Key: benchmark-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "csv",
    "limit": 1000000
  }' \
  http://localhost:8080/api/v1/exports/stream \
  --output orders.csv
```

#### 响应

流式返回文件内容，HTTP 状态码 200，Content-Type 为对应的文件类型。

## 任务管理接口

### 5. 查询任务状态

查询异步导出任务的状态和进度。

#### 请求

```http
GET /api/v1/exports/tasks/{task_id}
```

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务 ID |

#### 请求示例

```bash
curl -H "X-API-Key: benchmark-api-key-2024" \
  http://localhost:8080/api/v1/exports/tasks/550e8400-e29b-41d4-a716-446655440000
```

#### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "progress": 45,
    "total": 1000000,
    "processed": 450000,
    "createdAt": "2024-01-01T10:00:00Z",
    "updatedAt": "2024-01-01T10:05:00Z",
    "downloadToken": null,
    "errorMessage": null
  }
}
```

#### 任务状态枚举

| 状态 | 说明 |
|------|------|
| pending | 待处理 |
| processing | 处理中 |
| completed | 已完成 |
| failed | 失败 |

### 6. SSE 进度推送

通过 Server-Sent Events 实时推送任务进度。

#### 请求

```http
GET /api/v1/exports/sse/{task_id}
Accept: text/event-stream
```

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务 ID |

#### 请求示例

```javascript
const eventSource = new EventSource(
  'http://localhost:8080/api/v1/exports/sse/550e8400-e29b-41d4-a716-446655440000',
  {
    headers: {
      'X-API-Key': 'benchmark-api-key-2024'
    }
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
};
```

#### 响应格式

```
event: progress
data: {"taskId":"550e8400-e29b-41d4-a716-446655440000","status":"processing","progress":45,"processed":450000,"total":1000000}

event: progress
data: {"taskId":"550e8400-e29b-41d4-a716-446655440000","status":"processing","progress":90,"processed":900000,"total":1000000}

event: completed
data: {"taskId":"550e8400-e29b-41d4-a716-446655440000","status":"completed","progress":100,"processed":1000000,"total":1000000,"downloadToken":"abc123"}
```

### 7. 文件下载

下载已完成的导出文件。

#### 请求

```http
GET /api/v1/exports/download/{token}
```

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| token | string | 下载令牌（从任务状态或 SSE 获取） |

#### 请求示例

```bash
curl -H "X-API-Key: benchmark-api-key-2024" \
  http://localhost:8080/api/v1/exports/download/abc123 \
  --output orders.xlsx
```

#### 响应

成功时返回文件流，HTTP 状态码 200。

#### 注意事项

- 下载令牌有效期为 1 小时
- 每个令牌只能使用一次
- 文件下载完成后会自动删除

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 数据格式错误 |
| 2001 | 认证失败 |
| 2002 | API Key 无效 |
| 3001 | 任务不存在 |
| 3002 | 任务已过期 |
| 3003 | 下载令牌无效 |
| 4001 | 数据库错误 |
| 4002 | 导出失败 |
| 5001 | 服务不可用 |

### 错误响应示例

```json
{
  "code": 1001,
  "message": "Invalid parameter: limit must be between 1 and 20000000",
  "data": null
}
```

## 示例代码

### JavaScript (Axios)

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8080/api/v1';
const API_KEY = 'benchmark-api-key-2024';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

// 查询订单
async function getOrders(page = 1, pageSize = 20) {
  const response = await client.get('/orders', {
    params: { page, pageSize }
  });
  return response.data;
}

// 同步导出
async function syncExport(format, limit, conditions = {}) {
  const response = await client.post('/exports/sync', {
    format,
    limit,
    conditions
  }, {
    responseType: 'blob'
  });
  return response.data;
}

// 异步导出
async function asyncExport(format, limit, conditions = {}) {
  const response = await client.post('/exports/async', {
    format,
    limit,
    conditions
  });
  return response.data;
}

// 查询任务状态
async function getTaskStatus(taskId) {
  const response = await client.get(`/exports/tasks/${taskId}`);
  return response.data;
}

// SSE 进度监听
function listenProgress(taskId, onProgress) {
  const eventSource = new EventSource(
    `${API_BASE}/exports/sse/${taskId}`,
    {
      headers: { 'X-API-Key': API_KEY }
    }
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onProgress(data);
    if (data.status === 'completed' || data.status === 'failed') {
      eventSource.close();
    }
  };

  return eventSource;
}
```

### Python (requests)

```python
import requests
import json

API_BASE = 'http://localhost:8080/api/v1'
API_KEY = 'benchmark-api-key-2024'

headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# 查询订单
def get_orders(page=1, page_size=20):
    response = requests.get(
        f'{API_BASE}/orders',
        headers=headers,
        params={'page': page, 'pageSize': page_size}
    )
    return response.json()

# 同步导出
def sync_export(format, limit, conditions=None):
    response = requests.post(
        f'{API_BASE}/exports/sync',
        headers=headers,
        json={
            'format': format,
            'limit': limit,
            'conditions': conditions or {}
        }
    )
    return response.content

# 异步导出
def async_export(format, limit, conditions=None):
    response = requests.post(
        f'{API_BASE}/exports/async',
        headers=headers,
        json={
            'format': format,
            'limit': limit,
            'conditions': conditions or {}
        }
    )
    return response.json()

# 查询任务状态
def get_task_status(task_id):
    response = requests.get(
        f'{API_BASE}/exports/tasks/{task_id}',
        headers=headers
    )
    return response.json()
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

const (
    APIBase = "http://localhost:8080/api/v1"
    APIKey  = "benchmark-api-key-2024"
)

type Client struct {
    client *http.Client
}

func NewClient() *Client {
    return &Client{
        client: &http.Client{},
    }
}

func (c *Client) doRequest(method, path string, body interface{}) (*http.Response, error) {
    var reqBody io.Reader
    if body != nil {
        jsonBody, err := json.Marshal(body)
        if err != nil {
            return nil, err
        }
        reqBody = bytes.NewBuffer(jsonBody)
    }

    req, err := http.NewRequest(method, APIBase+path, reqBody)
    if err != nil {
        return nil, err
    }

    req.Header.Set("X-API-Key", APIKey)
    req.Header.Set("Content-Type", "application/json")

    return c.client.Do(req)
}

// GetOrders 查询订单
func (c *Client) GetOrders(page, pageSize int) (*http.Response, error) {
    path := fmt.Sprintf("/orders?page=%d&pageSize=%d", page, pageSize)
    return c.doRequest("GET", path, nil)
}

// AsyncExport 异步导出
func (c *Client) AsyncExport(format string, limit int, conditions map[string]interface{}) (*http.Response, error) {
    body := map[string]interface{}{
        "format":     format,
        "limit":      limit,
        "conditions": conditions,
    }
    return c.doRequest("POST", "/exports/async", body)
}

// GetTaskStatus 查询任务状态
func (c *Client) GetTaskStatus(taskID string) (*http.Response, error) {
    return c.doRequest("GET", "/exports/tasks/"+taskID, nil)
}
```

## 最佳实践

### 1. 选择合适的导出方式

| 数据量 | 推荐方式 | 说明 |
|--------|---------|------|
| < 10 万条 | 同步导出 | 简单快速 |
| 10-100 万条 | 流式导出 | 内存占用低 |
| > 100 万条 | 异步导出 | 后台处理，不阻塞 |

### 2. 优化查询性能

- 使用合适的筛选条件减少数据量
- 避免查询过大的时间范围
- 使用分页查询

### 3. 处理大文件

- 使用流式下载避免内存溢出
- 及时清理下载的文件
- 监控磁盘空间

### 4. 错误处理

- 实现重试机制
- 记录错误日志
- 提供友好的错误提示
