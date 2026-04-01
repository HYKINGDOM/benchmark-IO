"""
Order model for database
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class Order(Model):
    """
    Order model representing orders table
    """
    # Primary key
    order_id = fields.BigIntField(pk=True, description="订单ID")
    
    # Order basic info
    order_no = fields.CharField(max_length=32, unique=True, description="订单编号")
    
    # User info
    user_id = fields.BigIntField(description="用户ID")
    user_name = fields.CharField(max_length=64, description="用户姓名")
    user_phone = fields.CharField(max_length=11, description="用户手机号")
    user_id_card = fields.CharField(max_length=18, null=True, description="用户身份证")
    user_email = fields.CharField(max_length=128, null=True, description="用户邮箱")
    user_address = fields.CharField(max_length=256, null=True, description="用户地址")
    
    # Product info
    product_id = fields.BigIntField(description="商品ID")
    product_name = fields.CharField(max_length=128, description="商品名称")
    product_category = fields.CharField(max_length=64, description="商品分类")
    product_price = fields.DecimalField(max_digits=10, decimal_places=2, description="商品单价")
    quantity = fields.IntField(description="购买数量")
    
    # Amount info
    total_amount = fields.DecimalField(max_digits=12, decimal_places=2, description="订单总金额")
    discount_amount = fields.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), description="优惠金额")
    pay_amount = fields.DecimalField(max_digits=12, decimal_places=2, description="实付金额")
    
    # Order status
    order_status = fields.CharField(max_length=16, description="订单状态")
    payment_method = fields.CharField(max_length=16, null=True, description="支付方式")
    payment_time = fields.DatetimeField(null=True, description="支付时间")
    
    # Order source
    order_source = fields.CharField(max_length=32, null=True, description="订单来源")
    
    # Shipping info
    shipping_address = fields.CharField(max_length=512, null=True, description="收货地址")
    receiver_name = fields.CharField(max_length=64, null=True, description="收货人姓名")
    receiver_phone = fields.CharField(max_length=11, null=True, description="收货人电话")
    logistics_no = fields.CharField(max_length=32, null=True, description="物流单号")
    delivery_time = fields.DatetimeField(null=True, description="发货时间")
    complete_time = fields.DatetimeField(null=True, description="完成时间")
    
    # Remark
    remark = fields.CharField(max_length=512, null=True, description="备注")
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # Soft delete
    is_deleted = fields.SmallIntField(default=0, description="是否删除 0-未删除 1-已删除")

    class Meta:
        table = "orders"
        table_description = "订单表"

    def __str__(self) -> str:
        return f"Order({self.order_no})"

    def __repr__(self) -> str:
        return (
            f"<Order order_id={self.order_id} order_no={self.order_no} "
            f"user_id={self.user_id} status={self.order_status}>"
        )

    @classmethod
    def get_active_orders(cls):
        """Get all non-deleted orders"""
        return cls.filter(is_deleted=0)

    async def soft_delete(self) -> None:
        """Soft delete the order"""
        self.is_deleted = 1
        await self.save(update_fields=["is_deleted", "updated_at"])
