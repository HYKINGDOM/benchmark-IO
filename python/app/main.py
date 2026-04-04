"""
FastAPI application main entry point
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

# Prometheus monitoring
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.controllers import api_router
from tortoise import Tortoise

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize database
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.models.order", "app.models.task"]},
    )

    # Note: Tables are created by init.sql, skip auto schema generation
    # await Tortoise.generate_schemas(safe=True)

    # Create export directory
    export_dir = Path(settings.EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Database connection established")
    logger.info(f"Export directory: {export_dir}")

    yield

    # Shutdown
    logger.info("Shutting down application")

    # Close database connections
    await Tortoise.close_connections()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Benchmark IO Python API - 订单数据查询与导出服务

    ## 功能特性

    * **订单查询**: 支持分页、多条件筛选的订单查询
    * **同步导出**: 直接返回文件流，适合小数据量导出
    * **异步导出**: 后台任务处理，适合大数据量导出
    * **SSE 推送**: 实时推送导出进度
    * **流式导出**: 流式返回数据，适合大数据量导出

    ## 认证方式

    所有 API 接口需要通过 `X-API-Key` Header 进行认证。

    ## 导出格式

    * **CSV**: 文本格式，体积小，适合大数据量
    * **XLSX**: Excel 格式，支持样式，适合小数据量
    """,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "detail": exc.errors(),
                "body": exc.body,
            }
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Initialize Prometheus instrumentation
Instrumentator().instrument(app).expose(app)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint

    Returns basic health status of the application
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint

    Returns basic information about the API
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/api/v1/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
