use bigdecimal::BigDecimal;
use chrono::NaiveDateTime;
use diesel::prelude::*;
use diesel::{BoolExpressionMethods, ExpressionMethods, QueryDsl, TextExpressionMethods};

use crate::db::DbConnection;
use crate::models::{Order, OrderListResponse, OrderQueryParams, OrderResponse};
use crate::schema::orders;

/// 订单服务
pub struct OrderService;

impl OrderService {
    /// 查询订单列表
    pub fn query_orders(
        conn: &mut DbConnection,
        params: OrderQueryParams,
    ) -> Result<OrderListResponse, String> {
        let page = params.page.unwrap_or(1).max(1);
        let page_size = params.page_size.unwrap_or(20).min(100).max(1);
        let offset = (page - 1) * page_size;

        // 构建基础查询
        let mut query = orders::table
            .filter(orders::is_deleted.eq(0))
            .into_boxed();

        // 时间范围筛选
        if let Some(start_time) = &params.start_time {
            if let Ok(dt) = NaiveDateTime::parse_from_str(start_time, "%Y-%m-%d %H:%M:%S") {
                query = query.filter(orders::created_at.ge(dt));
            } else if let Ok(dt) = NaiveDateTime::parse_from_str(
                &format!("{} 00:00:00", start_time),
                "%Y-%m-%d %H:%M:%S",
            ) {
                query = query.filter(orders::created_at.ge(dt));
            }
        }

        if let Some(end_time) = &params.end_time {
            if let Ok(dt) = NaiveDateTime::parse_from_str(end_time, "%Y-%m-%d %H:%M:%S") {
                query = query.filter(orders::created_at.le(dt));
            } else if let Ok(dt) = NaiveDateTime::parse_from_str(
                &format!("{} 23:59:59", end_time),
                "%Y-%m-%d %H:%M:%S",
            ) {
                query = query.filter(orders::created_at.le(dt));
            }
        }

        // 订单状态筛选
        if let Some(status) = &params.order_status {
            query = query.filter(orders::order_status.eq(status));
        }

        // 金额范围筛选
        if let Some(min_amount) = params.min_amount {
            query = query.filter(orders::pay_amount.ge(BigDecimal::from(min_amount)));
        }

        if let Some(max_amount) = params.max_amount {
            query = query.filter(orders::pay_amount.le(BigDecimal::from(max_amount)));
        }

        // 用户ID筛选
        if let Some(user_id) = params.user_id {
            query = query.filter(orders::user_id.eq(user_id));
        }

        // 订单编号筛选
        if let Some(order_no) = &params.order_no {
            query = query.filter(orders::order_no.eq(order_no));
        }

        // 查询总数
        let total = query
            .count()
            .get_result(conn)
            .map_err(|e| format!("Failed to count orders: {}", e))?;

        // 查询分页数据
        let order_list = query
            .order(orders::created_at.desc())
            .offset(offset)
            .limit(page_size)
            .select(Order::as_select())
            .load(conn)
            .map_err(|e| format!("Failed to load orders: {}", e))?;

        let orders: Vec<OrderResponse> = order_list.into_iter().map(OrderResponse::from).collect();
        let total_pages = (total as f64 / page_size as f64).ceil() as i64;

        Ok(OrderListResponse {
            total,
            page,
            page_size,
            total_pages,
            orders,
        })
    }

