use std::fs::{self, File};
use std::io::Write;
use std::path::PathBuf;
use std::sync::Arc;
use uuid::Uuid;

use crate::db::DbPool;
use crate::models::{ExportRequest, ExportTask, Order, OrderQueryParams, TaskStatus, SSEEventData};
use crate::services::order::OrderService;
use crate::services::task::TaskManager;
use crate::utils::csv::write_csv;
use crate::utils::excel::write_excel;

/// 导出服务
pub struct ExportService;

impl ExportService {
    /// 同步导出（直接返回文件）
    pub fn export_sync(
        pool: &DbPool,
        export_dir: &str,
        request: ExportRequest,
    ) -> Result<(PathBuf, String), String> {
        // 创建导出目录
        fs::create_dir_all(export_dir)
            .map_err(|e| format!("Failed to create export directory: {}", e))?;

        let mut conn = pool.get()
            .map_err(|e| format!("Failed to get database connection: {}", e))?;

        // 构建查询参数
        let params = OrderQueryParams {
            page: None,
            page_size: None,
            start_time: request.start_time,
            end_time: request.end_time,
            order_status: request.order_status,
            min_amount: request.min_amount,
            max_amount: request.max_amount,
            user_id: request.user_id,
            order_no: request.order_no,
        };

        // 查询所有订单
        let total = OrderService::count_orders(&mut conn, &params)?;
        let orders = OrderService::query_orders_batch(&mut conn, &params, 0, total)?;

        // 生成文件名
        let format = request.format.unwrap_or_else(|| "csv".to_string());
        let filename = format!(
            "export_{}.{}",
            chrono::Local::now().format("%Y%m%d_%H%M%S"),
            format
        );
        let filepath = PathBuf::from(export_dir).join(&filename);

        // 写入文件
        match format.as_str() {
            "csv" => write_csv(&filepath, &orders)?,
            "xlsx" | "excel" => write_excel(&filepath, &orders)?,
            _ => return Err(format!("Unsupported format: {}", format)),
        }

        Ok((filepath, format))
    }

    /// 异步导出（后台任务）
    pub fn export_async(
        pool: DbPool,
        export_dir: String,
        request: ExportRequest,
        task_manager: Arc<TaskManager>,
    ) -> ExportTask {
        let format = request.format.clone().unwrap_or_else(|| "csv".to_string());
        let task = task_manager.create_task(format.clone());

        let task_id = task.task_id;
        let task_manager_clone = task_manager.clone();

        // 启动后台任务
        tokio::spawn(async move {
            // 创建导出目录
            if let Err(e) = fs::create_dir_all(&export_dir) {
                let mut task = task_manager_clone.get_task(&task_id).unwrap();
                task.status = TaskStatus::Failed;
                task.error_message = Some(format!("Failed to create export directory: {}", e));
                task_manager_clone.update_task(&task);
                return;
            }

            // 获取数据库连接
            let mut conn = match pool.get() {
                Ok(c) => c,
                Err(e) => {
                    let mut task = task_manager_clone.get_task(&task_id).unwrap();
                    task.status = TaskStatus::Failed;
                    task.error_message = Some(format!("Failed to get database connection: {}", e));
                    task_manager_clone.update_task(&task);
                    return;
                }
            };

            // 构建查询参数
            let params = OrderQueryParams {
                page: None,
                page_size: None,
                start_time: request.start_time,
                end_time: request.end_time,
                order_status: request.order_status,
                min_amount: request.min_amount,
                max_amount: request.max_amount,
                user_id: request.user_id,
                order_no: request.order_no,
            };

            // 更新任务状态为处理中
            let mut task = task_manager_clone.get_task(&task_id).unwrap();
            task.status = TaskStatus::Processing;
            task_manager_clone.update_task(&task);

            // 查询总数
            let total = match OrderService::count_orders(&mut conn, &params) {
                Ok(t) => t as u32,
                Err(e) => {
                    task.status = TaskStatus::Failed;
                    task.error_message = Some(e);
                    task_manager_clone.update_task(&task);
                    return;
                }
            };

            task.total = total;
            task_manager_clone.update_task(&task);

            // 分批查询并写入文件
            let batch_size = 1000;
            let mut all_orders = Vec::new();

            for offset in (0..total as i64).step_by(batch_size as usize) {
                let orders = match OrderService::query_orders_batch(
                    &mut conn,
                    &params,
                    offset,
                    batch_size,
                ) {
                    Ok(o) => o,
                    Err(e) => {
                        task.status = TaskStatus::Failed;
                        task.error_message = Some(e);
                        task_manager_clone.update_task(&task);
                        return;
                    }
                };

                all_orders.extend(orders);
                task.progress = all_orders.len() as u32;
                task_manager_clone.update_task(&task);
            }

            // 生成文件
            let filename = format!(
                "export_{}.{}",
                chrono::Local::now().format("%Y%m%d_%H%M%S"),
                format
            );
            let filepath = PathBuf::from(&export_dir).join(&filename);

            let write_result = match format.as_str() {
                "csv" => write_csv(&filepath, &all_orders),
                "xlsx" | "excel" => write_excel(&filepath, &all_orders),
                _ => Err(format!("Unsupported format: {}", format)),
            };

            match write_result {
                Ok(_) => {
                    task.status = TaskStatus::Completed;
                    task.file_path = Some(filepath.to_string_lossy().to_string());
                    task.download_token = Some(Uuid::new_v4().to_string());
                    task.completed_at = Some(chrono::Utc::now());
                }
                Err(e) => {
                    task.status = TaskStatus::Failed;
                    task.error_message = Some(e);
                }
            }

            task_manager_clone.update_task(&task);
        });

        task
    }
}
