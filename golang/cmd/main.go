package main

import (
	"benchmark-api/internal/config"
	"benchmark-api/internal/controller"
	"benchmark-api/internal/middleware"
	"benchmark-api/internal/model"
	"benchmark-api/internal/repository"
	"benchmark-api/internal/service"
	"fmt"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func main() {
	// 加载配置
	cfg := config.Load()

	// 设置 Gin 模式
	gin.SetMode(cfg.Server.Mode)

	// 初始化数据库
	db, err := initDatabase(cfg)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// 自动迁移
	if err := autoMigrate(db); err != nil {
		log.Fatalf("Failed to migrate database: %v", err)
	}

	// 初始化依赖
	orderRepo := repository.NewOrderRepository(db)
	orderSvc := service.NewOrderService(orderRepo)
	taskSvc := service.NewTaskService(db)
	exportSvc := service.NewExportService(db, orderRepo, taskSvc, &cfg.Export)

	orderCtrl := controller.NewOrderController(orderSvc)
	exportCtrl := controller.NewExportController(exportSvc, taskSvc)

	// 创建 Gin 路由
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(middleware.LoggerMiddleware())
	router.Use(middleware.CORSMiddleware())

	// 健康检查
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"service": "golang-api",
		})
	})

	// Prometheus metrics 端点
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// API 路由组
	api := router.Group("/api/v1")
	api.Use(middleware.AuthMiddleware(cfg.Auth.APIKey))
	{
		// 订单路由
		api.GET("/orders", orderCtrl.GetOrders)

		// 导出路由
		exports := api.Group("/exports")
		{
			exports.POST("/sync", exportCtrl.ExportSync)
			exports.POST("/async", exportCtrl.ExportAsync)
			exports.POST("/stream", exportCtrl.ExportStream)
			exports.GET("/tasks/:task_id", exportCtrl.GetTaskStatus)
			exports.GET("/sse/:task_id", exportCtrl.StreamProgress)
			exports.GET("/download/:token", exportCtrl.DownloadFile)
		}
	}

	// 启动服务器
	addr := fmt.Sprintf(":%d", cfg.Server.Port)
	log.Printf("Server starting on %s", addr)
	if err := router.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func initDatabase(cfg *config.Config) (*gorm.DB, error) {
	dsn := cfg.Database.DSN()

	logLevel := logger.Warn
	if cfg.Server.Mode == "debug" {
		logLevel = logger.Info
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	})
	if err != nil {
		return nil, err
	}

	// 获取底层的 sql.DB
	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	// 设置连接池
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)

	// 测试连接
	if err := sqlDB.Ping(); err != nil {
		return nil, err
	}

	log.Println("Database connected successfully")
	return db, nil
}

func autoMigrate(db *gorm.DB) error {
	// 只迁移 export_tasks 表，orders 表已存在
	if err := db.AutoMigrate(&model.ExportTask{}); err != nil {
		return err
	}
	log.Println("Database migration completed")
	return nil
}
