# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies（带重试机制）
RUN for i in 1 2 3; do \
    apt-get update && apt-get install -y --no-install-recommends --fix-missing \
        gcc \
        libpq-dev \
        curl \
        && rm -rf /var/lib/apt/lists/* && break || \
        (echo "Retry $i/3..." && sleep 5); \
    done

# Install Python dependencies（使用国内镜像源）
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
