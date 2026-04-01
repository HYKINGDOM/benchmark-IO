use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// 导出任务状态
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum TaskStatus {
    Pending,
    Processing,
    Completed,
    Failed,
}

impl std::fmt::Display for TaskStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TaskStatus::Pending => write!(f, "pending"),
            TaskStatus::Processing => write!(f, "processing"),
            TaskStatus::Completed => write!(f, "completed"),
            TaskStatus::Failed => write!(f, "failed"),
        }
    }
}

/// 导出任务
#[derive(Debug, Clone, Serialize)]
pub struct ExportTask {
    pub task_id: Uuid,
    pub status: TaskStatus,
    pub progress: u32,
    pub total: u32,
    pub format: String,
    pub created_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
    pub file_path: Option<String>,
    pub download_token: Option<String>,
    pub error_message: Option<String>,
}

impl ExportTask {
    pub fn new(format: String) -> Self {
        Self {
            task_id: Uuid::new_v4(),
            status: TaskStatus::Pending,
            progress: 0,
            total: 0,
            format,
            created_at: Utc::now(),
            completed_at: None,
            file_path: None,
            download_token: None,
            error_message: None,
        }
    }

    pub fn progress_percent(&self) -> f32 {
        if self.total == 0 {
            0.0
        } else {
            (self.progress as f32 / self.total as f32) * 100.0
        }
    }
}

/// 导出请求参数
#[derive(Debug, Deserialize)]
pub struct ExportRequest {
    pub format: Option<String>,
    pub start_time: Option<String>,
    pub end_time: Option<String>,
    pub order_status: Option<String>,
    pub min_amount: Option<f64>,
    pub max_amount: Option<f64>,
    pub user_id: Option<i64>,
    pub order_no: Option<String>,
}

impl Default for ExportRequest {
    fn default() -> Self {
        Self {
            format: Some("csv".to_string()),
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

/// 任务状态响应
#[derive(Debug, Serialize)]
pub struct TaskStatusResponse {
    pub task_id: Uuid,
    pub status: TaskStatus,
    pub progress: u32,
    pub total: u32,
    pub progress_percent: f32,
    pub download_url: Option<String>,
    pub error_message: Option<String>,
}

impl From<ExportTask> for TaskStatusResponse {
    fn from(task: ExportTask) -> Self {
        Self {
            task_id: task.task_id,
            status: task.status.clone(),
            progress: task.progress,
            total: task.total,
            progress_percent: task.progress_percent(),
            download_url: task.download_token.map(|token| {
                format!("/api/v1/exports/download/{}", token)
            }),
            error_message: task.error_message,
        }
    }
}

/// SSE 事件数据
#[derive(Debug, Serialize)]
pub struct SSEEventData {
    pub task_id: Uuid,
    pub status: TaskStatus,
    pub progress: u32,
    pub total: u32,
    pub progress_percent: f32,
    pub message: String,
}
