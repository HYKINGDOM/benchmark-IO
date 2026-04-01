package service

import (
	"benchmark-api/internal/config"
	"benchmark-api/internal/model"
	"benchmark-api/internal/repository"
	"benchmark-api/internal/util"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"gorm.io/gorm"
)

type ExportService struct {
	db        *gorm.DB
	repo      *repository.OrderRepository
	taskSvc   *TaskService
	config    *config.ExportConfig
	workerSem chan struct{}
}

func NewExportService(db *gorm.DB, repo *repository.OrderRepository, taskSvc *TaskService, cfg *config.ExportConfig) *ExportService {
	return &ExportService{
		db:        db,
		repo:      repo,
		taskSvc:   taskSvc,
		config:    cfg,
		workerSem: make(chan struct{}, cfg.MaxConcurrent),
	}
}

// ExportSync 同步导出
func (s *ExportService) ExportSync(params *model.ExportRequest) ([]byte, string, error) {
	var data []byte
	var fileName string

	switch params.GetFormat() {
	case "xlsx":
		data, fileName, err := s.exportExcelSync(params)
		return data, fileName, err
	default:
		data, fileName, err := s.exportCSVSync(params)
		return data, fileName, err
	}
}

func (s *ExportService) exportCSVSync(params *model.ExportRequest) ([]byte, string, error) {
	writer := util.NewCSVWriter()

	err := s.repo.FindByParamsStream(params, s.config.ChunkSize, func(orders []model.Order) error {
		return writer.WriteOrders(orders)
	})

	if err != nil {
		return nil, "", err
	}

	fileName := fmt.Sprintf("orders_%s.csv", time.Now().Format("20060102150405"))
	return writer.Bytes(), fileName, nil
}

func (s *ExportService) exportExcelSync(params *model.ExportRequest) ([]byte, string, error) {
	writer := util.NewExcelWriter()
	defer writer.Close()

	err := s.repo.FindByParamsStream(params, s.config.ChunkSize, func(orders []model.Order) error {
		return writer.WriteOrders(orders)
	})

	if err != nil {
		return nil, "", err
	}

	data, err := writer.Save()
	if err != nil {
		return nil, "", err
	}

	fileName := fmt.Sprintf("orders_%s.xlsx", time.Now().Format("20060102150405"))
	return data, fileName, nil
}

// ExportAsync 异步导出
func (s *ExportService) ExportAsync(params *model.ExportRequest) (*model.ExportTask, error) {
	// 获取总数
	total, err := s.repo.CountByParams(params)
	if err != nil {
		return nil, err
	}

	// 创建任务
	task, err := s.taskSvc.CreateTask(params.GetFormat(), int(total))
	if err != nil {
		return nil, err
	}

	// 启动异步处理
	go s.processExport(task.TaskID, params)

	return task, nil
}

func (s *ExportService) processExport(taskID string, params *model.ExportRequest) {
	// 获取信号量
	s.workerSem <- struct{}{}
	defer func() { <-s.workerSem }()

	// 更新状态为处理中
	task, _ := s.taskSvc.GetTask(taskID)
	task.Status = model.TaskStatusProcessing
	s.taskSvc.UpdateTask(task)

	// 确保输出目录存在
	if err := os.MkdirAll(s.config.OutputDir, 0755); err != nil {
		s.taskSvc.FailTask(taskID, fmt.Sprintf("创建输出目录失败: %v", err))
		return
	}

	var filePath string
	var fileName string
	var err error

	switch params.GetFormat() {
	case "xlsx":
		filePath, fileName, err = s.exportExcelAsync(taskID, params)
	default:
		filePath, fileName, err = s.exportCSVAsync(taskID, params)
	}

	if err != nil {
		s.taskSvc.FailTask(taskID, err.Error())
		return
	}

	// 完成任务
	s.taskSvc.CompleteTask(taskID, fileName, filePath)
}

func (s *ExportService) exportCSVAsync(taskID string, params *model.ExportRequest) (string, string, error) {
	fileName := fmt.Sprintf("orders_%s.csv", time.Now().Format("20060102150405"))
	filePath := filepath.Join(s.config.OutputDir, fileName)

	file, err := os.Create(filePath)
	if err != nil {
		return "", "", fmt.Errorf("创建文件失败: %v", err)
	}
	defer file.Close()

	writer := util.NewCSVWriter()
	processed := 0

	err = s.repo.FindByParamsStream(params, s.config.ChunkSize, func(orders []model.Order) error {
		if err := writer.WriteOrders(orders); err != nil {
			return err
		}
		processed += len(orders)
		s.taskSvc.UpdateProgress(taskID, processed, 0)
		return nil
	})

	if err != nil {
		return "", "", err
	}

	_, err = writer.WriteTo(file)
	return filePath, fileName, err
}

func (s *ExportService) exportExcelAsync(taskID string, params *model.ExportRequest) (string, string, error) {
	writer := util.NewExcelWriter()
	defer writer.Close()

	processed := 0

	err := s.repo.FindByParamsStream(params, s.config.ChunkSize, func(orders []model.Order) error {
		if err := writer.WriteOrders(orders); err != nil {
			return err
		}
		processed += len(orders)
		s.taskSvc.UpdateProgress(taskID, processed, 0)
		return nil
	})

	if err != nil {
		return "", "", err
	}

	data, err := writer.Save()
	if err != nil {
		return "", "", err
	}

	fileName := fmt.Sprintf("orders_%s.xlsx", time.Now().Format("20060102150405"))
	filePath := filepath.Join(s.config.OutputDir, fileName)

	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return "", "", fmt.Errorf("写入文件失败: %v", err)
	}

	return filePath, fileName, nil
}

// ExportStream 流式导出
func (s *ExportService) ExportStream(params *model.ExportRequest, callback func([]byte) error) error {
	switch params.GetFormat() {
	case "xlsx":
		return s.exportExcelStream(params, callback)
	default:
		return s.exportCSVStream(params, callback)
	}
}

func (s *ExportService) exportCSVStream(params *model.ExportRequest, callback func([]byte) error) error {
	writer := util.NewCSVWriter()

	err := s.repo.FindByParamsStream(params, s.config.ChunkSize, func(orders []model.Order) error {
		if err := writer.WriteOrders(orders); err != nil {
			return err
		}
		// 每次处理后回调
		return callback(writer.Bytes())
	})

	return err
}

func (s *ExportService) exportExcelStream(params *model.ExportRequest, callback func([]byte) error) error {
	writer := util.NewStreamExcelWriter()
	defer writer.Close()

	if err := writer.WriteHeader(); err != nil {
		return err
	}

	err := s.repo.FindByParamsStream(params, s.config.ChunkSize, func(orders []model.Order) error {
		for i := range orders {
			if err := writer.WriteRow(&orders[i]); err != nil {
				return err
			}
		}
		return nil
	})

	if err != nil {
		return err
	}

	data, err := writer.Save()
	if err != nil {
		return err
	}

	return callback(data)
}
