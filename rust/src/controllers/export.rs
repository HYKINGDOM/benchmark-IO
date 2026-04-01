use std::sync::Arc;
use std::fs::File;
use std::io::Read;

use actix_web::{web, HttpRequest, HttpResponse};
use actix_web_lab::sse;
use futures::stream;
use serde_json::json;
use uuid::Uuid;

use crate::config::Config;
use crate::db::DbPool;
use crate::middleware::auth::ApiKeyAuth;
use crate::models::{ExportRequest, TaskStatusResponse};
use crate::services::export::ExportService;
use crate::services::task::TaskManager;

/// POST /api/v1/exports/sync - 同步导出
pub async fn export_sync(
    _auth: ApiKeyAuth,
    pool: web::Data<DbPool>,
    config: web::Data<Arc<Config>>,
    request: web::Json<ExportRequest>,
) -> HttpResponse {
    match ExportService::export_sync(&pool, &config.export_dir, request.into_inner()) {
        Ok((filepath, format)) => {
            // 读取文件内容
            let mut file = match File::open(&filepath) {
                Ok(f) => f,
                Err(e) => {
                    return HttpResponse::InternalServerError().json(json!({
                        "error": "File error",
                        "message": format!("Failed to open file: {}", e)
                    }));
                }
            };

            let mut buffer = Vec::new();
            if let Err(e) = file.read_to_end(&mut buffer) {
                return HttpResponse::InternalServerError().json(json!({
                    "error": "File error",
                    "message": format!("Failed to read file: {}", e)
                }));
            }

            // 设置响应头
            let content_type = match format.as_str() {
                "csv" => "text/csv",
                "xlsx" | "excel" => "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                _ => "application/octet-stream",
            };

            let filename = filepath.file_name().unwrap().to_string_lossy().to_string();

            HttpResponse::Ok()
                .content_type(content_type)
                .insert_header(("Content-Disposition", format!("attachment; filename=\"{}\"", filename)))
                .body(buffer)
        }
        Err(e) => {
            HttpResponse::InternalServerError().json(json!({
                "error": "Export error",
                "message": e
            }))
        }
    }
}

/// POST /api/v1/exports/async - 异步导出
pub async fn export_async(
    _auth: ApiKeyAuth,
    pool: web::Data<DbPool>,
    config: web::Data<Arc<Config>>,
    task_manager: web::Data<Arc<TaskManager>>,
    request: web::Json<ExportRequest>,
) -> HttpResponse {
    let task = ExportService::export_async(
        pool.into_inner(),
        config.export_dir.clone(),
        request.into_inner(),
        task_manager.into_inner(),
    );

    HttpResponse::Accepted().json(json!({
        "task_id": task.task_id,
        "status": task.status,
        "message": "Export task created successfully"
    }))
}

/// GET /api/v1/exports/tasks/{task_id} - 任务状态查询
pub async fn get_task_status(
    _auth: ApiKeyAuth,
    task_manager: web::Data<Arc<TaskManager>>,
    path: web::Path<Uuid>,
) -> HttpResponse {
    let task_id = path.into_inner();

    match task_manager.get_task(&task_id) {
        Some(task) => {
            let response: TaskStatusResponse = task.into();
            HttpResponse::Ok().json(response)
        }
        None => {
            HttpResponse::NotFound().json(json!({
                "error": "Not found",
                "message": "Task not found"
            }))
        }
    }
}

/// GET /api/v1/exports/sse/{task_id} - SSE 进度推送
pub async fn export_sse(
    _auth: ApiKeyAuth,
    task_manager: web::Data<Arc<TaskManager>>,
    path: web::Path<Uuid>,
) -> HttpResponse {
    let task_id = path.into_inner();

    // 创建 SSE 流
    let task_manager_clone = task_manager.into_inner();
    
    let stream = stream::repeat_with(move || {
        let task = task_manager_clone.get_task(&task_id);
        
        match task {
            Some(task) => {
                let data = json!({
                    "task_id": task.task_id,
                    "status": task.status,
                    "progress": task.progress,
                    "total": task.total,
                    "progress_percent": task.progress_percent(),
                    "message": format!("Processing {}/{}", task.progress, task.total)
                });

                let is_completed = task.status == crate::models::TaskStatus::Completed 
                    || task.status == crate::models::TaskStatus::Failed;

                (data.to_string(), is_completed)
            }
            None => {
                let data = json!({
                    "error": "Task not found"
                });
                (data.to_string(), true)
            }
        }
    })
    .take_while(|(_, is_completed)| futures::future::ready(!*is_completed))
    .map(|(data, _)| {
        Ok::<_, actix_web::Error>(sse::Event::Data(sse::Data::new(data)))
    })
    .throttle(std::time::Duration::from_millis(500));

    sse::Sse::new(stream)
        .with_keep_alive(std::time::Duration::from_secs(10))
        .into_response()
}

