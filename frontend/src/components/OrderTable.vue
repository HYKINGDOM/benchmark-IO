<template>
  <div class="order-table">
    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>筛选条件</span>
          <el-button
            type="primary"
            link
            @click="handleReset"
            :disabled="!hasFilters"
          >
            重置
          </el-button>
        </div>
      </template>
      
      <el-form :model="filterForm" label-width="100px" inline>
        <el-form-item label="订单编号">
          <el-input
            v-model="filterForm.order_id"
            placeholder="请输入订单编号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="用户ID">
          <el-input
            v-model="filterForm.user_id"
            placeholder="请输入用户ID"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="订单状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择订单状态"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="下单时间">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 360px"
          />
        </el-form-item>
        
        <el-form-item label="订单金额">
          <el-input-number
            v-model="filterForm.min_amount"
            :min="0"
            :precision="2"
            placeholder="最小金额"
            style="width: 120px"
          />
          <span style="margin: 0 8px">-</span>
          <el-input-number
            v-model="filterForm.max_amount"
            :min="0"
            :precision="2"
            placeholder="最大金额"
            style="width: 120px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        :data="orders"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
        max-height="600"
      >
        <el-table-column prop="order_id" label="订单编号" width="180" fixed />
        <el-table-column prop="user_id" label="用户ID" width="120" />
        <el-table-column prop="status" label="订单状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="订单金额" width="120">
          <template #default="{ row }">
            ¥{{ row.total_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_amount" label="支付金额" width="120">
          <template #default="{ row }">
            ¥{{ row.payment_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="discount_amount" label="优惠金额" width="100">
          <template #default="{ row }">
            ¥{{ row.discount_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" width="180" />
        <el-table-column prop="paid_at" label="支付时间" width="180" />
        <el-table-column prop="product_name" label="商品名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="region" label="地区" width="100" />
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useOrderStore } from '@/stores/order'
import { storeToRefs } from 'pinia'
import { Search } from '@element-plus/icons-vue'

const orderStore = useOrderStore()
const { orders, pagination, filters, loading, statusOptions, hasFilters } = storeToRefs(orderStore)

const filterForm = ref({
  order_id: '',
  user_id: '',
  status: '',
  min_amount: null,
  max_amount: null
})

const dateRange = ref([])

const currentPage = ref(1)
const pageSize = ref(20)

const total = computed(() => pagination.value.total)

// 监听日期范围变化
watch(dateRange, (val) => {
  if (val && val.length === 2) {
    filterForm.value.start_time = val[0]
    filterForm.value.end_time = val[1]
  } else {
    filterForm.value.start_time = ''
    filterForm.value.end_time = ''
  }
})

// 查询
const handleSearch = () => {
  orderStore.updateFilters(filterForm.value)
  currentPage.value = 1
  orderStore.fetchOrders()
}

// 重置
const handleReset = () => {
  filterForm.value = {
    order_id: '',
    user_id: '',
    status: '',
    min_amount: null,
    max_amount: null
  }
  dateRange.value = []
  orderStore.resetFilters()
  orderStore.fetchOrders()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pageSize.value = size
  orderStore.updatePagination(currentPage.value, size)
}

// 页码改变
const handlePageChange = (page) => {
  currentPage.value = page
  orderStore.updatePagination(page)
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    paid: 'success',
    cancelled: 'info',
    refunded: 'danger',
    completed: 'success'
  }
  return types[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const option = statusOptions.value.find(item => item.value === status)
  return option ? option.label : status
}

onMounted(() => {
  orderStore.fetchOrders()
})
</script>

<style scoped>
.order-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-card {
  flex: 1;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
