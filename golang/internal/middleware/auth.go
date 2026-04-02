package middleware

import (
	"benchmark-api/pkg/response"
	"fmt"
	"strings"

	"github.com/gin-gonic/gin"
)

func AuthMiddleware(apiKey string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从 Header 获取 API Key
		key := c.GetHeader("X-API-Key")
		if key == "" {
			// 尝试从 Authorization Header 获取
			auth := c.GetHeader("Authorization")
			if strings.HasPrefix(auth, "Bearer ") {
				key = strings.TrimPrefix(auth, "Bearer ")
			}
		}

		if key == "" {
			response.Unauthorized(c, "缺少 API Key")
			c.Abort()
			return
		}

		if key != apiKey {
			response.Unauthorized(c, "无效的 API Key")
			c.Abort()
			return
		}

		c.Next()
	}
}

func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With, X-API-Key")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

func LoggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		path := c.Request.URL.Path
		method := c.Request.Method

		c.Next()

		statusCode := c.Writer.Status()
		clientIP := c.ClientIP()

		gin.DefaultWriter.Write([]byte(
			fmt.Sprintf("[GIN] %s | %s | %d | %s\n", method, path, statusCode, clientIP),
		))
	}
}
