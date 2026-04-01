<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <h1>数据导出性能基准测试系统</h1>
          </div>
          
          <div class="header-right">
            <ServiceSelector />
          </div>
        </div>
      </el-header>
      
      <!-- 主内容 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
      
      <!-- 底部导航 -->
      <el-footer class="app-footer">
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/orders">
            <el-icon><Document /></el-icon>
            <span>数据查询与导出</span>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><List /></el-icon>
            <span>任务管理</span>
          </el-menu-item>
        </el-menu>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Document, List } from '@element-plus/icons-vue'
import ServiceSelector from '@/components/ServiceSelector.vue'

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

const handleMenuSelect = (index) => {
  router.push(index)
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f7fa;
}

#app {
  min-height: 100vh;
}

.el-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: auto !important;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.logo h1 {
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.app-main {
  flex: 1;
  padding: 0;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.app-footer {
  background-color: #fff;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: auto !important;
}

.app-footer .el-menu {
  border-bottom: none;
  display: flex;
  justify-content: center;
}
</style>
