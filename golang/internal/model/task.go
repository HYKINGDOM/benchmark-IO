package model

import (
	"time"
)

type TaskStatus string

const (
	TaskStatusPending    TaskStatus = "pending"
	TaskStatusProcessing TaskStatus = "processing"
	TaskStatusCompleted  TaskStatus = "completed"
	TaskStatusFailed     TaskStatus = "failed"
)

type ExportTask struct {
	TaskID       string     `gorm:"primaryKey" json:"task_id"`
	Status       TaskStatus `gorm:"type:varchar(16);not null;default:'pending'" json:"status"`
	Total        int        `gorm:"not null;default:0" json:"total"`
	Processed    int        `gorm:"not null;default:0" json:"processed"`
	Failed       int        `gorm:"not null;default:0" json:"failed"`
	Format       string     `gorm:"type:varchar(8);not null" json:"format"`
	FileName     string     `gorm:"type:varchar(256)" json:"file_name"`
	FilePath     string     `gorm:"type:varchar(512)" json:"file_path"`
	DownloadToken string    `gorm:"type:varchar(64)" json:"download_token"`
	Error        string     `gorm:"type:text" json:"error"`
	CreatedAt    time.Time  `gorm:"not null;default:CURRENT_TIMESTAMP" json:"created_at"`
	UpdatedAt    time.Time  `gorm:"not null;default:CURRENT_TIMESTAMP" json:"updated_at"`
	CompletedAt  *time.Time `json:"completed_at"`
}

func (ExportTask) TableName() string {
	return "export_tasks"
}

type ExportRequest struct {
	Format     string  `form:"format" json:"format"` // csv, xlsx
	StartTime  *string `form:"start_time" json:"start_time"`
	EndTime    *string `form:"end_time" json:"end_time"`
	OrderNo    string  `form:"order_no" json:"order_no"`
	UserID     *int64  `form:"user_id" json:"user_id"`
	Status     string  `form:"status" json:"status"`
	MinAmount  *float64 `form:"min_amount" json:"min_amount"`
	MaxAmount  *float64 `form:"max_amount" json:"max_amount"`
}

func (r *ExportRequest) GetFormat() string {
	if r.Format == "" {
		return "csv"
	}
	return r.Format
}

type TaskResponse struct {
	TaskID      string     `json:"task_id"`
	Status      TaskStatus `json:"status"`
	Total       int        `json:"total"`
	Processed   int        `json:"processed"`
	Failed      int        `json:"failed"`
	Progress    float64    `json:"progress"`
	FileName    string     `json:"file_name,omitempty"`
	DownloadURL string     `json:"download_url,omitempty"`
	Error       string     `json:"error,omitempty"`
	CreatedAt   time.Time  `json:"created_at"`
	CompletedAt *time.Time `json:"completed_at,omitempty"`
}

func (t *ExportTask) ToResponse(downloadURL string) *TaskResponse {
	progress := 0.0
	if t.Total > 0 {
		progress = float64(t.Processed) / float64(t.Total) * 100
	}
	
	return &TaskResponse{
		TaskID:      t.TaskID,
		Status:      t.Status,
		Total:       t.Total,
		Processed:   t.Processed,
		Failed:      t.Failed,
		Progress:    progress,
		FileName:    t.FileName,
		DownloadURL: downloadURL,
		Error:       t.Error,
		CreatedAt:   t.CreatedAt,
		CompletedAt: t.CompletedAt,
	}
}
