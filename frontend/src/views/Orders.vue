<template>
  <div class="orders-view">
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="数据查询" name="query">
        <OrderTable />
      </el-tab-pane>
      
      <el-tab-pane label="数据导出" name="export">
        <ExportPanel ref="exportPanelRef" />
        <TaskProgress />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import OrderTable from '@/components/OrderTable.vue'
import ExportPanel from '@/components/ExportPanel.vue'
import TaskProgress from '@/components/TaskProgress.vue'

const activeTab = ref('query')
const exportPanelRef = ref(null)
</script>

<style scoped>
.orders-view {
  padding: 20px;
}
</style>
