import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useServiceStore = defineStore('service', () => {
  // 服务列表
  const services = ref([
    { name: 'Java', value: 'java', port: 8080, color: '#f89820' },
    { name: 'Golang', value: 'golang', port: 8081, color: '#00ADD8' },
    { name: 'Python', value: 'python', port: 8082, color: '#3776AB' },
    { name: 'Rust', value: 'rust', port: 8083, color: '#DEA584' }
  ])
  
  // 当前选中的服务
  const currentService = ref(import.meta.env.VITE_DEFAULT_SERVICE || 'java')
  
  // 当前服务信息
  const currentServiceInfo = computed(() => {
    return services.value.find(s => s.value === currentService.value) || services.value[0]
  })
  
  // API 基础 URL
  const apiBaseUrl = computed(() => {
    const serviceUrls = {
      java: import.meta.env.VITE_JAVA_API_URL || 'http://java:8080',
      golang: import.meta.env.VITE_GOLANG_API_URL || 'http://golang:8081',
      python: import.meta.env.VITE_PYTHON_API_URL || 'http://python:8082',
      rust: import.meta.env.VITE_RUST_API_URL || 'http://rust:8083'
    }
    return serviceUrls[currentService.value] || serviceUrls.java
  })
  
  // 切换服务
  function switchService(serviceName) {
    if (services.value.find(s => s.value === serviceName)) {
      currentService.value = serviceName
      // 保存到 localStorage
      localStorage.setItem('currentService', serviceName)
    }
  }
  
  // 从 localStorage 恢复服务选择
  function restoreService() {
    const saved = localStorage.getItem('currentService')
    if (saved && services.value.find(s => s.value === saved)) {
      currentService.value = saved
    }
  }
  
  return {
    services,
    currentService,
    currentServiceInfo,
    apiBaseUrl,
    switchService,
    restoreService
  }
})