/// GET /api/v1/exports/download/{token} - 文件下载
pub async fn download_file(
    _auth: ApiKeyAuth,
    task_manager: web::Data<Arc<TaskManager>>,
    path: web::Path<String>,
) -> HttpResponse {
    let token = path.into_inner();

    // 通过 token 查找任务
    match task_manager.get_task_by_token(&token) {
        Some(task) => {
            if task.status != crate::models::TaskStatus::Completed {
                return HttpResponse::BadRequest().json(json!({
                    "error": "Task not completed",
                    "message": "The export task is not yet completed"
                }));
            }

            match task.file_path {
                Some(filepath) => {
                    // 读取文件
                    let mut file = match File::open(&filepath) {
                        Ok(f) => f,
                        Err(e) => {
                            return HttpResponse::InternalServerError().json(json!({
                                "error": "File error",
                                "message": format!("Failed to open file: {}", e)
                            }));
                        }
                    };

                    let mut buffer = Vec::new();
                    if let Err(e) = file.read_to_end(&mut buffer) {
                        return HttpResponse::InternalServerError().json(json!({
                            "error": "File error",
                            "message": format!("Failed to read file: {}", e)
                        }));
                    }

                    // 设置响应头
                    let content_type = match task.format.as_str() {
                        "csv" => "text/csv",
                        "xlsx" | "excel" => "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        _ => "application/octet-stream",
                    };

                    let filename = std::path::Path::new(&filepath)
                        .file_name()
                        .unwrap()
                        .to_string_lossy()
                        .to_string();

                    HttpResponse::Ok()
                        .content_type(content_type)
                        .insert_header(("Content-Disposition", format!("attachment; filename=\"{}\"", filename)))
                        .body(buffer)
                }
                None => {
                    HttpResponse::NotFound().json(json!({
                        "error": "File not found",
                        "message": "Export file not found"
                    }))
                }
            }
        }
        None => {
            HttpResponse::NotFound().json(json!({
                "error": "Invalid token",
                "message": "Download token not found or expired"
            }))
        }
    }
}

/// POST /api/v1/exports/stream - 流式导出
pub async fn export_stream(
    _auth: ApiKeyAuth,
    pool: web::Data<DbPool>,
    request: web::Json<ExportRequest>,
) -> HttpResponse {
    use actix_web::body::BoxBody;
    use bytes::Bytes;
    use futures::stream::{Stream, StreamExt};

    let pool_clone = pool.into_inner();
    let request_inner = request.into_inner();

    // 创建流
    let stream = async_stream::stream! {
        // 获取数据库连接
        let mut conn = match pool_clone.get() {
            Ok(c) => c,
            Err(e) => {
                yield Err(std::io::Error::new(
                    std::io::ErrorKind::Other,
                    format!("Failed to get database connection: {}", e)
                ));
                return;
            }
        };

        // 构建查询参数
        let params = crate::models::OrderQueryParams {
            page: None,
            page_size: None,
            start_time: request_inner.start_time.clone(),
            end_time: request_inner.end_time.clone(),
            order_status: request_inner.order_status.clone(),
            min_amount: request_inner.min_amount,
            max_amount: request_inner.max_amount,
            user_id: request_inner.user_id,
            order_no: request_inner.order_no.clone(),
        };

        // 查询总数
        let total = match crate::services::order::OrderService::count_orders(&mut conn, &params) {
            Ok(t) => t,
            Err(e) => {
                yield Err(std::io::Error::new(
                    std::io::ErrorKind::Other,
                    format!("Failed to count orders: {}", e)
                ));
                return;
            }
        };

        // 写入 CSV 表头
        let headers = "订单ID,订单编号,用户ID,用户姓名,用户手机,用户身份证,用户邮箱,用户地址,商品ID,商品名称,商品分类,商品单价,数量,订单总额,优惠金额,实付金额,订单状态,支付方式,支付时间,订单来源,收货地址,收货人,收货电话,物流单号,发货时间,完成时间,备注,创建时间,更新时间\n";
        yield Ok(Bytes::from(headers.as_bytes()));

        // 分批查询并流式输出
        let batch_size = 1000;
        for offset in (0..total).step_by(batch_size as usize) {
            let orders = match crate::services::order::OrderService::query_orders_batch(
                &mut conn,
                &params,
                offset,
                batch_size,
            ) {
                Ok(o) => o,
                Err(e) => {
                    yield Err(std::io::Error::new(
                        std::io::ErrorKind::Other,
                        format!("Failed to query orders: {}", e)
                    ));
                    return;
                }
            };

            for order in orders {
                let row = format!(
                    "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
                    order.order_id,
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
                    order.payment_time.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string()).unwrap_or_default(),
                    order.order_source,
                    order.shipping_address,
                    order.receiver_name,
                    order.receiver_phone,
                    order.logistics_no.unwrap_or_default(),
                    order.delivery_time.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string()).unwrap_or_default(),
                    order.complete_time.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string()).unwrap_or_default(),
                    order.remark.unwrap_or_default(),
                    order.created_at.format("%Y-%m-%d %H:%M:%S"),
                    order.updated_at.format("%Y-%m-%d %H:%M:%S")
                );
                yield Ok(Bytes::from(row.as_bytes()));
            }
        }
    };

    HttpResponse::Ok()
        .content_type("text/csv")
        .insert_header(("Content-Disposition", "attachment; filename=\"export.csv\""))
        .streaming(stream)
}
