package service

import (
	"benchmark-api/internal/model"
	"sync"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type TaskService struct {
	db           *gorm.DB
	taskChannels map[string]chan *model.ExportTask
	mu           sync.RWMutex
}

func NewTaskService(db *gorm.DB) *TaskService {
	return &TaskService{
		db:           db,
		taskChannels: make(map[string]chan *model.ExportTask),
	}
}

func (s *TaskService) CreateTask(format string, total int) (*model.ExportTask, error) {
	taskID := uuid.New().String()
	downloadToken := uuid.New().String()

	task := &model.ExportTask{
		TaskID:        taskID,
		Status:        model.TaskStatusPending,
		Total:         total,
		Processed:     0,
		Failed:        0,
		Format:        format,
		DownloadToken: downloadToken,
		CreatedAt:     time.Now(),
		UpdatedAt:     time.Now(),
	}

	if err := s.db.Create(task).Error; err != nil {
		return nil, err
	}

	// 创建进度通知 channel
	s.mu.Lock()
	s.taskChannels[taskID] = make(chan *model.ExportTask, 100)
	s.mu.Unlock()

	return task, nil
}

func (s *TaskService) GetTask(taskID string) (*model.ExportTask, error) {
	var task model.ExportTask
	if err := s.db.Where("task_id = ?", taskID).First(&task).Error; err != nil {
		return nil, err
	}
	return &task, nil
}

func (s *TaskService) GetTaskByToken(token string) (*model.ExportTask, error) {
	var task model.ExportTask
	if err := s.db.Where("download_token = ?", token).First(&task).Error; err != nil {
		return nil, err
	}
	return &task, nil
}

func (s *TaskService) UpdateTask(task *model.ExportTask) error {
	task.UpdatedAt = time.Now()
	return s.db.Save(task).Error
}

func (s *TaskService) UpdateProgress(taskID string, processed, failed int) error {
	task, err := s.GetTask(taskID)
	if err != nil {
		return err
	}

	task.Processed = processed
	task.Failed = failed
	task.UpdatedAt = time.Now()

	if err := s.db.Save(task).Error; err != nil {
		return err
	}

	// 通知进度更新
	s.mu.RLock()
	if ch, ok := s.taskChannels[taskID]; ok {
		select {
		case ch <- task:
		default:
			// channel 满了就跳过
		}
	}
	s.mu.RUnlock()

	return nil
}

func (s *TaskService) CompleteTask(taskID, fileName, filePath string) error {
	task, err := s.GetTask(taskID)
	if err != nil {
		return err
	}

	now := time.Now()
	task.Status = model.TaskStatusCompleted
	task.FileName = fileName
	task.FilePath = filePath
	task.CompletedAt = &now
	task.UpdatedAt = now

	if err := s.db.Save(task).Error; err != nil {
		return err
	}

	// 通知完成
	s.mu.RLock()
	if ch, ok := s.taskChannels[taskID]; ok {
		select {
		case ch <- task:
		default:
		}
		close(ch)
		delete(s.taskChannels, taskID)
	}
	s.mu.RUnlock()

	return nil
}

func (s *TaskService) FailTask(taskID, errMsg string) error {
	task, err := s.GetTask(taskID)
	if err != nil {
		return err
	}

	now := time.Now()
	task.Status = model.TaskStatusFailed
	task.Error = errMsg
	task.CompletedAt = &now
	task.UpdatedAt = now

	if err := s.db.Save(task).Error; err != nil {
		return err
	}

	// 通知失败
	s.mu.RLock()
	if ch, ok := s.taskChannels[taskID]; ok {
		select {
		case ch <- task:
		default:
		}
		close(ch)
		delete(s.taskChannels, taskID)
	}
	s.mu.RUnlock()

	return nil
}

func (s *TaskService) GetTaskChannel(taskID string) (<-chan *model.ExportTask, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	ch, ok := s.taskChannels[taskID]
	if !ok {
		return nil, false
	}
	return ch, true
}
