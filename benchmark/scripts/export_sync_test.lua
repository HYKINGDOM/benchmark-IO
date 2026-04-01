-- wrk 同步导出测试脚本
-- 测试同步导出接口性能

local api_key = "benchmark-api-key-2024"

-- 配置参数
local start_date = os.getenv("start_date") or "2024-01-01"
local end_date = os.getenv("end_date") or "2024-12-31"
local order_status = os.getenv("order_status") or ""
local min_amount = os.getenv("min_amount") or ""
local max_amount = os.getenv("max_amount") or ""
local user_id = os.getenv("user_id") or ""
local region = os.getenv("region") or ""
local format = os.getenv("format") or "csv"

-- 构建请求体
local function build_request_body()
    local body = {
        start_date = start_date,
        end_date = end_date,
        format = format
    }
    
    if order_status and order_status ~= "" then
        body.status = order_status
    end
    
    if min_amount and min_amount ~= "" then
        body.min_amount = tonumber(min_amount)
    end
    
    if max_amount and max_amount ~= "" then
        body.max_amount = tonumber(max_amount)
    end
    
    if user_id and user_id ~= "" then
        body.user_id = user_id
    end
    
    if region and region ~= "" then
        body.region = region
    end
    
    return body
end

function init(args)
    print("Sync Export Test initialized")
    print("  Format: " .. format)
    print("  Date range: " .. start_date .. " to " .. end_date)
end

function request()
    local body = build_request_body()
    local json_body = '{"start_date":"' .. body.start_date .. '","end_date":"' .. body.end_date .. '","format":"' .. body.format .. '"'
    
    if body.status then
        json_body = json_body .. ',"status":"' .. body.status .. '"'
    end
    if body.min_amount then
        json_body = json_body .. ',"min_amount":' .. body.min_amount
    end
    if body.max_amount then
        json_body = json_body .. ',"max_amount":' .. body.max_amount
    end
    if body.user_id then
        json_body = json_body .. ',"user_id":"' .. body.user_id .. '"'
    end
    if body.region then
        json_body = json_body .. ',"region":"' .. body.region .. '"'
    end
    
    json_body = json_body .. '}'
    
    return wrk.format("POST", "/api/v1/exports/sync", {
        ["X-API-Key"] = api_key,
        ["Content-Type"] = "application/json"
    }, json_body)
end

function response(status, headers, body)
    if status ~= 200 then
        print("Sync Export Error: " .. status .. " - " .. body)
    end
end

function done(summary, latency, requests)
    print("\n=== Sync Export Test Summary ===")
    print("Total requests: " .. summary.requests)
    print("Total duration: " .. summary.duration / 1000000 .. " ms")
    print("Requests/sec: " .. summary.requests / (summary.duration / 1000000000))
    print("\nLatency distribution:")
    print("  Avg: " .. latency.mean / 1000 .. " ms")
    print("  Max: " .. latency.max / 1000 .. " ms")
    print("  99th percentile: " .. latency:percentile(99) / 1000 .. " ms")
end
