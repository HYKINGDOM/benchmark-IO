"""
订单数据生成器
实现符合字段规则的数据生成逻辑
"""
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from config import config


@dataclass
class OrderData:
    """订单数据结构"""
    order_no: str
    user_id: int
    user_name: str
    user_phone: str
    user_id_card: str
    user_email: str
    user_address: str
    product_id: int
    product_name: str
    product_category: str
    product_price: float
    quantity: int
    total_amount: float
    discount_amount: float
    pay_amount: float
    order_status: str
    payment_method: Optional[str]
    payment_time: Optional[datetime]
    order_source: str
    shipping_address: Optional[str]
    receiver_name: Optional[str]
    receiver_phone: Optional[str]
    logistics_no: Optional[str]
    delivery_time: Optional[datetime]
    complete_time: Optional[datetime]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_deleted: int = 0


class DataGenerator:
    """数据生成器"""
    
    # 身份证校验码权重
    ID_CARD_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    ID_CARD_CHECK_CODES = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    # 省份代码（身份证前两位）
    PROVINCE_CODES = {
        '北京市': '11', '天津市': '12', '河北省': '13', '山西省': '14', 
        '内蒙古自治区': '15', '辽宁省': '21', '吉林省': '22', '黑龙江省': '23',
        '上海市': '31', '江苏省': '32', '浙江省': '33', '安徽省': '34',
        '福建省': '35', '江西省': '36', '山东省': '37', '河南省': '41',
        '湖北省': '42', '湖南省': '43', '广东省': '44', '广西壮族自治区': '45',
        '海南省': '46', '重庆市': '50', '四川省': '51', '贵州省': '52',
        '云南省': '53', '西藏自治区': '54', '陕西省': '61', '甘肃省': '62',
        '青海省': '63', '宁夏回族自治区': '64', '新疆维吾尔自治区': '65',
    }
    
    def __init__(self):
        self._init_status_ranges()
        self._init_year_ranges()
    
    def _init_status_ranges(self) -> None:
        """初始化状态分布范围"""
        self._status_ranges: List[Tuple[str, float, float]] = []
        cumulative = 0.0
        for status, ratio in config.status_distribution.status_distribution.items():
            self._status_ranges.append((status, cumulative, cumulative + ratio))
            cumulative += ratio
    
    def _init_year_ranges(self) -> None:
        """初始化年份分布范围"""
        self._year_ranges: List[Tuple[int, float, float]] = []
        cumulative = 0.0
        for year, ratio in config.time_distribution.year_distribution.items():
            self._year_ranges.append((year, cumulative, cumulative + ratio))
            cumulative += ratio
    
    def generate_random_datetime(
        self, 
        year: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> datetime:
        """
        生成随机日期时间
        
        Args:
            year: 指定年份（如果提供）
            start_date: 开始日期（如果提供）
            end_date: 结束日期（如果提供）
            
        Returns:
            随机日期时间
        """
        if start_date and end_date:
            delta = end_date - start_date
            random_seconds = random.randint(0, int(delta.total_seconds()))
            return start_date + timedelta(seconds=random_seconds)
        
        if year:
            start = datetime(year, 1, 1, 0, 0, 0)
            end = datetime(year, 12, 31, 23, 59, 59)
            return self.generate_random_datetime(start_date=start, end_date=end)
        
        # 根据年份分布随机选择年份
        rand_val = random.random()
        selected_year = config.generation.end_year
        for year_val, start_ratio, end_ratio in self._year_ranges:
            if start_ratio <= rand_val < end_ratio:
                selected_year = year_val
                break
        
        return self.generate_random_datetime(year=selected_year)
    
    def generate_random_status(self) -> str:
        """根据分布生成随机订单状态"""
        rand_val = random.random()
        for status, start_ratio, end_ratio in self._status_ranges:
            if start_ratio <= rand_val < end_ratio:
                return status
        return "已支付"  # 默认返回
    
    def generate_chinese_name(self) -> str:
        """生成随机中文姓名（2-4个汉字）"""
        surname = random.choice(config.data_pool.surnames)
        
        # 70% 概率双字名，30% 概率单字名
        if random.random() < 0.7:
            if random.random() < 0.5:
                # 双字名（从双字名池选择）
                given_name = random.choice(config.data_pool.given_names_double)
            else:
                # 双字名（组合两个单字）
                given_name = random.choice(config.data_pool.given_names_single) + \
                            random.choice(config.data_pool.given_names_single)
        else:
            given_name = random.choice(config.data_pool.given_names_single)
        
        return surname + given_name
    
    def generate_phone_number(self) -> str:
        """生成符合规范的手机号"""
        prefix = random.choice(config.data_pool.phone_prefixes)
        suffix = ''.join(random.choices(string.digits, k=11 - len(prefix)))
        return prefix + suffix
    
    def generate_id_card(self, birth_date: Optional[datetime] = None) -> str:
        """
        生成符合格式的身份证号
        
        Args:
            birth_date: 出生日期（如果提供）
            
        Returns:
            18位身份证号
        """
        # 随机选择省份
        province = random.choice(list(self.PROVINCE_CODES.keys()))
        province_code = self.PROVINCE_CODES[province]
        
        # 随机城市和区县代码（4位）
        city_code = str(random.randint(1, 99)).zfill(2)
        district_code = str(random.randint(1, 99)).zfill(2)
        
        # 出生日期
        if birth_date:
            birth_str = birth_date.strftime('%Y%m%d')
        else:
            # 随机生成出生日期（18-70岁）
            age = random.randint(18, 70)
            birth_year = datetime.now().year - age
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birth_str = f"{birth_year}{birth_month:02d}{birth_day:02d}"
        
        # 顺序码（3位）
        sequence = str(random.randint(1, 999)).zfill(3)
        
        # 组合前17位
        id_17 = province_code + city_code + district_code + birth_str + sequence
        
        # 计算校验码
        check_sum = sum(int(id_17[i]) * self.ID_CARD_WEIGHTS[i] for i in range(17))
        check_code = self.ID_CARD_CHECK_CODES[check_sum % 11]
        
        return id_17 + check_code
    
    def generate_address(self) -> str:
        """生成随机省市区地址"""
        province = random.choice(config.data_pool.provinces)
        
        # 获取该省份的城市
        cities = config.data_pool.cities.get(province, ["市中心"])
        city = random.choice(cities)
        
        # 随机详细地址
        street_num = random.randint(1, 999)
        building = random.randint(1, 50)
        room = random.randint(101, 2599)
        
        return f"{province}{city}某某路{street_num}号{building}栋{room}室"
    
    def generate_product_name(self) -> Tuple[str, str]:
        """
        生成随机商品名称和分类
        
        Returns:
            (商品名称, 商品分类)
        """
        prefix = random.choice(config.data_pool.product_name_prefixes)
        body = random.choice(config.data_pool.product_name_bodies)
        spec = random.choice(config.data_pool.product_specs)
        category = random.choice(config.data_pool.product_categories)
        
        product_name = f"{prefix}{body} {spec}"
        return product_name, category
    
    def generate_logistics_no(self) -> str:
        """生成物流单号"""
        prefix = random.choice(config.data_pool.logistics_prefixes)
        numbers = ''.join(random.choices(string.digits, k=12))
        return prefix + numbers
    
    def generate_order_no(self, created_at: datetime) -> str:
        """
        生成订单编号
        
        格式: ORD + 时间戳 + 6位随机数
        """
        timestamp = int(created_at.timestamp())
        random_suffix = ''.join(random.choices(string.digits, k=6))
        return f"ORD{timestamp}{random_suffix}"
    
    def generate_order(self, order_id: int) -> OrderData:
        """
        生成单条订单数据
        
        Args:
            order_id: 订单ID（自增）
            
        Returns:
            订单数据
        """
        # 生成基础数据
        user_id = random.randint(
            config.generation.user_id_min, 
            config.generation.user_id_max
        )
        user_name = self.generate_chinese_name()
        user_phone = self.generate_phone_number()
        user_id_card = self.generate_id_card()
        user_email = f"user_{user_id}@example.com"
        user_address = self.generate_address()
        
        # 商品信息
        product_id = random.randint(
            config.generation.product_id_min,
            config.generation.product_id_max
        )
        product_name, product_category = self.generate_product_name()
        product_price = round(random.uniform(
            config.generation.product_price_min,
            config.generation.product_price_max
        ), 2)
        quantity = random.randint(
            config.generation.quantity_min,
            config.generation.quantity_max
        )
        
        # 金额计算
        total_amount = round(product_price * quantity, 2)
        max_discount = total_amount * config.generation.max_discount_ratio
        discount_amount = round(random.uniform(0, max_discount), 2)
        pay_amount = round(total_amount - discount_amount, 2)
        
        # 订单状态和来源
        order_status = self.generate_random_status()
        order_source = random.choice(config.data_pool.order_sources)
        
        # 时间相关
        created_at = self.generate_random_datetime()
        order_no = self.generate_order_no(created_at)
        
        # 根据状态设置支付、发货、完成时间
        payment_method = None
        payment_time = None
        shipping_address = None
        receiver_name = None
        receiver_phone = None
        logistics_no = None
        delivery_time = None
        complete_time = None
        
        if order_status in ["已支付", "已退款", "已完成"]:
            payment_method = random.choice(config.data_pool.payment_methods)
            # 支付时间在下单后1小时-7天内
            payment_delay = random.randint(60, 7 * 24 * 3600)
            payment_time = created_at + timedelta(seconds=payment_delay)
            
            if order_status in ["已完成"]:
                # 发货信息
                shipping_address = self.generate_address()
                receiver_name = self.generate_chinese_name()
                receiver_phone = self.generate_phone_number()
                logistics_no = self.generate_logistics_no()
                
                # 发货时间在支付后1-3天
                delivery_delay = random.randint(24 * 3600, 3 * 24 * 3600)
                delivery_time = payment_time + timedelta(seconds=delivery_delay)
                
                # 完成时间在发货后2-7天
                complete_delay = random.randint(2 * 24 * 3600, 7 * 24 * 3600)
                complete_time = delivery_time + timedelta(seconds=complete_delay)
        
        # 更新时间（在创建时间之后）
        updated_at = created_at + timedelta(
            seconds=random.randint(0, 7 * 24 * 3600)
        )
        
        # 备注
        remark = random.choice(config.data_pool.remarks) if random.random() < 0.2 else None
        
        return OrderData(
            order_no=order_no,
            user_id=user_id,
            user_name=user_name,
            user_phone=user_phone,
            user_id_card=user_id_card,
            user_email=user_email,
            user_address=user_address,
            product_id=product_id,
            product_name=product_name,
            product_category=product_category,
            product_price=product_price,
            quantity=quantity,
            total_amount=total_amount,
            discount_amount=discount_amount,
            pay_amount=pay_amount,
            order_status=order_status,
            payment_method=payment_method,
            payment_time=payment_time,
            order_source=order_source,
            shipping_address=shipping_address,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            logistics_no=logistics_no,
            delivery_time=delivery_time,
            complete_time=complete_time,
            remark=remark,
            created_at=created_at,
            updated_at=updated_at,
            is_deleted=0,
        )
    
    def generate_batch(self, start_id: int, count: int) -> List[OrderData]:
        """
        批量生成订单数据
        
        Args:
            start_id: 起始订单ID
            count: 生成数量
            
        Returns:
            订单数据列表
        """
        orders = []
        for i in range(count):
            order_id = start_id + i
            order = self.generate_order(order_id)
            orders.append(order)
        return orders
    
    def generate_orders_for_time_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        count: int
    ) -> List[OrderData]:
        """
        生成指定时间范围内的订单数据（增量生成）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            count: 生成数量
            
        Returns:
            订单数据列表
        """
        orders = []
        for i in range(count):
            order = self.generate_order(i)
            # 覆盖创建时间为指定范围内
            order.created_at = self.generate_random_datetime(
                start_date=start_date, 
                end_date=end_date
            )
            order.order_no = self.generate_order_no(order.created_at)
            orders.append(order)
        return orders


