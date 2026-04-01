"""
Export controller for handling export-related requests
"""
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.responses import Response as FastAPIResponse

from app.middleware.auth import verify_api_key
from app.schemas.export import ExportFormat, ExportRequest, ExportTaskResponse
from app.services.export import ExportService
from app.services.task import TaskService

router = APIRouter()


@router.post("/sync", summary="同步导出")
async def sync_export(
    params: ExportRequest,
    api_key: str = Depends(verify_api_key),
) -> StreamingResponse:
    """
    同步导出订单数据

    直接返回文件流，适合数据量较小的场景

    Args:
        params: 导出请求参数
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        文件流响应
    """
    # Export data
    content, filename, file_size = await ExportService.sync_export(params)

    # Determine content type
    content_type = (
        "text/csv; charset=utf-8"
        if params.format == ExportFormat.CSV
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Return streaming response
    return StreamingResponse(
        iter([content]),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(file_size),
        },
    )


@router.post("/async", response_model=ExportTaskResponse, summary="异步导出")
async def async_export(
    params: ExportRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
) -> ExportTaskResponse:
    """
    异步导出订单数据

    创建后台任务，返回任务ID，适合数据量较大的场景

    Args:
        params: 导出请求参数
        background_tasks: FastAPI 后台任务
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        导出任务响应（包含任务ID）
    """
    # Create task
    task = await ExportService.create_async_export_task(params, api_key)

    # Add background task to process export
    background_tasks.add_task(ExportService.process_export_task, task.task_id)

    # Return task response
    return ExportTaskResponse.model_validate(task)


@router.get("/tasks/{task_id}", response_model=ExportTaskResponse, summary="查询任务状态")
async def get_task_status(
    task_id: str,
    api_key: str = Depends(verify_api_key),
) -> ExportTaskResponse:
    """
    查询导出任务状态

    Args:
        task_id: 任务ID
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        任务状态响应

    Raises:
        HTTPException: 任务不存在时返回 404
    """
    task = await TaskService.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return ExportTaskResponse.model_validate(task)


@router.get("/sse/{task_id}", summary="SSE 进度推送")
async def sse_progress(
    task_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    SSE 进度推送

    通过 Server-Sent Events 实时推送导出进度

    Args:
        task_id: 任务ID
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        SSE 事件流
    """
    from fastapi.responses import StreamingResponse
    import json

    async def event_generator():
        """Generate SSE events"""
        while True:
            # Get task
            task = await TaskService.get_task_by_id(task_id)
            if not task:
                yield f"event: error\ndata: {json.dumps({'error': 'Task not found'})}\n\n"
                break

            # Send progress update
            data = {
                "task_id": task.task_id,
                "status": task.status.value,
                "progress": task.progress,
                "processed_count": task.processed_count,
                "total_count": task.total_count,
                "error_message": task.error_message,
            }
            yield f"event: progress\ndata: {json.dumps(data)}\n\n"

            # Check if task is completed or failed
            if task.is_completed or task.is_failed:
                # Send final event
                yield f"event: complete\ndata: {json.dumps(data)}\n\n"
                break

            # Wait before next update
            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/download/{token}", summary="文件下载")
async def download_file(
    token: str,
    api_key: str = Depends(verify_api_key),
) -> FileResponse:
    """
    通过下载令牌下载导出文件

    Args:
        token: 下载令牌
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        文件响应

    Raises:
        HTTPException: 文件不存在时返回 404
    """
    # Get file
    result = await ExportService.get_export_file(token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or download link expired",
        )

    file_path, filename = result

    # Determine content type
    content_type = (
        "text/csv; charset=utf-8"
        if file_path.suffix == ".csv"
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Return file response
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=content_type,
    )


@router.post("/stream", summary="流式导出")
async def stream_export(
    params: ExportRequest,
    api_key: str = Depends(verify_api_key),
) -> StreamingResponse:
    """
    流式导出订单数据

    以流的方式返回数据，适合大数据量导出

    Args:
        params: 导出请求参数
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        流式响应
    """
    # Determine content type
    content_type = (
        "text/csv; charset=utf-8"
        if params.format == ExportFormat.CSV
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Generate filename
    filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{params.format.value}"

    # Return streaming response
    return StreamingResponse(
        ExportService.stream_export(params),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Transfer-Encoding": "chunked",
        },
    )
