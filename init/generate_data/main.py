#!/usr/bin/env python3
"""
订单数据生成工具主程序
支持全量生成、增量生成、数据清理等功能
"""
import argparse
import logging
import sys
import time
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
from typing import List, Optional

from config import config
from db import db
from generator import DataGenerator, OrderDataConverter, ORDER_COLUMNS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def generate_batch_worker(args: tuple) -> List[tuple]:
    """
    批量生成工作进程
    
    Args:
        args: (start_id, batch_size)
        
    Returns:
        订单数据元组列表
    """
    start_id, batch_size = args
    generator = DataGenerator()
    orders = generator.generate_batch(start_id, batch_size)
    return [OrderDataConverter.to_tuple(order) for order in orders]


class DataGenerationManager:
    """数据生成管理器"""
    
    def __init__(self):
        self.generator = DataGenerator()
        self.converter = OrderDataConverter()
    
    def generate_full_data(
        self, 
        total_records: int = None, 
        batch_size: int = None,
        num_workers: int = None
    ) -> None:
        """
        全量生成数据
        
        Args:
            total_records: 总记录数
            batch_size: 批次大小
            num_workers: 并发工作进程数
        """
        total_records = total_records or config.generation.total_records
        batch_size = batch_size or config.generation.batch_size
        num_workers = num_workers or config.generation.num_workers
        
        logger.info(f"开始生成 {total_records:,} 条订单数据")
        logger.info(f"批次大小: {batch_size:,}, 并发进程数: {num_workers}")
        
        # 确保表存在
        db.ensure_table_exists()
        
        # 获取当前最大ID
        max_id = db.get_max_order_id()
        start_id = max_id + 1
        
        if max_id > 0:
            logger.info(f"检测到已有数据，最大ID: {max_id}，将从 {start_id} 开始生成")
        
        # 计算批次数量
        num_batches = (total_records + batch_size - 1) // batch_size
        remaining = total_records
        
        start_time = time.time()
        total_inserted = 0
        
        # 准备批次参数
        batch_args = []
        current_id = start_id
        for i in range(num_batches):
            current_batch_size = min(batch_size, remaining)
            batch_args.append((current_id, current_batch_size))
            current_id += current_batch_size
            remaining -= current_batch_size
        
        # 使用进程池并行生成
        logger.info(f"共 {num_batches} 个批次，开始并行生成...")
        
        with Pool(processes=num_workers) as pool:
            for i, batch_result in enumerate(pool.imap(generate_batch_worker, batch_args), 1):
                # 批量插入数据库
                inserted = db.batch_insert("orders", ORDER_COLUMNS, batch_result)
                total_inserted += inserted
                
                # 计算进度和速度
                elapsed = time.time() - start_time
                speed = total_inserted / elapsed if elapsed > 0 else 0
                progress = (i / num_batches) * 100
                
                logger.info(
                    f"进度: {progress:.1f}% ({i}/{num_batches}), "
                    f"已插入: {total_inserted:,}, "
                    f"速度: {speed:,.0f} 条/秒, "
                    f"耗时: {elapsed:.1f}秒"
                )
        
        total_time = time.time() - start_time
        avg_speed = total_inserted / total_time if total_time > 0 else 0
        
        logger.info("=" * 60)
        logger.info(f"数据生成完成!")
        logger.info(f"总记录数: {total_inserted:,}")
        logger.info(f"总耗时: {total_time:.2f} 秒")
        logger.info(f"平均速度: {avg_speed:,.0f} 条/秒")
        logger.info("=" * 60)
    
    def generate_incremental_data(
        self,
        start_date: str,
        end_date: str,
        count: int,
        batch_size: int = None,
        num_workers: int = None
    ) -> None:
        """
        增量生成指定时间范围内的数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            count: 生成数量
            batch_size: 批次大小
            num_workers: 并发工作进程数
        """
        batch_size = batch_size or config.generation.batch_size
        num_workers = num_workers or config.generation.num_workers
        
        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        
        logger.info(f"开始增量生成数据")
        logger.info(f"时间范围: {start_date} ~ {end_date}")
        logger.info(f"生成数量: {count:,}")
        
        # 确保表存在
        db.ensure_table_exists()
        
        # 获取当前最大ID
        max_id = db.get_max_order_id()
        start_id = max_id + 1
        
        start_time = time.time()
        total_inserted = 0
        remaining = count
        
        while remaining > 0:
            current_batch_size = min(batch_size, remaining)
            
            # 生成数据
            orders = self.generator.generate_orders_for_time_range(
                start_dt, end_dt, current_batch_size
            )
            
            # 转换并插入
            values = [self.converter.to_tuple(order) for order in orders]
            inserted = db.batch_insert("orders", ORDER_COLUMNS, values)
            total_inserted += inserted
            remaining -= current_batch_size
            
            # 更新起始ID
            start_id += current_batch_size
            
            # 计算进度
            elapsed = time.time() - start_time
            speed = total_inserted / elapsed if elapsed > 0 else 0
            progress = ((count - remaining) / count) * 100
            
            logger.info(
                f"进度: {progress:.1f}%, "
                f"已插入: {total_inserted:,}, "
                f"速度: {speed:,.0f} 条/秒"
            )
        
        total_time = time.time() - start_time
        avg_speed = total_inserted / total_time if total_time > 0 else 0
        
        logger.info("=" * 60)
        logger.info(f"增量数据生成完成!")
        logger.info(f"总记录数: {total_inserted:,}")
        logger.info(f"总耗时: {total_time:.2f} 秒")
        logger.info(f"平均速度: {avg_speed:,.0f} 条/秒")
        logger.info("=" * 60)
    
    def clear_data(self, confirm: bool = False) -> None:
        """
        清理所有数据
        
        Args:
            confirm: 是否确认清理
        """
        if not confirm:
            response = input("确认要清空 orders 表的所有数据吗？(yes/no): ")
            if response.lower() != 'yes':
                logger.info("操作已取消")
                return
        
        logger.info("开始清理数据...")
        start_time = time.time()
        
        # 获取当前记录数
        count = db.get_table_count("orders")
        logger.info(f"当前记录数: {count:,}")
        
        # 清空表
        db.truncate_table("orders")
        
        elapsed = time.time() - start_time
        logger.info(f"数据清理完成，耗时: {elapsed:.2f} 秒")
    
    def show_statistics(self) -> None:
        """显示数据统计信息"""
        if not db.table_exists("orders"):
            logger.info("orders 表不存在")
            return
        
        # 总记录数
        total_count = db.get_table_count("orders")
        logger.info(f"总记录数: {total_count:,}")
        
        if total_count == 0:
            return
        
        # 按状态统计
        status_query = """
            SELECT order_status, COUNT(*) as count 
            FROM orders 
            GROUP BY order_status 
            ORDER BY count DESC;
        """
        status_results = db.fetchall(status_query)
        logger.info("\n按状态统计:")
        for status, count in status_results:
            percentage = (count / total_count) * 100
            logger.info(f"  {status}: {count:,} ({percentage:.2f}%)")
        
        # 按年份统计
        year_query = """
            SELECT EXTRACT(YEAR FROM created_at) as year, COUNT(*) as count 
            FROM orders 
            GROUP BY year 
            ORDER BY year;
        """
        year_results = db.fetchall(year_query)
        logger.info("\n按年份统计:")
        for year, count in year_results:
            percentage = (count / total_count) * 100
            logger.info(f"  {int(year)}年: {count:,} ({percentage:.2f}%)")
        
        # 时间范围
        time_query = """
            SELECT MIN(created_at), MAX(created_at) FROM orders;
        """
        min_time, max_time = db.fetchone(time_query)
        logger.info(f"\n时间范围: {min_time} ~ {max_time}")
        
        # 金额统计
        amount_query = """
            SELECT 
                COUNT(*) as total,
                SUM(total_amount) as sum_total,
                AVG(total_amount) as avg_total,
                MIN(total_amount) as min_total,
                MAX(total_amount) as max_total
            FROM orders;
        """
        result = db.fetchone(amount_query)
        if result:
            logger.info(f"\n金额统计:")
            logger.info(f"  总金额: {result[1]:,.2f}")
            logger.info(f"  平均金额: {result[2]:,.2f}")
            logger.info(f"  最小金额: {result[3]:,.2f}")
            logger.info(f"  最大金额: {result[4]:,.2f}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="订单数据生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成 2000 万条数据
  python main.py generate --total 20000000
  
  # 生成 100 万条数据，使用 8 个进程
  python main.py generate --total 1000000 --workers 8
  
  # 增量生成 2024 年 1 月的数据
  python main.py incremental --start 2024-01-01 --end 2024-01-31 --count 100000
  
  # 显示数据统计
  python main.py stats
  
  # 清空数据
  python main.py clear
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成全量数据")
    gen_parser.add_argument(
        "--total", "-t", 
        type=int, 
        default=config.generation.total_records,
        help=f"总记录数 (默认: {config.generation.total_records:,})"
    )
    gen_parser.add_argument(
        "--batch", "-b", 
        type=int, 
        default=config.generation.batch_size,
        help=f"批次大小 (默认: {config.generation.batch_size:,})"
    )
    gen_parser.add_argument(
        "--workers", "-w", 
        type=int, 
        default=config.generation.num_workers,
        help=f"并发进程数 (默认: {config.generation.num_workers})"
    )
    
    # incremental 命令
    inc_parser = subparsers.add_parser("incremental", help="增量生成数据")
    inc_parser.add_argument(
        "--start", "-s", 
        required=True,
        help="开始日期 (YYYY-MM-DD)"
    )
    inc_parser.add_argument(
        "--end", "-e", 
        required=True,
        help="结束日期 (YYYY-MM-DD)"
    )
    inc_parser.add_argument(
        "--count", "-c", 
        type=int, 
        required=True,
        help="生成数量"
    )
    inc_parser.add_argument(
        "--batch", "-b", 
        type=int, 
        default=config.generation.batch_size,
        help=f"批次大小 (默认: {config.generation.batch_size:,})"
    )
    inc_parser.add_argument(
        "--workers", "-w", 
        type=int, 
        default=config.generation.num_workers,
        help=f"并发进程数 (默认: {config.generation.num_workers})"
    )
    
    # stats 命令
    subparsers.add_parser("stats", help="显示数据统计")
    
    # clear 命令
    clear_parser = subparsers.add_parser("clear", help="清空数据")
    clear_parser.add_argument(
        "--yes", "-y", 
        action="store_true",
        help="跳过确认"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = DataGenerationManager()
    
    try:
        if args.command == "generate":
            manager.generate_full_data(
                total_records=args.total,
                batch_size=args.batch,
                num_workers=args.workers
            )
        elif args.command == "incremental":
            manager.generate_incremental_data(
                start_date=args.start,
                end_date=args.end,
                count=args.count,
                batch_size=args.batch,
                num_workers=args.workers
            )
        elif args.command == "stats":
            manager.show_statistics()
        elif args.command == "clear":
            manager.clear_data(confirm=args.yes)
    except Exception as e:
        logger.error(f"执行失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
