"""
Export task model for database
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportTask(Model):
    """
    Export task model for tracking async export operations
    """
    # Primary key
    id = fields.BigIntField(pk=True, description="任务ID")
    
    # Task identification
    task_id = fields.CharField(max_length=64, unique=True, index=True, description="任务UUID")
    download_token = fields.CharField(max_length=64, null=True, unique=True, description="下载令牌")
    
    # Task info
    task_type = fields.CharField(max_length=32, default="export", description="任务类型")
    export_format = fields.CharField(max_length=10, default="csv", description="导出格式 csv/xlsx")
    
    # Status
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.PENDING, description="任务状态")
    progress = fields.IntField(default=0, description="进度百分比 0-100")
    total_count = fields.IntField(default=0, description="总记录数")
    processed_count = fields.IntField(default=0, description="已处理记录数")
    
    # File info
    file_path = fields.CharField(max_length=512, null=True, description="文件路径")
    file_size = fields.BigIntField(null=True, description="文件大小(字节)")
    
    # Error info
    error_message = fields.TextField(null=True, description="错误信息")
    
    # Query parameters (JSON)
    query_params = fields.JSONField(null=True, description="查询参数")
    
    # API Key
    api_key = fields.CharField(max_length=128, null=True, description="API Key")
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    
    # Expiration
    expires_at = fields.DatetimeField(null=True, description="过期时间")

    class Meta:
        table = "export_tasks"
        table_description = "导出任务表"
        indexes = [
            ("task_id",),
            ("download_token",),
            ("status",),
            ("created_at",),
        ]

    def __str__(self) -> str:
        return f"ExportTask({self.task_id})"

    def __repr__(self) -> str:
        return (
            f"<ExportTask id={self.id} task_id={self.task_id} "
            f"status={self.status} progress={self.progress}%>"
        )

    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if task is failed"""
        return self.status == TaskStatus.FAILED

    @property
    def is_pending(self) -> bool:
        """Check if task is pending"""
        return self.status == TaskStatus.PENDING

    @property
    def is_processing(self) -> bool:
        """Check if task is processing"""
        return self.status == TaskStatus.PROCESSING

    async def start(self) -> None:
        """Mark task as started"""
        self.status = TaskStatus.PROCESSING
        self.started_at = datetime.now()
        await self.save(update_fields=["status", "started_at", "updated_at"])

    async def complete(self, file_path: str, file_size: int) -> None:
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.file_path = file_path
        self.file_size = file_size
        self.completed_at = datetime.now()
        await self.save(update_fields=[
            "status", "progress", "file_path", "file_size", 
            "completed_at", "updated_at"
        ])

    async def fail(self, error_message: str) -> None:
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()
        await self.save(update_fields=["status", "error_message", "completed_at", "updated_at"])

    async def update_progress(self, processed: int, total: int) -> None:
        """Update task progress"""
        self.processed_count = processed
        self.total_count = total
        if total > 0:
            self.progress = int((processed / total) * 100)
        await self.save(update_fields=["processed_count", "total_count", "progress", "updated_at"])
