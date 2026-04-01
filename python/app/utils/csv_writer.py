"""
CSV writer utility for exporting orders
"""
import asyncio
import csv
import io
from pathlib import Path
from typing import AsyncIterator

from app.models.order import Order


class CSVWriter:
    """CSV writer for order exports"""

    # CSV headers mapping
    HEADERS = [
        "订单ID",
        "订单编号",
        "用户ID",
        "用户姓名",
        "用户手机号",
        "用户身份证",
        "用户邮箱",
        "用户地址",
        "商品ID",
        "商品名称",
        "商品分类",
        "商品单价",
        "购买数量",
        "订单总金额",
        "优惠金额",
        "实付金额",
        "订单状态",
        "支付方式",
        "支付时间",
        "订单来源",
        "收货地址",
        "收货人姓名",
        "收货人电话",
        "物流单号",
        "发货时间",
        "完成时间",
        "备注",
        "创建时间",
        "更新时间",
    ]

    FIELDS = [
        "order_id",
        "order_no",
        "user_id",
        "user_name",
        "user_phone",
        "user_id_card",
        "user_email",
        "user_address",
        "product_id",
        "product_name",
        "product_category",
        "product_price",
        "quantity",
        "total_amount",
        "discount_amount",
        "pay_amount",
        "order_status",
        "payment_method",
        "payment_time",
        "order_source",
        "shipping_address",
        "receiver_name",
        "receiver_phone",
        "logistics_no",
        "delivery_time",
        "complete_time",
        "remark",
        "created_at",
        "updated_at",
    ]

    @staticmethod
    def format_value(value) -> str:
        """Format a value for CSV output"""
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            return str(value)
        return str(value)

    @classmethod
    async def write_to_file(
        cls,
        orders: list[Order],
        file_path: Path,
        batch_size: int = 1000,
    ) -> int:
        """
        Write orders to CSV file asynchronously

        Args:
            orders: List of order objects
            file_path: Output file path
            batch_size: Number of records to process in each batch

        Returns:
            Number of records written
        """
        count = 0

        # Create parent directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

            # Write header
            writer.writerow(cls.HEADERS)

            # Write data in batches
            for i in range(0, len(orders), batch_size):
                batch = orders[i : i + batch_size]

                for order in batch:
                    row = [cls.format_value(getattr(order, field)) for field in cls.FIELDS]
                    writer.writerow(row)
                    count += 1

                # Yield control to event loop
                await asyncio.sleep(0)

        return count

    @classmethod
    async def stream_csv(
        cls,
        orders: list[Order],
        batch_size: int = 1000,
    ) -> AsyncIterator[str]:
        """
        Stream CSV data as string chunks

        Args:
            orders: List of order objects
            batch_size: Number of records to process in each batch

        Yields:
            CSV string chunks
        """
        # Create string buffer
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Write header
        writer.writerow(cls.HEADERS)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        # Write data in batches
        for i in range(0, len(orders), batch_size):
            batch = orders[i : i + batch_size]

            for order in batch:
                row = [cls.format_value(getattr(order, field)) for field in cls.FIELDS]
                writer.writerow(row)

            # Yield the batch
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

            # Yield control to event loop
            await asyncio.sleep(0)

    @classmethod
    async def generate_csv_bytes(cls, orders: list[Order]) -> bytes:
        """
        Generate CSV content as bytes

        Args:
            orders: List of order objects

        Returns:
            CSV content as bytes
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Write header
        writer.writerow(cls.HEADERS)

        # Write data
        for order in orders:
            row = [cls.format_value(getattr(order, field)) for field in cls.FIELDS]
            writer.writerow(row)

        return output.getvalue().encode("utf-8-sig")
