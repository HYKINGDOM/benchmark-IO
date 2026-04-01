import request from '@/utils/request'

/**
 * 同步导出
 * @param {Object} data - 导出参数
 * @param {string} data.format - 导出格式 (csv/excel)
 * @param {string} data.start_time - 开始时间
 * @param {string} data.end_time - 结束时间
 * @param {string} data.status - 订单状态
 * @param {number} data.min_amount - 最小金额
 * @param {number} data.max_amount - 最大金额
 * @param {string} data.user_id - 用户ID
 * @param {number} data.limit - 数据量限制
 */
export function syncExport(data) {
  return request({
    url: '/exports/sync',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

/**
 * 异步导出
 * @param {Object} data - 导出参数
 */
export function asyncExport(data) {
  return request({
    url: '/exports/async',
    method: 'post',
    data
  })
}

/**
 * 流式导出
 * @param {Object} data - 导出参数
 */
export function streamExport(data) {
  return request({
    url: '/exports/stream',
    method: 'post',
    data
  })
}

/**
 * 查询任务状态
 * @param {string} taskId - 任务ID
 */
export function getTaskStatus(taskId) {
  return request({
    url: `/exports/tasks/${taskId}`,
    method: 'get'
  })
}

/**
 * 下载文件
 * @param {string} token - 下载令牌
 */
export function downloadFile(token) {
  return request({
    url: `/exports/download/${token}`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * SSE 进度推送 URL
 * @param {string} taskId - 任务ID
 */
export function getSSEUrl(taskId) {
  return `/api/v1/exports/sse/${taskId}`
}
