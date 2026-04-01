use bigdecimal::BigDecimal;
use chrono::NaiveDateTime;
use diesel::prelude::*;
use serde::{Deserialize, Serialize};

use crate::schema::orders;

/// 订单数据库模型
#[derive(Debug, Clone, Queryable, Selectable)]
#[diesel(table_name = orders)]
pub struct Order {
    pub order_id: i64,
    pub order_no: String,
    pub user_id: i64,
    pub user_name: String,
    pub user_phone: String,
    pub user_id_card: String,
    pub user_email: String,
    pub user_address: String,
    pub product_id: i64,
    pub product_name: String,
    pub product_category: String,
    pub product_price: BigDecimal,
    pub quantity: i32,
    pub total_amount: BigDecimal,
    pub discount_amount: BigDecimal,
    pub pay_amount: BigDecimal,
    pub order_status: String,
    pub payment_method: String,
    pub payment_time: Option<NaiveDateTime>,
    pub order_source: String,
    pub shipping_address: String,
    pub receiver_name: String,
    pub receiver_phone: String,
    pub logistics_no: Option<String>,
    pub delivery_time: Option<NaiveDateTime>,
    pub complete_time: Option<NaiveDateTime>,
    pub remark: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub is_deleted: i16,
}

/// 订单查询参数
#[derive(Debug, Deserialize)]
pub struct OrderQueryParams {
    pub page: Option<i64>,
    pub page_size: Option<i64>,
    pub start_time: Option<String>,
    pub end_time: Option<String>,
    pub order_status: Option<String>,
    pub min_amount: Option<f64>,
    pub max_amount: Option<f64>,
    pub user_id: Option<i64>,
    pub order_no: Option<String>,
}

impl Default for OrderQueryParams {
    fn default() -> Self {
        Self {
            page: Some(1),
            page_size: Some(20),
            start_time: None,
            end_time: None,
            order_status: None,
            min_amount: None,
            max_amount: None,
            user_id: None,
            order_no: None,
        }
    }
}

/// 订单列表响应
#[derive(Debug, Serialize)]
pub struct OrderListResponse {
    pub total: i64,
    pub page: i64,
    pub page_size: i64,
    pub total_pages: i64,
    pub orders: Vec<OrderResponse>,
}

/// 订单响应模型
#[derive(Debug, Serialize)]
pub struct OrderResponse {
    pub order_id: i64,
    pub order_no: String,
    pub user_id: i64,
    pub user_name: String,
    pub user_phone: String,
    pub user_id_card: String,
    pub user_email: String,
    pub user_address: String,
    pub product_id: i64,
    pub product_name: String,
    pub product_category: String,
    pub product_price: String,
    pub quantity: i32,
    pub total_amount: String,
    pub discount_amount: String,
    pub pay_amount: String,
    pub order_status: String,
    pub payment_method: String,
    pub payment_time: Option<String>,
    pub order_source: String,
    pub shipping_address: String,
    pub receiver_name: String,
    pub receiver_phone: String,
    pub logistics_no: Option<String>,
    pub delivery_time: Option<String>,
    pub complete_time: Option<String>,
    pub remark: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

impl From<Order> for OrderResponse {
    fn from(order: Order) -> Self {
        Self {
            order_id: order.order_id,
            order_no: order.order_no,
            user_id: order.user_id,
            user_name: order.user_name,
            user_phone: order.user_phone,
            user_id_card: order.user_id_card,
            user_email: order.user_email,
            user_address: order.user_address,
            product_id: order.product_id,
            product_name: order.product_name,
            product_category: order.product_category,
            product_price: order.product_price.to_string(),
            quantity: order.quantity,
            total_amount: order.total_amount.to_string(),
            discount_amount: order.discount_amount.to_string(),
            pay_amount: order.pay_amount.to_string(),
            order_status: order.order_status,
            payment_method: order.payment_method,
            payment_time: order.payment_time.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string()),
            order_source: order.order_source,
            shipping_address: order.shipping_address,
            receiver_name: order.receiver_name,
            receiver_phone: order.receiver_phone,
            logistics_no: order.logistics_no,
            delivery_time: order.delivery_time.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string()),
            complete_time: order.complete_time.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string()),
            remark: order.remark,
            created_at: order.created_at.format("%Y-%m-%d %H:%M:%S").to_string(),
            updated_at: order.updated_at.format("%Y-%m-%d %H:%M:%S").to_string(),
        }
    }
}
