-- =============================================================================
-- 数据库初始化脚本
-- 创建 orders 表及相关索引
-- =============================================================================

-- 设置客户端编码
SET client_encoding = 'UTF8';

-- 使用 benchmark 数据库
\connect benchmark

-- =============================================================================
-- 创建 orders 表
-- =============================================================================
DROP TABLE IF EXISTS orders CASCADE;

CREATE TABLE orders (
    -- 主键
    order_id BIGSERIAL PRIMARY KEY,
    
    -- 订单基本信息
    order_no VARCHAR(32) NOT NULL,
    
    -- 用户信息
    user_id BIGINT NOT NULL,
    user_name VARCHAR(64),
    user_phone VARCHAR(11),
    user_id_card VARCHAR(18),
    user_email VARCHAR(128),
    user_address VARCHAR(256),
    
    -- 商品信息
    product_id BIGINT NOT NULL,
    product_name VARCHAR(128),
    product_category VARCHAR(64),
    product_price DECIMAL(10,2) NOT NULL,
    
    -- 数量和金额
    quantity INT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0.00,
    pay_amount DECIMAL(12,2) NOT NULL,
    
    -- 订单状态
    order_status VARCHAR(16) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(16),
    payment_time TIMESTAMP,
    
    -- 订单来源
    order_source VARCHAR(32),
    
    -- 物流信息
    shipping_address VARCHAR(512),
    receiver_name VARCHAR(64),
    receiver_phone VARCHAR(11),
    logistics_no VARCHAR(32),
    delivery_time TIMESTAMP,
    
    -- 完成时间
    complete_time TIMESTAMP,
    
    -- 备注
    remark VARCHAR(512),
    
    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 软删除标记
    is_deleted SMALLINT NOT NULL DEFAULT 0
);

-- =============================================================================
-- 创建索引
-- =============================================================================

-- 唯一索引：订单号
CREATE UNIQUE INDEX uk_order_no ON orders(order_no);

-- BTree 索引：用户 ID
CREATE INDEX idx_user_id ON orders(user_id);

-- BTree 索引：创建时间
CREATE INDEX idx_created_at ON orders(created_at);

-- BTree 索引：订单状态
CREATE INDEX idx_order_status ON orders(order_status);

-- BTree 索引：订单总金额
CREATE INDEX idx_total_amount ON orders(total_amount);

-- 复合索引：用户 ID + 创建时间（常用查询组合）
CREATE INDEX idx_user_created ON orders(user_id, created_at);

-- 复合索引：订单状态 + 创建时间（常用查询组合）
CREATE INDEX idx_status_created ON orders(order_status, created_at);

-- =============================================================================
-- 添加表注释
-- =============================================================================
COMMENT ON TABLE orders IS '订单表';
COMMENT ON COLUMN orders.order_id IS '订单ID，主键，自增';
COMMENT ON COLUMN orders.order_no IS '订单号，唯一，格式：ORD + 时间戳 + 6位随机数';
COMMENT ON COLUMN orders.user_id IS '用户ID，范围：1 ~ 20000000';
COMMENT ON COLUMN orders.user_name IS '用户姓名';
COMMENT ON COLUMN orders.user_phone IS '用户手机号';
COMMENT ON COLUMN orders.user_id_card IS '用户身份证号';
COMMENT ON COLUMN orders.user_email IS '用户邮箱';
COMMENT ON COLUMN orders.user_address IS '用户地址';
COMMENT ON COLUMN orders.product_id IS '商品ID';
COMMENT ON COLUMN orders.product_name IS '商品名称';
COMMENT ON COLUMN orders.product_category IS '商品分类';
COMMENT ON COLUMN orders.product_price IS '商品单价';
COMMENT ON COLUMN orders.quantity IS '购买数量';
COMMENT ON COLUMN orders.total_amount IS '订单总金额';
COMMENT ON COLUMN orders.discount_amount IS '优惠金额';
COMMENT ON COLUMN orders.pay_amount IS '实付金额';
COMMENT ON COLUMN orders.order_status IS '订单状态：pending-待支付, paid-已支付, shipped-已发货, delivered-已送达, completed-已完成, cancelled-已取消';
COMMENT ON COLUMN orders.payment_method IS '支付方式：alipay-支付宝, wechat-微信, bank-银行卡';
COMMENT ON COLUMN orders.payment_time IS '支付时间';
COMMENT ON COLUMN orders.order_source IS '订单来源：web-网页, app-移动端, mini-小程序';
COMMENT ON COLUMN orders.shipping_address IS '收货地址';
COMMENT ON COLUMN orders.receiver_name IS '收货人姓名';
COMMENT ON COLUMN orders.receiver_phone IS '收货人电话';
COMMENT ON COLUMN orders.logistics_no IS '物流单号';
COMMENT ON COLUMN orders.delivery_time IS '发货时间';
COMMENT ON COLUMN orders.complete_time IS '完成时间';
COMMENT ON COLUMN orders.remark IS '订单备注';
COMMENT ON COLUMN orders.created_at IS '创建时间';
COMMENT ON COLUMN orders.updated_at IS '更新时间';
COMMENT ON COLUMN orders.is_deleted IS '软删除标记：0-未删除, 1-已删除';

-- =============================================================================
-- 创建更新时间触发器
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 创建常用查询视图（可选）
-- =============================================================================

-- 有效订单视图（未删除）
CREATE OR REPLACE VIEW v_active_orders AS
SELECT * FROM orders WHERE is_deleted = 0;

-- =============================================================================
-- 授权
-- =============================================================================
GRANT ALL PRIVILEGES ON TABLE orders TO benchmark;
GRANT USAGE, SELECT ON SEQUENCE orders_order_id_seq TO benchmark;

-- =============================================================================
-- 验证表结构
-- =============================================================================
\d orders

-- 显示索引
\di orders*

-- 完成提示
SELECT 'Database initialization completed successfully!' AS status;
