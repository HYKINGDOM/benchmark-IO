use std::sync::Arc;

use actix_web::{middleware, web, App, HttpServer};
use env_logger::Env;

mod config;
mod controllers;
mod db;
mod middleware;
mod models;
mod schema;
mod services;
mod utils;

use config::Config;
use controllers::{export, order};
use services::task::TaskManager;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // 初始化日志
    env_logger::init_from_env(Env::default().default_filter_or("info"));

    // 加载配置
    let config = Config::from_env();
    log::info!("Starting server at {}:{}", config.server_host, config.server_port);

    // 创建数据库连接池
    let pool = db::create_pool();
    log::info!("Database connection pool created");

    // 创建任务管理器
    let task_manager = Arc::new(TaskManager::new());

    // 创建导出目录
    std::fs::create_dir_all(&config.export_dir)
        .expect("Failed to create export directory");
    log::info!("Export directory created: {}", config.export_dir);

    // 包装配置
    let config_arc = Arc::new(config.clone());

    // 启动 HTTP 服务器
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .app_data(web::Data::new(config_arc.clone()))
            .app_data(web::Data::new(task_manager.clone()))
            .wrap(middleware::Logger::default())
            .wrap(
                actix_web::middleware::DefaultHeaders::new()
                    .add(("X-Content-Type-Options", "nosniff"))
                    .add(("X-Frame-Options", "DENY"))
                    .add(("X-XSS-Protection", "1; mode=block"))
            )
            .service(
                web::scope("/api/v1")
                    .route("/orders", web::get().to(order::query_orders))
                    .route("/exports/sync", web::post().to(export::export_sync))
                    .route("/exports/async", web::post().to(export::export_async))
                    .route("/exports/tasks/{task_id}", web::get().to(export::get_task_status))
                    .route("/exports/sse/{task_id}", web::get().to(export::export_sse))
                    .route("/exports/download/{token}", web::get().to(export::download_file))
                    .route("/exports/stream", web::post().to(export::export_stream))
            )
            .route("/health", web::get().to(|| async { "OK" }))
    })
    .bind(format!("{}:{}", config.server_host, config.server_port))?
    .workers(4)
    .run()
    .await
}