class OrderDataConverter:
    """订单数据转换器"""
    
    @staticmethod
    def to_tuple(order: OrderData) -> tuple:
        """转换为元组（用于批量插入）"""
        return (
            order.order_no,
            order.user_id,
            order.user_name,
            order.user_phone,
            order.user_id_card,
            order.user_email,
            order.user_address,
            order.product_id,
            order.product_name,
            order.product_category,
            order.product_price,
            order.quantity,
            order.total_amount,
            order.discount_amount,
            order.pay_amount,
            order.order_status,
            order.payment_method,
            order.payment_time,
            order.order_source,
            order.shipping_address,
            order.receiver_name,
            order.receiver_phone,
            order.logistics_no,
            order.delivery_time,
            order.complete_time,
            order.remark,
            order.created_at,
            order.updated_at,
            order.is_deleted,
        )
    
    @staticmethod
    def to_csv_row(order: OrderData) -> str:
        """转换为CSV行（用于COPY命令）"""
        def escape_csv(value: any) -> str:
            if value is None:
                return ''
            if isinstance(value, datetime):
                return value.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(value, str):
                # CSV 转义：包含逗号、引号、换行符时需要用引号包裹
                if ',' in value or '"' in value or '\n' in value:
                    return '"' + value.replace('"', '""') + '"'
                return value
            return str(value)
        
        values = [
            order.order_no,
            order.user_id,
            order.user_name,
            order.user_phone,
            order.user_id_card,
            order.user_email,
            order.user_address,
            order.product_id,
            order.product_name,
            order.product_category,
            order.product_price,
            order.quantity,
            order.total_amount,
            order.discount_amount,
            order.pay_amount,
            order.order_status,
            order.payment_method,
            order.payment_time,
            order.order_source,
            order.shipping_address,
            order.receiver_name,
            order.receiver_phone,
            order.logistics_no,
            order.delivery_time,
            order.complete_time,
            order.remark,
            order.created_at,
            order.updated_at,
            order.is_deleted,
        ]
        
        return ','.join(escape_csv(v) for v in values)
    
    @staticmethod
    def to_csv(orders: List[OrderData]) -> str:
        """转换为CSV格式字符串"""
        rows = [OrderDataConverter.to_csv_row(order) for order in orders]
        return '\n'.join(rows)


# 列名列表（用于批量插入）
ORDER_COLUMNS = [
    'order_no', 'user_id', 'user_name', 'user_phone', 'user_id_card',
    'user_email', 'user_address', 'product_id', 'product_name', 'product_category',
    'product_price', 'quantity', 'total_amount', 'discount_amount', 'pay_amount',
    'order_status', 'payment_method', 'payment_time', 'order_source',
    'shipping_address', 'receiver_name', 'receiver_phone', 'logistics_no',
    'delivery_time', 'complete_time', 'remark', 'created_at', 'updated_at', 'is_deleted',
]
