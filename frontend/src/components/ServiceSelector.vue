<template>
  <div class="service-selector">
    <span class="label">后端服务:</span>
    <el-radio-group v-model="selectedService" @change="handleServiceChange">
      <el-radio-button
        v-for="service in services"
        :key="service.value"
        :value="service.value"
      >
        <el-badge :value="service.port" type="info" class="service-badge">
          <span :style="{ color: service.color }">{{ service.name }}</span>
        </el-badge>
      </el-radio-button>
    </el-radio-group>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useServiceStore } from '@/stores/service'
import { storeToRefs } from 'pinia'

const serviceStore = useServiceStore()
const { services, currentService } = storeToRefs(serviceStore)

const selectedService = ref(currentService.value)

const handleServiceChange = (value) => {
  serviceStore.switchService(value)
}

onMounted(() => {
  serviceStore.restoreService()
  selectedService.value = currentService.value
})
</script>

<style scoped>
.service-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.service-badge {
  margin: 0 4px;
}
</style>