    /// 查询订单总数（用于导出）
    pub fn count_orders(
        conn: &mut DbConnection,
        params: &OrderQueryParams,
    ) -> Result<i64, String> {
        let mut query = orders::table
            .filter(orders::is_deleted.eq(0))
            .into_boxed();

        // 时间范围筛选
        if let Some(start_time) = &params.start_time {
            if let Ok(dt) = NaiveDateTime::parse_from_str(start_time, "%Y-%m-%d %H:%M:%S") {
                query = query.filter(orders::created_at.ge(dt));
            } else if let Ok(dt) = NaiveDateTime::parse_from_str(
                &format!("{} 00:00:00", start_time),
                "%Y-%m-%d %H:%M:%S",
            ) {
                query = query.filter(orders::created_at.ge(dt));
            }
        }

        if let Some(end_time) = &params.end_time {
            if let Ok(dt) = NaiveDateTime::parse_from_str(end_time, "%Y-%m-%d %H:%M:%S") {
                query = query.filter(orders::created_at.le(dt));
            } else if let Ok(dt) = NaiveDateTime::parse_from_str(
                &format!("{} 23:59:59", end_time),
                "%Y-%m-%d %H:%M:%S",
            ) {
                query = query.filter(orders::created_at.le(dt));
            }
        }

        // 订单状态筛选
        if let Some(status) = &params.order_status {
            query = query.filter(orders::order_status.eq(status));
        }

        // 金额范围筛选
        if let Some(min_amount) = params.min_amount {
            query = query.filter(orders::pay_amount.ge(BigDecimal::from(min_amount)));
        }

        if let Some(max_amount) = params.max_amount {
            query = query.filter(orders::pay_amount.le(BigDecimal::from(max_amount)));
        }

        // 用户ID筛选
        if let Some(user_id) = params.user_id {
            query = query.filter(orders::user_id.eq(user_id));
        }

        // 订单编号筛选
        if let Some(order_no) = &params.order_no {
            query = query.filter(orders::order_no.eq(order_no));
        }

        query
            .count()
            .get_result(conn)
            .map_err(|e| format!("Failed to count orders: {}", e))
    }

    /// 分批查询订单（用于导出）
    pub fn query_orders_batch(
        conn: &mut DbConnection,
        params: &OrderQueryParams,
        offset: i64,
        limit: i64,
    ) -> Result<Vec<Order>, String> {
        let mut query = orders::table
            .filter(orders::is_deleted.eq(0))
            .into_boxed();

        // 时间范围筛选
        if let Some(start_time) = &params.start_time {
            if let Ok(dt) = NaiveDateTime::parse_from_str(start_time, "%Y-%m-%d %H:%M:%S") {
                query = query.filter(orders::created_at.ge(dt));
            } else if let Ok(dt) = NaiveDateTime::parse_from_str(
                &format!("{} 00:00:00", start_time),
                "%Y-%m-%d %H:%M:%S",
            ) {
                query = query.filter(orders::created_at.ge(dt));
            }
        }

        if let Some(end_time) = &params.end_time {
            if let Ok(dt) = NaiveDateTime::parse_from_str(end_time, "%Y-%m-%d %H:%M:%S") {
                query = query.filter(orders::created_at.le(dt));
            } else if let Ok(dt) = NaiveDateTime::parse_from_str(
                &format!("{} 23:59:59", end_time),
                "%Y-%m-%d %H:%M:%S",
            ) {
                query = query.filter(orders::created_at.le(dt));
            }
        }

        // 订单状态筛选
        if let Some(status) = &params.order_status {
            query = query.filter(orders::order_status.eq(status));
        }

        // 金额范围筛选
        if let Some(min_amount) = params.min_amount {
            query = query.filter(orders::pay_amount.ge(BigDecimal::from(min_amount)));
        }

        if let Some(max_amount) = params.max_amount {
            query = query.filter(orders::pay_amount.le(BigDecimal::from(max_amount)));
        }

        // 用户ID筛选
        if let Some(user_id) = params.user_id {
            query = query.filter(orders::user_id.eq(user_id));
        }

        // 订单编号筛选
        if let Some(order_no) = &params.order_no {
            query = query.filter(orders::order_no.eq(order_no));
        }

        query
            .order(orders::created_at.desc())
            .offset(offset)
            .limit(limit)
            .select(Order::as_select())
            .load(conn)
            .map_err(|e| format!("Failed to load orders batch: {}", e))
    }
}
