"""
Export service for handling various export operations
"""
import asyncio
import io
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

from app.config import settings
from app.models.order import Order
from app.models.task import ExportTask, TaskStatus
from app.schemas.export import ExportFormat, ExportRequest
from app.schemas.order import OrderQueryParams
from app.services.order import OrderService
from app.services.task import TaskService
from app.utils.csv_writer import CSVWriter
from app.utils.excel_writer import ExcelWriter


class ExportService:
    """Service for export operations"""

    @staticmethod
    async def sync_export(params: ExportRequest) -> tuple[bytes, str, int]:
        """
        Synchronous export - returns file content directly

        Args:
            params: Export request parameters

        Returns:
            Tuple of (file content, filename, file size)
        """
        # Build query params
        query_params = OrderQueryParams(
            order_no=params.order_no,
            user_id=params.user_id,
            order_status=params.order_status,
            start_time=params.start_time,
            end_time=params.end_time,
            min_amount=params.min_amount,
            max_amount=params.max_amount,
            page=1,
            page_size=10000,  # Limit for sync export
        )

        # Get orders
        orders = await OrderService.get_orders_for_export(query_params)

        # Generate file content
        if params.format == ExportFormat.CSV:
            content = await CSVWriter.generate_csv_bytes(orders)
            filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        else:
            content = await ExcelWriter.generate_excel_bytes(orders)
            filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return content, filename, len(content)

    @staticmethod
    async def create_async_export_task(
        params: ExportRequest,
        api_key: Optional[str] = None,
    ) -> ExportTask:
        """
        Create async export task

        Args:
            params: Export request parameters
            api_key: API Key for authentication

        Returns:
            Created export task
        """
        # Build query params dict
        query_params = {
            "order_no": params.order_no,
            "user_id": params.user_id,
            "order_status": params.order_status,
            "start_time": params.start_time.isoformat() if params.start_time else None,
            "end_time": params.end_time.isoformat() if params.end_time else None,
            "min_amount": float(params.min_amount) if params.min_amount else None,
            "max_amount": float(params.max_amount) if params.max_amount else None,
        }

        # Create task
        task = await TaskService.create_task(
            export_format=params.format,
            query_params=query_params,
            api_key=api_key,
        )

        return task

    @staticmethod
    async def process_export_task(task_id: str) -> None:
        """
        Process export task in background

        Args:
            task_id: Task ID to process
        """
        # Get task
        task = await TaskService.get_task_by_id(task_id)
        if not task:
            return

        try:
            # Mark task as started
            await TaskService.start_task(task_id)

            # Parse query params
            query_params_dict = task.query_params or {}
            query_params = OrderQueryParams(
                order_no=query_params_dict.get("order_no"),
                user_id=query_params_dict.get("user_id"),
                order_status=query_params_dict.get("order_status"),
                start_time=(
                    datetime.fromisoformat(query_params_dict["start_time"])
                    if query_params_dict.get("start_time")
                    else None
                ),
                end_time=(
                    datetime.fromisoformat(query_params_dict["end_time"])
                    if query_params_dict.get("end_time")
                    else None
                ),
                min_amount=query_params_dict.get("min_amount"),
                max_amount=query_params_dict.get("max_amount"),
                page=1,
                page_size=1000000,  # Large limit for export
            )

            # Get orders
            orders = await OrderService.get_orders_for_export(query_params)
            total_count = len(orders)

            # Update total count
            await TaskService.update_task_progress(task_id, 0, total_count)

            # Create export directory
            export_dir = Path(settings.EXPORT_DIR)
            export_dir.mkdir(parents=True, exist_ok=True)

            # Generate file
            filename = f"orders_{task_id}.{task.export_format}"
            file_path = export_dir / filename

            # Write file
            if task.export_format == ExportFormat.CSV.value:
                count = await CSVWriter.write_to_file(orders, file_path)
            else:
                count = await ExcelWriter.write_to_file(orders, file_path)

            # Update progress
            await TaskService.update_task_progress(task_id, count, total_count)

            # Mark task as completed
            file_size = file_path.stat().st_size
            await TaskService.complete_task(task_id, str(file_path), file_size)

        except Exception as e:
            # Mark task as failed
            await TaskService.fail_task(task_id, str(e))
            raise

    @staticmethod
    async def stream_export(params: ExportRequest) -> AsyncIterator[bytes]:
        """
        Stream export data

        Args:
            params: Export request parameters

        Yields:
            File content chunks
        """
        # Build query params
        query_params = OrderQueryParams(
            order_no=params.order_no,
            user_id=params.user_id,
            order_status=params.order_status,
            start_time=params.start_time,
            end_time=params.end_time,
            min_amount=params.min_amount,
            max_amount=params.max_amount,
            page=1,
            page_size=1000000,  # Large limit for export
        )

        # Get orders
        orders = await OrderService.get_orders_for_export(query_params)

        # Stream CSV data
        if params.format == ExportFormat.CSV:
            async for chunk in CSVWriter.stream_csv(orders):
                yield chunk.encode("utf-8-sig")
        else:
            # For Excel, we need to generate the entire file first
            # Then stream it in chunks
            content = await ExcelWriter.generate_excel_bytes(orders)
            chunk_size = 8192
            for i in range(0, len(content), chunk_size):
                yield content[i : i + chunk_size]
                await asyncio.sleep(0)

    @staticmethod
    async def get_export_file(token: str) -> Optional[tuple[Path, str]]:
        """
        Get export file by download token

        Args:
            token: Download token

        Returns:
            Tuple of (file path, filename) or None
        """
        # Get task
        task = await TaskService.get_task_by_token(token)
        if not task or not task.is_completed:
            return None

        # Check if file exists
        if not task.file_path:
            return None

        file_path = Path(task.file_path)
        if not file_path.exists():
            return None

        # Generate filename
        filename = f"orders_{task.created_at.strftime('%Y%m%d_%H%M%S')}.{task.export_format}"

        return file_path, filename
