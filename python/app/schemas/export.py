"""
Export schemas for request/response validation
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Export format enumeration"""
    CSV = "csv"
    XLSX = "xlsx"


class ExportRequest(BaseModel):
    """Export request parameters"""
    format: ExportFormat = Field(default=ExportFormat.CSV, description="导出格式")
    order_no: Optional[str] = Field(None, description="订单编号")
    user_id: Optional[int] = Field(None, description="用户ID")
    order_status: Optional[str] = Field(None, description="订单状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    min_amount: Optional[float] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[float] = Field(None, ge=0, description="最大金额")

    class Config:
        json_schema_extra = {
            "example": {
                "format": "csv",
                "order_no": "ORD202401010001",
                "user_id": 10001,
                "order_status": "completed",
                "start_time": "2024-01-01T00:00:00",
                "end_time": "2024-12-31T23:59:59",
                "min_amount": 100.00,
                "max_amount": 10000.00,
            }
        }


class ExportTaskStatus(str, Enum):
    """Export task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportTaskResponse(BaseModel):
    """Export task response"""
    task_id: str = Field(..., description="任务ID")
    status: ExportTaskStatus = Field(..., description="任务状态")
    progress: int = Field(default=0, ge=0, le=100, description="进度百分比")
    total_count: int = Field(default=0, description="总记录数")
    processed_count: int = Field(default=0, description="已处理记录数")
    download_token: Optional[str] = Field(None, description="下载令牌")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "progress": 100,
                "total_count": 1000,
                "processed_count": 1000,
                "download_token": "abc123token",
                "file_size": 102400,
                "error_message": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:01:00",
                "completed_at": "2024-01-01T00:01:00",
            }
        }


class ExportTaskCreate(BaseModel):
    """Export task creation parameters"""
    task_id: str = Field(..., description="任务ID")
    export_format: ExportFormat = Field(default=ExportFormat.CSV, description="导出格式")
    query_params: dict[str, Any] = Field(default_factory=dict, description="查询参数")
    api_key: Optional[str] = Field(None, description="API Key")


class SSEProgressEvent(BaseModel):
    """SSE progress event"""
    event: str = Field(default="progress", description="事件类型")
    data: dict[str, Any] = Field(..., description="事件数据")

    class Config:
        json_schema_extra = {
            "example": {
                "event": "progress",
                "data": {
                    "task_id": "550e8400-e29b-41d4-a716-446655440000",
                    "progress": 50,
                    "processed_count": 500,
                    "total_count": 1000,
                },
            }
        }
