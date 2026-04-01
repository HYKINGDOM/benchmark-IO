import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { exportApi } from '@/api'
import { SSEClient } from '@/utils/sse'

export const useExportStore = defineStore('export', () => {
  // 导出任务列表
  const tasks = ref([])
  
  // 当前任务
  const currentTask = ref(null)
  
  // SSE 客户端实例
  const sseClient = ref(null)
  
  // 导出格式选项
  const formatOptions = ref([
    { label: 'CSV', value: 'csv' },
    { label: 'Excel (xlsx)', value: 'excel' }
  ])
  
  // 导出方式选项
  const exportTypeOptions = ref([
    { label: '同步导出', value: 'sync' },
    { label: '异步导出', value: 'async' },
    { label: '流式导出', value: 'stream' }
  ])
  
  // 数据量选项
  const limitOptions = ref([
    { label: '100万', value: 1000000 },
    { label: '200万', value: 2000000 },
    { label: '500万', value: 5000000 },
    { label: '1000万', value: 10000000 },
    { label: '2000万', value: 20000000 }
  ])
  
  // 任务状态选项
  const taskStatusOptions = ref([
    { label: '全部', value: '' },
    { label: '待处理', value: 'pending' },
    { label: '处理中', value: 'processing' },
    { label: '已完成', value: 'completed' },
    { label: '失败', value: 'failed' }
  ])
  
  // 正在进行的任务
  const activeTasks = computed(() => {
    return tasks.value.filter(t => t.status === 'processing' || t.status === 'pending')
  })
  
  // 已完成的任务
  const completedTasks = computed(() => {
    return tasks.value.filter(t => t.status === 'completed' || t.status === 'failed')
  })
  
  /**
   * 同步导出
   */
  async function syncExport(params) {
    try {
      const response = await exportApi.syncExport(params)
      
      // 创建下载链接
      const blob = new Blob([response.data], {
        type: params.format === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `orders_${Date.now()}.${params.format === 'csv' ? 'csv' : 'xlsx'}`
      link.click()
      window.URL.revokeObjectURL(url)
      
      return { success: true }
    } catch (error) {
      console.error('Sync export failed:', error)
      throw error
    }
  }
  
  /**
   * 异步导出
   */
  async function asyncExport(params) {
    try {
      const response = await exportApi.asyncExport(params)
      
      if (response.data && response.data.data) {
        const task = {
          task_id: response.data.data.task_id,
          status: 'pending',
          progress: 0,
          total: 0,
          created_at: new Date().toISOString(),
          ...params
        }
        
        // 添加到任务列表
        tasks.value.unshift(task)
        saveTasks()
        
        // 连接 SSE
        connectSSE(task.task_id)
        
        return task
      }
    } catch (error) {
      console.error('Async export failed:', error)
      throw error
    }
  }
  
  /**
   * 流式导出
   */
  async function streamExport(params) {
    try {
      // 流式导出使用 SSE 方式
      const response = await exportApi.streamExport(params)
      
      if (response.data && response.data.data) {
        const task = {
          task_id: response.data.data.task_id,
          status: 'processing',
          progress: 0,
          total: 0,
          created_at: new Date().toISOString(),
          export_type: 'stream',
          ...params
        }
        
        tasks.value.unshift(task)
        saveTasks()
        
        // 连接 SSE
        connectSSE(task.task_id)
        
        return task
      }
    } catch (error) {
      console.error('Stream export failed:', error)
      throw error
    }
  }
  
  /**
   * 连接 SSE
   */
  function connectSSE(taskId) {
    // 关闭之前的连接
    if (sseClient.value) {
      sseClient.value.close()
    }
    
    const url = exportApi.getSSEUrl(taskId)
    
    sseClient.value = new SSEClient(url, {
      onMessage: (data) => {
        updateTaskProgress(taskId, data)
      },
      onError: (error) => {
        console.error('SSE error:', error)
      }
    })
    
    sseClient.value.connect()
  }
  
  /**
   * 更新任务进度
   */
  function updateTaskProgress(taskId, data) {
    const taskIndex = tasks.value.findIndex(t => t.task_id === taskId)
    
    if (taskIndex !== -1) {
      tasks.value[taskIndex] = {
        ...tasks.value[taskIndex],
        ...data,
        updated_at: new Date().toISOString()
      }
      saveTasks()
      
      // 任务完成或失败时关闭 SSE
      if (data.status === 'completed' || data.status === 'failed') {
        if (sseClient.value) {
          sseClient.value.close()
        }
      }
    }
  }
  
  /**
   * 查询任务状态
   */
  async function fetchTaskStatus(taskId) {
    try {
      const response = await exportApi.getTaskStatus(taskId)
      
      if (response.data && response.data.data) {
        updateTaskProgress(taskId, response.data.data)
        return response.data.data
      }
    } catch (error) {
      console.error('Failed to fetch task status:', error)
      throw error
    }
  }
  
  /**
   * 下载文件
   */
  async function downloadFile(token, filename) {
    try {
      const response = await exportApi.downloadFile(token)
      
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename || `export_${Date.now()}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
      
      return { success: true }
    } catch (error) {
      console.error('Download failed:', error)
      throw error
    }
  }
  
  /**
   * 保存任务到 localStorage
   */
  function saveTasks() {
    localStorage.setItem('export_tasks', JSON.stringify(tasks.value))
  }
  
  /**
   * 从 localStorage 加载任务
   */
  function loadTasks() {
    const saved = localStorage.getItem('export_tasks')
    if (saved) {
      try {
        tasks.value = JSON.parse(saved)
        
        // 恢复进行中的任务
        const processingTask = tasks.value.find(t => t.status === 'processing' || t.status === 'pending')
        if (processingTask) {
          connectSSE(processingTask.task_id)
        }
      } catch (error) {
        console.error('Failed to load tasks:', error)
      }
    }
  }
  
  /**
   * 清除已完成的任务
   */
  function clearCompletedTasks() {
    tasks.value = tasks.value.filter(t => t.status !== 'completed' && t.status !== 'failed')
    saveTasks()
  }
  
  /**
   * 删除任务
   */
  function removeTask(taskId) {
    tasks.value = tasks.value.filter(t => t.task_id !== taskId)
    saveTasks()
  }
  
  return {
    tasks,
    currentTask,
    sseClient,
    formatOptions,
    exportTypeOptions,
    limitOptions,
    taskStatusOptions,
    activeTasks,
    completedTasks,
    syncExport,
    asyncExport,
    streamExport,
    connectSSE,
    updateTaskProgress,
    fetchTaskStatus,
    downloadFile,
    loadTasks,
    saveTasks,
    clearCompletedTasks,
    removeTask
  }
})
