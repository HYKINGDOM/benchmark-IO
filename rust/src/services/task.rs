use std::collections::HashMap;
use std::sync::Arc;
use uuid::Uuid;
use parking_lot::RwLock;

use crate::models::{ExportTask, TaskStatus};

/// 任务管理器
pub struct TaskManager {
    tasks: RwLock<HashMap<Uuid, ExportTask>>,
}

impl TaskManager {
    pub fn new() -> Self {
        Self {
            tasks: RwLock::new(HashMap::new()),
        }
    }

    /// 创建新任务
    pub fn create_task(&self, format: String) -> ExportTask {
        let task = ExportTask::new(format);
        let task_id = task.task_id;
        
        self.tasks.write().insert(task_id, task.clone());
        task
    }

    /// 获取任务
    pub fn get_task(&self, task_id: &Uuid) -> Option<ExportTask> {
        self.tasks.read().get(task_id).cloned()
    }

    /// 更新任务
    pub fn update_task(&self, task: &ExportTask) {
        self.tasks.write().insert(task.task_id, task.clone());
    }

    /// 删除任务
    pub fn remove_task(&self, task_id: &Uuid) {
        self.tasks.write().remove(task_id);
    }

    /// 通过下载令牌获取任务
    pub fn get_task_by_token(&self, token: &str) -> Option<ExportTask> {
        self.tasks
            .read()
            .values()
            .find(|task| {
                task.download_token.as_deref() == Some(token)
            })
            .cloned()
    }
}

impl Default for TaskManager {
    fn default() -> Self {
        Self::new()
    }
}
