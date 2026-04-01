import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { orderApi } from '@/api'

export const useOrderStore = defineStore('order', () => {
  // 订单列表
  const orders = ref([])
  
  // 分页信息
  const pagination = ref({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0
  })
  
  // 查询条件
  const filters = ref({
    order_id: '',
    user_id: '',
    status: '',
    start_time: '',
    end_time: '',
    min_amount: null,
    max_amount: null
  })
  
  // 加载状态
  const loading = ref(false)
  
  // 订单状态选项
  const statusOptions = ref([
    { label: '全部', value: '' },
    { label: '待支付', value: 'pending' },
    { label: '已支付', value: 'paid' },
    { label: '已取消', value: 'cancelled' },
    { label: '已退款', value: 'refunded' },
    { label: '已完成', value: 'completed' }
  ])
  
  // 是否有筛选条件
  const hasFilters = computed(() => {
    return !!(
      filters.value.order_id ||
      filters.value.user_id ||
      filters.value.status ||
      filters.value.start_time ||
      filters.value.end_time ||
      filters.value.min_amount ||
      filters.value.max_amount
    )
  })
  
  // 查询订单
  async function fetchOrders() {
    loading.value = true
    try {
      const params = {
        page: pagination.value.page,
        page_size: pagination.value.page_size,
        ...filters.value
      }
      
      // 移除空值
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key]
        }
      })
      
      const response = await orderApi.queryOrders(params)
      
      if (response.data) {
        orders.value = response.data.data || []
        pagination.value = {
          page: response.data.page || 1,
          page_size: response.data.page_size || 20,
          total: response.data.total || 0,
          total_pages: response.data.total_pages || 0
        }
      }
    } catch (error) {
      console.error('Failed to fetch orders:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 更新分页
  function updatePagination(page, pageSize) {
    pagination.value.page = page
    if (pageSize) {
      pagination.value.page_size = pageSize
    }
    fetchOrders()
  }
  
  // 更新筛选条件
  function updateFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.page = 1 // 重置到第一页
  }
  
  // 重置筛选条件
  function resetFilters() {
    filters.value = {
      order_id: '',
      user_id: '',
      status: '',
      start_time: '',
      end_time: '',
      min_amount: null,
      max_amount: null
    }
    pagination.value.page = 1
  }
  
  return {
    orders,
    pagination,
    filters,
    loading,
    statusOptions,
    hasFilters,
    fetchOrders,
    updatePagination,
    updateFilters,
    resetFilters
  }
})
