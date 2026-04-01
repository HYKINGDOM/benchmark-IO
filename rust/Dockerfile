# 构建阶段
FROM rust:1.75 AS builder

WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制 Cargo 文件
COPY Cargo.toml Cargo.lock ./

# 创建空的 src 目录和 main.rs 以缓存依赖
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs

# 构建依赖（利用 Docker 缓存）
RUN cargo build --release && rm -rf src

# 复制源代码
COPY src ./src

# 构建应用
RUN touch src/main.rs && cargo build --release

# 运行阶段
FROM debian:bookworm-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制二进制文件
COPY --from=builder /app/target/release/benchmark-io /usr/local/bin/benchmark-io

# 创建导出目录
RUN mkdir -p /app/exports

# 设置环境变量
ENV RUST_LOG=info
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8080
ENV EXPORT_DIR=/app/exports

# 暴露端口
EXPOSE 8080

# 启动应用
CMD ["benchmark-io"]
