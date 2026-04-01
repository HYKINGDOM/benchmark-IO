"""
Order service for business logic
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.order import Order
from app.schemas.order import OrderQueryParams


class OrderService:
    """Service for order-related operations"""

    @staticmethod
    async def get_orders(params: OrderQueryParams) -> tuple[list[Order], int]:
        """
        Get orders with filtering and pagination

        Args:
            params: Query parameters

        Returns:
            Tuple of (orders list, total count)
        """
        # Start with base query (non-deleted orders)
        query = Order.filter(is_deleted=0)

        # Apply filters
        if params.order_no:
            query = query.filter(order_no__icontains=params.order_no)

        if params.user_id:
            query = query.filter(user_id=params.user_id)

        if params.order_status:
            query = query.filter(order_status=params.order_status)

        if params.start_time:
            query = query.filter(created_at__gte=params.start_time)

        if params.end_time:
            query = query.filter(created_at__lte=params.end_time)

        if params.min_amount is not None:
            query = query.filter(pay_amount__gte=params.min_amount)

        if params.max_amount is not None:
            query = query.filter(pay_amount__lte=params.max_amount)

        # Get total count
        total = await query.count()

        # Apply pagination
        offset = (params.page - 1) * params.page_size
        orders = (
            await query.order_by("-created_at")
            .offset(offset)
            .limit(params.page_size)
            .all()
        )

        return orders, total

    @staticmethod
    async def get_order_by_id(order_id: int) -> Optional[Order]:
        """
        Get order by ID

        Args:
            order_id: Order ID

        Returns:
            Order object or None
        """
        return await Order.filter(order_id=order_id, is_deleted=0).first()

    @staticmethod
    async def get_order_by_no(order_no: str) -> Optional[Order]:
        """
        Get order by order number

        Args:
            order_no: Order number

        Returns:
            Order object or None
        """
        return await Order.filter(order_no=order_no, is_deleted=0).first()

    @staticmethod
    async def get_orders_for_export(params: OrderQueryParams) -> list[Order]:
        """
        Get all orders matching criteria for export (no pagination)

        Args:
            params: Query parameters

        Returns:
            List of matching orders
        """
        # Start with base query (non-deleted orders)
        query = Order.filter(is_deleted=0)

        # Apply filters
        if params.order_no:
            query = query.filter(order_no__icontains=params.order_no)

        if params.user_id:
            query = query.filter(user_id=params.user_id)

        if params.order_status:
            query = query.filter(order_status=params.order_status)

        if params.start_time:
            query = query.filter(created_at__gte=params.start_time)

        if params.end_time:
            query = query.filter(created_at__lte=params.end_time)

        if params.min_amount is not None:
            query = query.filter(pay_amount__gte=params.min_amount)

        if params.max_amount is not None:
            query = query.filter(pay_amount__lte=params.max_amount)

        # Get all matching orders
        orders = await query.order_by("-created_at").all()

        return orders

    @staticmethod
    async def count_orders(params: OrderQueryParams) -> int:
        """
        Count orders matching criteria

        Args:
            params: Query parameters

        Returns:
            Count of matching orders
        """
        # Start with base query (non-deleted orders)
        query = Order.filter(is_deleted=0)

        # Apply filters
        if params.order_no:
            query = query.filter(order_no__icontains=params.order_no)

        if params.user_id:
            query = query.filter(user_id=params.user_id)

        if params.order_status:
            query = query.filter(order_status=params.order_status)

        if params.start_time:
            query = query.filter(created_at__gte=params.start_time)

        if params.end_time:
            query = query.filter(created_at__lte=params.end_time)

        if params.min_amount is not None:
            query = query.filter(pay_amount__gte=params.min_amount)

        if params.max_amount is not None:
            query = query.filter(pay_amount__lte=params.max_amount)

        return await query.count()
