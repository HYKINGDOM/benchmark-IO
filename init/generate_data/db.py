"""
数据库操作模块
使用 psycopg2 进行数据库连接和批量操作
"""
import io
import logging
from contextlib import contextmanager
from typing import Iterator, List, Any, Optional

import psycopg2
from psycopg2.extras import execute_values

from config import config

logger = logging.getLogger(__name__)


class Database:
    """数据库操作类"""
    
    def __init__(self):
        self._connection = None
    
    def connect(self) -> None:
        """建立数据库连接"""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                host=config.database.host,
                port=config.database.port,
                database=config.database.database,
                user=config.database.user,
                password=config.database.password,
            )
            self._connection.autocommit = False
            logger.info(f"数据库连接成功: {config.database.host}:{config.database.port}/{config.database.database}")
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("数据库连接已关闭")
    
    @contextmanager
    def cursor(self) -> Iterator[Any]:
        """获取数据库游标的上下文管理器"""
        self.connect()
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def commit(self) -> None:
        """提交事务"""
        if self._connection:
            self._connection.commit()
    
    def rollback(self) -> None:
        """回滚事务"""
        if self._connection:
            self._connection.rollback()
    
    def execute(self, query: str, params: Optional[tuple] = None) -> None:
        """执行单条SQL语句"""
        with self.cursor() as cursor:
            cursor.execute(query, params)
        self.commit()
    
    def fetchone(self, query: str, params: Optional[tuple] = None) -> Optional[tuple]:
        """查询单条记录"""
        with self.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetchall(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """查询多条记录"""
        with self.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """
        result = self.fetchone(query, (table_name,))
        return result[0] if result else False
    
    def get_table_count(self, table_name: str) -> int:
        """获取表中的记录数"""
        query = f"SELECT COUNT(*) FROM {table_name};"
        result = self.fetchone(query)
        return result[0] if result else 0
    
    def get_max_order_id(self) -> int:
        """获取当前最大订单ID"""
        if not self.table_exists("orders"):
            return 0
        query = "SELECT COALESCE(MAX(order_id), 0) FROM orders;"
        result = self.fetchone(query)
        return result[0] if result else 0
    
    def truncate_table(self, table_name: str) -> None:
        """清空表数据"""
        query = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
        self.execute(query)
        logger.info(f"表 {table_name} 已清空")
    
    def drop_table(self, table_name: str) -> None:
        """删除表"""
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
        self.execute(query)
        logger.info(f"表 {table_name} 已删除")
    
    def reset_sequence(self, sequence_name: str, start_value: int = 1) -> None:
        """重置序列"""
        query = f"ALTER SEQUENCE {sequence_name} RESTART WITH {start_value};"
        self.execute(query)
        logger.info(f"序列 {sequence_name} 已重置为 {start_value}")
    
    def copy_from_csv(self, table_name: str, csv_data: str, columns: List[str]) -> int:
        """
        使用 COPY 命令从 CSV 格式数据批量插入
        
        Args:
            table_name: 目标表名
            csv_data: CSV 格式的数据字符串
            columns: 列名列表
            
        Returns:
            插入的行数
        """
        with self.cursor() as cursor:
            csv_file = io.StringIO(csv_data)
            cursor.copy_from(csv_file, table_name, sep=',', null='', columns=columns)
            row_count = cursor.rowcount
        self.commit()
        return row_count
    
    def batch_insert(self, table_name: str, columns: List[str], values: List[tuple]) -> int:
        """
        使用 execute_values 批量插入数据
        
        Args:
            table_name: 目标表名
            columns: 列名列表
            values: 值元组列表
            
        Returns:
            插入的行数
        """
        if not values:
            return 0
        
        columns_str = ', '.join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES %s"
        
        with self.cursor() as cursor:
            execute_values(cursor, query, values)
            row_count = cursor.rowcount
        self.commit()
        return row_count
    
    def create_orders_table(self) -> None:
        """创建订单表（如果不存在）"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            order_no VARCHAR(32) NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            user_name VARCHAR(50) NOT NULL,
            user_phone VARCHAR(20) NOT NULL,
            user_id_card VARCHAR(18) NOT NULL,
            user_email VARCHAR(100) NOT NULL,
            user_address VARCHAR(200) NOT NULL,
            product_id INTEGER NOT NULL,
            product_name VARCHAR(200) NOT NULL,
            product_category VARCHAR(50) NOT NULL,
            product_price DECIMAL(10, 2) NOT NULL,
            quantity INTEGER NOT NULL,
            total_amount DECIMAL(12, 2) NOT NULL,
            discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
            pay_amount DECIMAL(12, 2) NOT NULL,
            order_status VARCHAR(20) NOT NULL,
            payment_method VARCHAR(20),
            payment_time TIMESTAMP,
            order_source VARCHAR(20) NOT NULL,
            shipping_address VARCHAR(200),
            receiver_name VARCHAR(50),
            receiver_phone VARCHAR(20),
            logistics_no VARCHAR(20),
            delivery_time TIMESTAMP,
            complete_time TIMESTAMP,
            remark TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            is_deleted SMALLINT NOT NULL DEFAULT 0
        );
        
        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_order_status ON orders(order_status);
        CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
        CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);
        CREATE INDEX IF NOT EXISTS idx_orders_order_no ON orders(order_no);
        CREATE INDEX IF NOT EXISTS idx_orders_total_amount ON orders(total_amount);
        CREATE INDEX IF NOT EXISTS idx_orders_payment_time ON orders(payment_time);
        """
        self.execute(create_table_sql)
        logger.info("订单表创建成功")
    
    def ensure_table_exists(self) -> None:
        """确保订单表存在"""
        if not self.table_exists("orders"):
            self.create_orders_table()


# 全局数据库实例
db = Database()
