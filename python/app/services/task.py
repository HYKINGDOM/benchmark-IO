"""
Task service for export task management
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings
from app.models.task import ExportTask, TaskStatus
from app.schemas.export import ExportFormat


class TaskService:
    """Service for export task operations"""

    @staticmethod
    async def create_task(
        export_format: ExportFormat,
        query_params: dict,
        api_key: Optional[str] = None,
    ) -> ExportTask:
        """
        Create a new export task

        Args:
            export_format: Export format (CSV/XLSX)
            query_params: Query parameters for export
            api_key: API Key for authentication

        Returns:
            Created export task
        """
        # Generate unique task ID
        import uuid

        task_id = str(uuid.uuid4())

        # Generate download token
        download_token = secrets.token_urlsafe(32)

        # Set expiration time
        expires_at = datetime.now() + timedelta(hours=settings.EXPORT_FILE_EXPIRE_HOURS)

        # Create task
        task = await ExportTask.create(
            task_id=task_id,
            download_token=download_token,
            export_format=export_format.value,
            query_params=query_params,
            api_key=api_key,
            expires_at=expires_at,
        )

        return task

    @staticmethod
    async def get_task_by_id(task_id: str) -> Optional[ExportTask]:
        """
        Get task by task ID

        Args:
            task_id: Task ID

        Returns:
            Export task or None
        """
        return await ExportTask.filter(task_id=task_id).first()

    @staticmethod
    async def get_task_by_token(token: str) -> Optional[ExportTask]:
        """
        Get task by download token

        Args:
            token: Download token

        Returns:
            Export task or None
        """
        return await ExportTask.filter(download_token=token).first()

    @staticmethod
    async def update_task_progress(
        task_id: str,
        processed: int,
        total: int,
    ) -> Optional[ExportTask]:
        """
        Update task progress

        Args:
            task_id: Task ID
            processed: Number of processed records
            total: Total number of records

        Returns:
            Updated task or None
        """
        task = await ExportTask.filter(task_id=task_id).first()
        if task:
            await task.update_progress(processed, total)
        return task

    @staticmethod
    async def start_task(task_id: str) -> Optional[ExportTask]:
        """
        Mark task as started

        Args:
            task_id: Task ID

        Returns:
            Updated task or None
        """
        task = await ExportTask.filter(task_id=task_id).first()
        if task:
            await task.start()
        return task

    @staticmethod
    async def complete_task(
        task_id: str,
        file_path: str,
        file_size: int,
    ) -> Optional[ExportTask]:
        """
        Mark task as completed

        Args:
            task_id: Task ID
            file_path: Path to generated file
            file_size: Size of generated file

        Returns:
            Updated task or None
        """
        task = await ExportTask.filter(task_id=task_id).first()
        if task:
            await task.complete(file_path, file_size)
        return task

    @staticmethod
    async def fail_task(task_id: str, error_message: str) -> Optional[ExportTask]:
        """
        Mark task as failed

        Args:
            task_id: Task ID
            error_message: Error message

        Returns:
            Updated task or None
        """
        task = await ExportTask.filter(task_id=task_id).first()
        if task:
            await task.fail(error_message)
        return task

    @staticmethod
    async def cleanup_expired_tasks() -> int:
        """
        Clean up expired tasks

        Returns:
            Number of deleted tasks
        """
        now = datetime.now()
        expired_tasks = await ExportTask.filter(expires_at__lt=now).all()

        count = 0
        for task in expired_tasks:
            # Delete associated files
            if task.file_path:
                from pathlib import Path

                file_path = Path(task.file_path)
                if file_path.exists():
                    file_path.unlink()

            # Delete task
            await task.delete()
            count += 1

        return count

    @staticmethod
    async def get_active_tasks_count() -> int:
        """
        Get count of active (pending/processing) tasks

        Returns:
            Count of active tasks
        """
        return await ExportTask.filter(
            status__in=[TaskStatus.PENDING, TaskStatus.PROCESSING]
        ).count()
