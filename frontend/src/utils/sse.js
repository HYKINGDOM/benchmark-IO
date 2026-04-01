/**
 * SSE (Server-Sent Events) 客户端
 */
export class SSEClient {
  constructor(url, options = {}) {
    this.url = url
    this.options = {
      headers: {},
      onMessage: null,
      onError: null,
      onOpen: null,
      ...options
    }
    this.eventSource = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = options.maxReconnectAttempts || 3
  }

  /**
   * 连接 SSE
   */
  connect() {
    return new Promise((resolve, reject) => {
      try {
        // 添加 API Key 到 URL
        const apiKey = import.meta.env.VITE_API_KEY || 'benchmark-api-key-2024'
        const url = new URL(this.url, window.location.origin)
        url.searchParams.append('api_key', apiKey)
        
        this.eventSource = new EventSource(url.toString())
        
        this.eventSource.onopen = () => {
          console.log('SSE connection opened')
          this.reconnectAttempts = 0
          if (this.options.onOpen) {
            this.options.onOpen()
          }
          resolve()
        }
        
        this.eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (this.options.onMessage) {
              this.options.onMessage(data)
            }
          } catch (error) {
            console.error('Failed to parse SSE message:', error)
          }
        }
        
        this.eventSource.onerror = (error) => {
          console.error('SSE error:', error)
          
          if (this.options.onError) {
            this.options.onError(error)
          }
          
          // 自动重连
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)
            setTimeout(() => this.connect(), 1000 * this.reconnectAttempts)
          } else {
            this.close()
            reject(new Error('SSE connection failed after max reconnect attempts'))
          }
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  /**
   * 关闭 SSE 连接
   */
  close() {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
  }

  /**
   * 检查连接状态
   */
  isConnected() {
    return this.eventSource && this.eventSource.readyState === EventSource.OPEN
  }
}

/**
 * 创建 SSE 客户端实例
 */
export function createSSEClient(url, options) {
  return new SSEClient(url, options)
}
