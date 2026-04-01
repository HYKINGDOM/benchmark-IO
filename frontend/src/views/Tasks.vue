<template>
  <div class="tasks-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>任务管理</span>
          <el-button
            type="primary"
            @click="handleRefresh"
          >
            刷新
          </el-button>
        </div>
      </template>
      
      <TaskProgress />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import TaskProgress from '@/components/TaskProgress.vue'
import { useExportStore } from '@/stores/export'
import { ElMessage } from 'element-plus'

const exportStore = useExportStore()

const handleRefresh = async () => {
  try {
    // 刷新所有进行中的任务
    const { activeTasks } = exportStore
    for (const task of activeTasks) {
      await exportStore.fetchTaskStatus(task.task_id)
    }
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('Refresh failed:', error)
    ElMessage.error('刷新失败')
  }
}

onMounted(() => {
  exportStore.loadTasks()
})
</script>

<style scoped>
.tasks-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
