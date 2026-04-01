# 构建阶段
FROM golang:1.23-alpine AS builder

WORKDIR /app

# 安装依赖
RUN apk add --no-cache git

# 复制 go.mod 和 go.sum
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/main.go

# 运行阶段
FROM alpine:latest

WORKDIR /app

# 安装 ca-certificates（用于 HTTPS）
RUN apk --no-cache add ca-certificates tzdata

# 设置时区
ENV TZ=Asia/Shanghai

# 从构建阶段复制可执行文件
COPY --from=builder /app/main .

# 创建导出目录
RUN mkdir -p /tmp/exports

# 暴露端口
EXPOSE 8081

# 设置环境变量
ENV SERVER_PORT=8081 \
    GIN_MODE=release \
    DB_HOST=localhost \
    DB_PORT=5432 \
    DB_USER=benchmark \
    DB_PASSWORD=benchmark123 \
    DB_NAME=benchmark \
    DB_SSLMODE=disable \
    API_KEY=benchmark-api-key-2024 \
    EXPORT_MAX_CONCURRENT=10 \
    EXPORT_CHUNK_SIZE=10000 \
    EXPORT_OUTPUT_DIR=/tmp/exports

# 运行应用
CMD ["./main"]
