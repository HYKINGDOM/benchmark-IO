import request from '@/utils/request'

/**
 * 订单查询
 */
export function queryOrders(params) {
  return request({
    url: '/orders',
    method: 'get',
    params
  })
}

/**
 * 订单查询参数
 * @param {Object} params
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.order_id - 订单编号
 * @param {string} params.user_id - 用户ID
 * @param {string} params.status - 订单状态
 * @param {string} params.start_time - 开始时间
 * @param {string} params.end_time - 结束时间
 * @param {number} params.min_amount - 最小金额
 * @param {number} params.max_amount - 最大金额
 */
export function queryOrdersWithFilters(params) {
  return queryOrders(params)
}
