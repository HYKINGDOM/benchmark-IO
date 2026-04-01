<template>
  <div class="export-panel">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>数据导出</span>
        </div>
      </template>
      
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="导出方式">
          <el-radio-group v-model="exportForm.export_type">
            <el-radio-button
              v-for="item in exportTypeOptions"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio-button
              v-for="item in formatOptions"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-divider content-position="left">导出条件</el-divider>
        
        <el-form-item label="数据量">
          <el-radio-group v-model="exportForm.limit">
            <el-radio-button
              v-for="item in limitOptions"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
          <span class="tip">（直接选择数据量导出）</span>
        </el-form-item>
        
        <el-divider>或使用筛选条件</el-divider>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 400px"
          />
        </el-form-item>
        
        <el-form-item label="订单状态">
          <el-select
            v-model="exportForm.status"
            placeholder="请选择订单状态"
            clearable
            style="width: 200px"
          >
            <el-option label="全部" value="" />
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已退款" value="refunded" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="金额范围">
          <el-input-number
            v-model="exportForm.min_amount"
            :min="0"
            :precision="2"
            placeholder="最小金额"
            style="width: 150px"
          />
          <span style="margin: 0 8px">-</span>
          <el-input-number
            v-model="exportForm.max_amount"
            :min="0"
            :precision="2"
            placeholder="最大金额"
            style="width: 150px"
          />
        </el-form-item>
        
        <el-form-item label="用户ID">
          <el-input
            v-model="exportForm.user_id"
            placeholder="请输入用户ID"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            @click="handleExport"
            :loading="exporting"
          >
            <el-icon><Download /></el-icon>
            开始导出
          </el-button>
          
          <el-button
            size="large"
            @click="handleReset"
          >
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useExportStore } from '@/stores/export'
import { useOrderStore } from '@/stores/order'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

const exportStore = useExportStore()
const orderStore = useOrderStore()
const { formatOptions, exportTypeOptions, limitOptions } = storeToRefs(exportStore)

const exportForm = ref({
  export_type: 'sync',
  format: 'csv',
  limit: 1000000,
  start_time: '',
  end_time: '',
  status: '',
  min_amount: null,
  max_amount: null,
  user_id: ''
})

const dateRange = ref([])
const exporting = ref(false)

// 监听日期范围变化
watch(dateRange, (val) => {
  if (val && val.length === 2) {
    exportForm.value.start_time = val[0]
    exportForm.value.end_time = val[1]
  } else {
    exportForm.value.start_time = ''
    exportForm.value.end_time = ''
  }
})

// 导出
const handleExport = async () => {
  exporting.value = true
  
  try {
    const params = { ...exportForm.value }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    switch (params.export_type) {
      case 'sync':
        await exportStore.syncExport(params)
        ElMessage.success('导出成功')
        break
        
      case 'async':
        const asyncTask = await exportStore.asyncExport(params)
        ElMessage.success(`异步导出任务已创建: ${asyncTask.task_id}`)
        break
        
      case 'stream':
        const streamTask = await exportStore.streamExport(params)
        ElMessage.success(`流式导出任务已创建: ${streamTask.task_id}`)
        break
    }
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 重置
const handleReset = () => {
  exportForm.value = {
    export_type: 'sync',
    format: 'csv',
    limit: 1000000,
    start_time: '',
    end_time: '',
    status: '',
    min_amount: null,
    max_amount: null,
    user_id: ''
  }
  dateRange.value = []
}

// 使用当前筛选条件
const useCurrentFilters = () => {
  const { filters } = storeToRefs(orderStore)
  exportForm.value = {
    ...exportForm.value,
    ...filters.value
  }
  
  if (filters.value.start_time && filters.value.end_time) {
    dateRange.value = [filters.value.start_time, filters.value.end_time]
  }
}

defineExpose({
  useCurrentFilters
})
</script>

<style scoped>
.export-panel {
  margin-top: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tip {
  margin-left: 12px;
  font-size: 12px;
  color: #909399;
}
</style>
