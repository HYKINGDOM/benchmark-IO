<template>
  <div class="task-progress">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>任务进度</span>
          <el-button
            type="primary"
            link
            @click="handleClearCompleted"
            :disabled="completedTasks.length === 0"
          >
            清除已完成
          </el-button>
        </div>
      </template>
      
      <div v-if="tasks.length === 0" class="empty">
        <el-empty description="暂无导出任务" />
      </div>
      
      <div v-else class="task-list">
        <div
          v-for="task in tasks"
          :key="task.task_id"
          class="task-item"
        >
          <div class="task-header">
            <div class="task-info">
              <span class="task-id">{{ task.task_id }}</span>
              <el-tag :type="getStatusType(task.status)" size="small">
                {{ getStatusLabel(task.status) }}
              </el-tag>
              <span class="task-type">{{ getExportTypeLabel(task.export_type) }}</span>
            </div>
            <div class="task-actions">
              <el-button
                v-if="task.status === 'completed'"
                type="primary"
                size="small"
                @click="handleDownload(task)"
              >
                下载
              </el-button>
              <el-button
                v-if="task.status === 'processing' || task.status === 'pending'"
                size="small"
                @click="handleRefresh(task.task_id)"
              >
                刷新
              </el-button>
              <el-button
                v-if="task.status === 'completed' || task.status === 'failed'"
                type="danger"
                size="small"
                @click="handleRemove(task.task_id)"
              >
                删除
              </el-button>
            </div>
          </div>
          
          <div class="task-body">
            <div class="task-meta">
              <span>格式: {{ task.format?.toUpperCase() }}</span>
              <span v-if="task.limit">数据量: {{ formatNumber(task.limit) }}</span>
              <span v-if="task.total">总数: {{ formatNumber(task.total) }}</span>
            </div>
            
            <el-progress
              v-if="task.status === 'processing'"
              :percentage="getProgress(task)"
              :status="task.status === 'failed' ? 'exception' : undefined"
              :stroke-width="20"
              :text-inside="true"
            />
            
            <div v-if="task.error" class="task-error">
              <el-alert type="error" :closable="false">
                {{ task.error }}
              </el-alert>
            </div>
            
            <div class="task-time">
              <span>创建时间: {{ formatTime(task.created_at) }}</span>
              <span v-if="task.updated_at">
                更新时间: {{ formatTime(task.updated_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useExportStore } from '@/stores/export'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'

const exportStore = useExportStore()
const { tasks, activeTasks, completedTasks } = storeToRefs(exportStore)

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labels = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return labels[status] || status
}

// 获取导出类型标签
const getExportTypeLabel = (type) => {
  const labels = {
    sync: '同步导出',
    async: '异步导出',
    stream: '流式导出'
  }
  return labels[type] || type
}

// 获取进度
const getProgress = (task) => {
  if (!task.total || task.total === 0) return 0
  return Math.round((task.progress / task.total) * 100)
}

// 格式化数字
const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000000) {
    return (num / 10000000).toFixed(1) + '千万'
  }
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

// 下载文件
const handleDownload = async (task) => {
  try {
    const filename = `orders_${task.task_id}.${task.format === 'csv' ? 'csv' : 'xlsx'}`
    await exportStore.downloadFile(task.download_token, filename)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('Download failed:', error)
    ElMessage.error('下载失败')
  }
}

// 刷新任务状态
const handleRefresh = async (taskId) => {
  try {
    await exportStore.fetchTaskStatus(taskId)
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('Refresh failed:', error)
    ElMessage.error('刷新失败')
  }
}

// 删除任务
const handleRemove = (taskId) => {
  exportStore.removeTask(taskId)
  ElMessage.success('删除成功')
}

// 清除已完成任务
const handleClearCompleted = () => {
  exportStore.clearCompletedTasks()
  ElMessage.success('清除成功')
}

onMounted(() => {
  exportStore.loadTasks()
})
</script>

<style scoped>
.task-progress {
  margin-top: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty {
  padding: 40px 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  padding: 16px;
  background-color: #FAFAFA;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-id {
  font-family: monospace;
  font-size: 14px;
  color: #606266;
}

.task-type {
  font-size: 12px;
  color: #909399;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.task-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.task-error {
  margin-top: 8px;
}

.task-time {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #C0C4CC;
}
</style>
