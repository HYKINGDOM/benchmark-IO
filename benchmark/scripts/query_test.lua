-- wrk 查询接口测试脚本
-- 支持多种查询条件组合

-- 配置
local api_key = "benchmark-api-key-2024"

-- 请求参数配置（可通过命令行参数覆盖）
-- wrk -s query_test.lua --latency -t4 -c10 -d30s http://localhost:8080/api/v1/orders
-- 可选参数: -e "start_date=2024-01-01" -e "end_date=2024-12-31" -e "status=paid"

-- 初始化
local counter = 0
local start_date = os.getenv("start_date") or "2024-01-01"
local end_date = os.getenv("end_date") or "2024-12-31"
local order_status = os.getenv("order_status") or ""
local min_amount = os.getenv("min_amount") or ""
local max_amount = os.getenv("max_amount") or ""
local user_id = os.getenv("user_id") or ""
local region = os.getenv("region") or ""
local page = os.getenv("page") or "1"
local page_size = os.getenv("page_size") or "20"

-- 构建查询参数
local function build_query_params()
    local params = {}
    
    table.insert(params, "page=" .. page)
    table.insert(params, "page_size=" .. page_size)
    
    if start_date and start_date ~= "" then
        table.insert(params, "start_date=" .. start_date)
    end
    
    if end_date and end_date ~= "" then
        table.insert(params, "end_date=" .. end_date)
    end
    
    if order_status and order_status ~= "" then
        table.insert(params, "status=" .. order_status)
    end
    
    if min_amount and min_amount ~= "" then
        table.insert(params, "min_amount=" .. min_amount)
    end
    
    if max_amount and max_amount ~= "" then
        table.insert(params, "max_amount=" .. max_amount)
    end
    
    if user_id and user_id ~= "" then
        table.insert(params, "user_id=" .. user_id)
    end
    
    if region and region ~= "" then
        table.insert(params, "region=" .. region)
    end
    
    return table.concat(params, "&")
end

-- 设置请求
function setup(thread)
    thread:set("id", counter)
    counter = counter + 1
end

-- 初始化请求
function init(args)
    print("Query Test initialized with:")
    print("  start_date: " .. start_date)
    print("  end_date: " .. end_date)
    print("  status: " .. order_status)
    print("  page: " .. page)
    print("  page_size: " .. page_size)
end

-- 延迟函数
function delay()
    return math.random(100, 500) -- 100-500ms 延迟模拟用户思考时间
end

-- 请求函数
function request()
    local query_params = build_query_params()
    local path = "/api/v1/orders?" .. query_params
    
    return wrk.format("GET", path, {
        ["X-API-Key"] = api_key,
        ["Content-Type"] = "application/json"
    })
end

-- 响应处理
function response(status, headers, body)
    if status ~= 200 then
        print("Error: " .. status .. " - " .. body)
    end
end

-- 完成统计
function done(summary, latency, requests)
    print("\n=== Query Test Summary ===")
    print("Total requests: " .. summary.requests)
    print("Total duration: " .. summary.duration / 1000000 .. " ms")
    print("Requests/sec: " .. summary.requests / (summary.duration / 1000000000))
    print("\nLatency distribution:")
    print("  Avg: " .. latency.mean / 1000 .. " ms")
    print("  Stdev: " .. latency.stdev / 1000 .. " ms")
    print("  Max: " .. latency.max / 1000 .. " ms")
    print("  Min: " .. latency.min / 1000 .. " ms")
    print("  50th percentile: " .. latency:percentile(50) / 1000 .. " ms")
    print("  75th percentile: " .. latency:percentile(75) / 1000 .. " ms")
    print("  90th percentile: " .. latency:percentile(90) / 1000 .. " ms")
    print("  99th percentile: " .. latency:percentile(99) / 1000 .. " ms")
end
