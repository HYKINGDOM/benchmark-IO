"""
数据生成工具配置文件
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    database: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "benchmark"))
    user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "benchmark"))
    password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "benchmark123"))
    
    @property
    def connection_string(self) -> str:
        """获取数据库连接字符串"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_connection_string(self) -> str:
        """获取异步数据库连接字符串"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class DataGenerationConfig:
    """数据生成配置"""
    # 总数据量
    total_records: int = 20_000_000
    
    # 批次大小（每次插入的记录数）
    batch_size: int = 50_000
    
    # 并发工作进程数
    num_workers: int = 4
    
    # 用户ID范围
    user_id_min: int = 1
    user_id_max: int = 20_000_000
    
    # 商品ID范围
    product_id_min: int = 1
    product_id_max: int = 100_000
    
    # 商品价格范围
    product_price_min: float = 0.01
    product_price_max: float = 9999.99
    
    # 购买数量范围
    quantity_min: int = 1
    quantity_max: int = 99
    
    # 最大折扣比例
    max_discount_ratio: float = 0.3
    
    # 时间范围
    start_year: int = 2020
    end_year: int = 2024


@dataclass
class TimeDistributionConfig:
    """时间分布配置"""
    # 各年份占比
    year_distribution: Dict[int, float] = field(default_factory=lambda: {
        2020: 0.10,  # 10%
        2021: 0.15,  # 15%
        2022: 0.20,  # 20%
        2023: 0.25,  # 25%
        2024: 0.30,  # 30%
    })


@dataclass
class StatusDistributionConfig:
    """状态分布配置"""
    # 各状态占比
    status_distribution: Dict[str, float] = field(default_factory=lambda: {
        "待支付": 0.15,  # 15%
        "已支付": 0.50,  # 50%
        "已取消": 0.15,  # 15%
        "已退款": 0.05,  # 5%
        "已完成": 0.15,  # 15%
    })


@dataclass
class DataPoolConfig:
    """数据池配置"""
    # 姓氏池
    surnames: List[str] = field(default_factory=lambda: [
        "王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
        "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
        "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
        "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
        "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎",
    ])
    
    # 名字池（单字）
    given_names_single: List[str] = field(default_factory=lambda: [
        "伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
        "勇", "艳", "杰", "娟", "涛", "明", "超", "秀", "霞", "平",
        "刚", "桂", "英", "华", "建", "国", "文", "辉", "斌", "波",
        "萍", "宁", "飞", "红", "玲", "龙", "燕", "彬", "鑫", "慧",
    ])
    
    # 名字池（双字）
    given_names_double: List[str] = field(default_factory=lambda: [
        "志强", "秀英", "建国", "桂英", "文杰", "秀兰", "明华", "丽华",
        "国强", "秀芳", "建华", "桂芳", "文华", "丽娟", "国华", "秀珍",
        "建平", "桂珍", "文明", "丽萍", "国平", "秀芬", "建新", "桂芬",
        "文斌", "丽芳", "国明", "秀英", "建国", "桂芳", "建华", "秀华",
    ])
    
    # 手机号前缀
    phone_prefixes: List[str] = field(default_factory=lambda: [
        "130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
        "145", "147", "149",
        "150", "151", "152", "153", "155", "156", "157", "158", "159",
        "165", "166", "167",
        "170", "171", "172", "173", "175", "176", "177", "178",
        "180", "181", "182", "183", "184", "185", "186", "187", "188", "189",
        "191", "199",
    ])
    
    # 省份池
    provinces: List[str] = field(default_factory=lambda: [
        "北京市", "上海市", "天津市", "重庆市",
        "广东省", "浙江省", "江苏省", "山东省", "河南省", "四川省",
        "湖北省", "湖南省", "福建省", "安徽省", "河北省", "陕西省",
        "辽宁省", "江西省", "云南省", "广西壮族自治区", "山西省",
        "贵州省", "黑龙江省", "吉林省", "甘肃省", "内蒙古自治区",
        "新疆维吾尔自治区", "宁夏回族自治区", "海南省", "青海省",
        "西藏自治区",
    ])
    
    # 城市池（按省份分组）
    cities: Dict[str, List[str]] = field(default_factory=lambda: {
        "北京市": ["东城区", "西城区", "朝阳区", "海淀区", "丰台区", "石景山区", "通州区", "顺义区"],
        "上海市": ["黄浦区", "徐汇区", "长宁区", "静安区", "普陀区", "虹口区", "杨浦区", "浦东新区"],
        "广东省": ["广州市", "深圳市", "珠海市", "佛山市", "东莞市", "中山市", "惠州市", "江门市"],
        "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市", "湖州市", "绍兴市", "金华市", "台州市"],
        "江苏省": ["南京市", "苏州市", "无锡市", "常州市", "南通市", "扬州市", "镇江市", "徐州市"],
        "四川省": ["成都市", "绵阳市", "德阳市", "乐山市", "宜宾市", "泸州市", "南充市", "自贡市"],
        "湖北省": ["武汉市", "宜昌市", "襄阳市", "荆州市", "黄石市", "十堰市", "孝感市", "黄冈市"],
        "福建省": ["福州市", "厦门市", "泉州市", "漳州市", "莆田市", "宁德市", "龙岩市", "三明市"],
    })
    
    # 商品名称前缀
    product_name_prefixes: List[str] = field(default_factory=lambda: [
        "智能", "超薄", "便携", "高清", "无线", "蓝牙", "多功能", "迷你",
        "专业", "豪华", "经典", "时尚", "简约", "高端", "旗舰", "至尊",
    ])
    
    # 商品名称主体
    product_name_bodies: List[str] = field(default_factory=lambda: [
        "手机", "耳机", "音箱", "手表", "平板", "笔记本", "键盘", "鼠标",
        "显示器", "摄像头", "充电器", "数据线", "移动电源", "存储卡", "U盘",
        "路由器", "机顶盒", "投影仪", "打印机", "扫描仪", "电饭煲", "电磁炉",
        "微波炉", "烤箱", "榨汁机", "豆浆机", "吸尘器", "空气净化器", "加湿器",
        "电风扇", "空调", "冰箱", "洗衣机", "电视", "音响", "相机", "摄像机",
    ])
    
    # 商品规格
    product_specs: List[str] = field(default_factory=lambda: [
        "标准版", "升级版", "增强版", "旗舰版", "豪华版", "限量版",
        "64GB", "128GB", "256GB", "512GB", "1TB",
        "白色", "黑色", "银色", "金色", "蓝色", "红色", "绿色",
        "大号", "中号", "小号", "迷你", "加长", "加宽",
    ])
    
    # 商品分类
    product_categories: List[str] = field(default_factory=lambda: [
        "数码电子", "家用电器", "电脑办公", "服饰鞋包", "美妆个护",
        "食品饮料", "家居家装", "图书音像", "运动户外", "母婴玩具",
        "汽车用品", "珠宝首饰", "医药保健", "农资园艺", "宠物生活",
    ])
    
    # 支付方式
    payment_methods: List[str] = field(default_factory=lambda: [
        "支付宝", "微信", "银行卡", "其他",
    ])
    
    # 订单来源
    order_sources: List[str] = field(default_factory=lambda: [
        "APP", "小程序", "Web", "H5", "线下",
    ])
    
    # 物流公司前缀
    logistics_prefixes: List[str] = field(default_factory=lambda: [
        "SF", "YT", "YD", "ZT", "HT", "EMS", "JD", "YUN",
    ])
    
    # 备注池
    remarks: List[str] = field(default_factory=lambda: [
        "", "", "", "", "",  # 大部分为空
        "请尽快发货", "送人的，包装好一点", "希望能准时送达",
        "不要打电话，放快递柜", "周末送货", "工作日送货",
        "易碎物品，轻拿轻放", "生日礼物，请附贺卡", "谢谢",
        "加急处理", "送前电话联系", "放在门口即可",
    ])


@dataclass
class Config:
    """主配置类"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    generation: DataGenerationConfig = field(default_factory=DataGenerationConfig)
    time_distribution: TimeDistributionConfig = field(default_factory=TimeDistributionConfig)
    status_distribution: StatusDistributionConfig = field(default_factory=StatusDistributionConfig)
    data_pool: DataPoolConfig = field(default_factory=DataPoolConfig)


# 全局配置实例
config = Config()
