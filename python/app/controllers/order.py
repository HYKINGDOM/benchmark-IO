"""
Order controller for handling order-related requests
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.middleware.auth import verify_api_key
from app.schemas.order import OrderListResponse, OrderQueryParams, OrderResponse
from app.services.order import OrderService

router = APIRouter()


@router.get("", response_model=OrderListResponse, summary="查询订单列表")
async def get_orders(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=1000, description="每页数量"),
    order_no: Optional[str] = Query(default=None, description="订单编号"),
    user_id: Optional[int] = Query(default=None, description="用户ID"),
    order_status: Optional[str] = Query(default=None, description="订单状态"),
    start_time: Optional[datetime] = Query(default=None, description="开始时间"),
    end_time: Optional[datetime] = Query(default=None, description="结束时间"),
    min_amount: Optional[Decimal] = Query(default=None, ge=0, description="最小金额"),
    max_amount: Optional[Decimal] = Query(default=None, ge=0, description="最大金额"),
    api_key: str = Depends(verify_api_key),
) -> OrderListResponse:
    """
    查询订单列表

    支持分页、时间范围、状态、金额、用户ID、订单编号筛选

    Args:
        page: 页码
        page_size: 每页数量
        order_no: 订单编号（模糊匹配）
        user_id: 用户ID
        order_status: 订单状态
        start_time: 开始时间
        end_time: 结束时间
        min_amount: 最小金额
        max_amount: 最大金额
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        订单列表响应（包含分页信息）
    """
    # Build query params
    params = OrderQueryParams(
        page=page,
        page_size=page_size,
        order_no=order_no,
        user_id=user_id,
        order_status=order_status,
        start_time=start_time,
        end_time=end_time,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    # Get orders
    orders, total = await OrderService.get_orders(params)

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    # Build response
    return OrderListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[OrderResponse.model_validate(order) for order in orders],
    )


@router.get("/{order_id}", response_model=OrderResponse, summary="查询订单详情")
async def get_order(
    order_id: int,
    api_key: str = Depends(verify_api_key),
) -> OrderResponse:
    """
    查询订单详情

    Args:
        order_id: 订单ID
        api_key: API Key（通过 X-API-Key Header 传递）

    Returns:
        订单详情

    Raises:
        HTTPException: 订单不存在时返回 404
    """
    from fastapi import HTTPException, status

    order = await OrderService.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )

    return OrderResponse.model_validate(order)
