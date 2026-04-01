import { createRouter, createWebHistory } from 'vue-router'
import Orders from '@/views/Orders.vue'
import Tasks from '@/views/Tasks.vue'

const routes = [
  {
    path: '/',
    redirect: '/orders'
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: {
      title: '数据查询与导出'
    }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks,
    meta: {
      title: '任务管理'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '数据导出性能基准测试系统'
  next()
})

export default router
