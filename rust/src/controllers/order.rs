use actix_web::{web, HttpResponse};
use serde_json::json;

use crate::db::DbPool;
use crate::middleware::auth::ApiKeyAuth;
use crate::models::OrderQueryParams;
use crate::services::order::OrderService;

/// GET /api/v1/orders - 订单查询
pub async fn query_orders(
    _auth: ApiKeyAuth,
    pool: web::Data<DbPool>,
    query: web::Query<OrderQueryParams>,
) -> HttpResponse {
    let mut conn = match pool.get() {
        Ok(conn) => conn,
        Err(e) => {
            return HttpResponse::InternalServerError().json(json!({
                "error": "Database error",
                "message": format!("Failed to get database connection: {}", e)
            }));
        }
    };

    match OrderService::query_orders(&mut conn, query.into_inner()) {
        Ok(response) => HttpResponse::Ok().json(response),
        Err(e) => HttpResponse::InternalServerError().json(json!({
            "error": "Query error",
            "message": e
        })),
    }
}
