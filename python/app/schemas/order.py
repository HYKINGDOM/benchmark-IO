"""
Order schemas for request/response validation
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    """Base order schema"""
    order_no: str = Field(..., description="订单编号")
    user_id: int = Field(..., description="用户ID")
    user_name: str = Field(..., description="用户姓名")
    user_phone: str = Field(..., description="用户手机号")
    user_id_card: Optional[str] = Field(None, description="用户身份证")
    user_email: Optional[str] = Field(None, description="用户邮箱")
    user_address: Optional[str] = Field(None, description="用户地址")
    product_id: int = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_category: str = Field(..., description="商品分类")
    product_price: Decimal = Field(..., description="商品单价")
    quantity: int = Field(..., description="购买数量")
    total_amount: Decimal = Field(..., description="订单总金额")
    discount_amount: Decimal = Field(default=Decimal("0.00"), description="优惠金额")
    pay_amount: Decimal = Field(..., description="实付金额")
    order_status: str = Field(..., description="订单状态")
    payment_method: Optional[str] = Field(None, description="支付方式")
    payment_time: Optional[datetime] = Field(None, description="支付时间")
    order_source: Optional[str] = Field(None, description="订单来源")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    receiver_name: Optional[str] = Field(None, description="收货人姓名")
    receiver_phone: Optional[str] = Field(None, description="收货人电话")
    logistics_no: Optional[str] = Field(None, description="物流单号")
    delivery_time: Optional[datetime] = Field(None, description="发货时间")
    complete_time: Optional[datetime] = Field(None, description="完成时间")
    remark: Optional[str] = Field(None, description="备注")


class OrderResponse(OrderBase):
    """Order response schema"""
    order_id: int = Field(..., description="订单ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: int = Field(default=0, description="是否删除")

    class Config:
        from_attributes = True


class OrderQueryParams(BaseModel):
    """Order query parameters"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=1000, description="每页数量")
    order_no: Optional[str] = Field(None, description="订单编号")
    user_id: Optional[int] = Field(None, description="用户ID")
    order_status: Optional[str] = Field(None, description="订单状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大金额")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "order_no": "ORD202401010001",
                "user_id": 10001,
                "order_status": "completed",
                "start_time": "2024-01-01T00:00:00",
                "end_time": "2024-12-31T23:59:59",
                "min_amount": 100.00,
                "max_amount": 10000.00,
            }
        }


class OrderListResponse(BaseModel):
    """Order list response with pagination"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    items: list[OrderResponse] = Field(..., description="订单列表")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "items": [],
            }
        }
