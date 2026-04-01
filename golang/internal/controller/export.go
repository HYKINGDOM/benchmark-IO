package controller

import (
	"benchmark-api/internal/model"
	"benchmark-api/internal/service"
	"benchmark-api/pkg/response"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

type ExportController struct {
	exportSvc *service.ExportService
	taskSvc   *service.TaskService
}

func NewExportController(exportSvc *service.ExportService, taskSvc *service.TaskService) *ExportController {
	return &ExportController{
		exportSvc: exportSvc,
		taskSvc:   taskSvc,
	}
}

// ExportSync 同步导出
// @Summary 同步导出订单
// @Description 同步导出订单数据，返回文件流
// @Tags 导出
// @Accept json
// @Produce octet-stream
// @Param format query string false "导出格式 (csv/xlsx)" default(csv)
// @Param start_time query string false "开始时间"
// @Param end_time query string false "结束时间"
// @Param order_no query string false "订单编号"
// @Param user_id query int false "用户ID"
// @Param status query string false "订单状态"
// @Param min_amount query number false "最小金额"
// @Param max_amount query number false "最大金额"
// @Success 200 {file} file
// @Router /api/v1/exports/sync [post]
func (c *ExportController) ExportSync(ctx *gin.Context) {
	var params model.ExportRequest
	if err := ctx.ShouldBindQuery(&params); err != nil {
		response.BadRequest(ctx, "参数错误: "+err.Error())
		return
	}

	data, fileName, err := c.exportSvc.ExportSync(&params)
	if err != nil {
		response.InternalServerError(ctx, "导出失败: "+err.Error())
		return
	}

	contentType := "text/csv"
	if params.GetFormat() == "xlsx" {
		contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
	}

	ctx.Header("Content-Description", "File Transfer")
	ctx.Header("Content-Type", contentType)
	ctx.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	ctx.Header("Content-Transfer-Encoding", "binary")
	ctx.Header("Expires", "0")
	ctx.Header("Cache-Control", "must-revalidate")
	ctx.Header("Pragma", "public")
	ctx.Data(http.StatusOK, contentType, data)
}

// ExportAsync 异步导出
// @Summary 异步导出订单
// @Description 异步导出订单数据，返回任务ID
// @Tags 导出
// @Accept json
// @Produce json
// @Param request query model.ExportRequest true "导出参数"
// @Success 200 {object} response.Response
// @Router /api/v1/exports/async [post]
func (c *ExportController) ExportAsync(ctx *gin.Context) {
	var params model.ExportRequest
	if err := ctx.ShouldBindQuery(&params); err != nil {
		response.BadRequest(ctx, "参数错误: "+err.Error())
		return
	}

	task, err := c.exportSvc.ExportAsync(&params)
	if err != nil {
		response.InternalServerError(ctx, "创建导出任务失败: "+err.Error())
		return
	}

	response.Success(ctx, gin.H{
		"task_id": task.TaskID,
		"status":  task.Status,
	})
}

// GetTaskStatus 查询任务状态
// @Summary 查询导出任务状态
// @Description 根据任务ID查询导出任务状态
// @Tags 导出
// @Produce json
// @Param task_id path string true "任务ID"
// @Success 200 {object} response.Response
// @Router /api/v1/exports/tasks/{task_id} [get]
func (c *ExportController) GetTaskStatus(ctx *gin.Context) {
	taskID := ctx.Param("task_id")
	if taskID == "" {
		response.BadRequest(ctx, "任务ID不能为空")
		return
	}

	task, err := c.taskSvc.GetTask(taskID)
	if err != nil {
		response.NotFound(ctx, "任务不存在")
		return
	}

	downloadURL := ""
	if task.Status == model.TaskStatusCompleted {
		downloadURL = fmt.Sprintf("/api/v1/exports/download/%s", task.DownloadToken)
	}

	response.Success(ctx, task.ToResponse(downloadURL))
}

// StreamProgress SSE 进度推送
// @Summary SSE 进度推送
// @Description 通过 SSE 推送导出任务进度
// @Tags 导出
// @Produce text/event-stream
// @Param task_id path string true "任务ID"
// @Router /api/v1/exports/sse/{task_id} [get]
func (c *ExportController) StreamProgress(ctx *gin.Context) {
	taskID := ctx.Param("task_id")
	if taskID == "" {
		response.BadRequest(ctx, "任务ID不能为空")
		return
	}

	// 设置 SSE headers
	ctx.Header("Content-Type", "text/event-stream")
	ctx.Header("Cache-Control", "no-cache")
	ctx.Header("Connection", "keep-alive")
	ctx.Header("Access-Control-Allow-Origin", "*")

	// 获取任务 channel
	taskCh, ok := c.taskSvc.GetTaskChannel(taskID)
	if !ok {
		// 如果没有 channel，直接查询数据库
		task, err := c.taskSvc.GetTask(taskID)
		if err != nil {
			ctx.SSEvent("error", gin.H{"message": "任务不存在"})
			return
		}
		ctx.SSEvent("progress", task.ToResponse(""))
		return
	}

	// 监听任务进度
	ctx.Stream(func(w io.Writer) bool {
		select {
		case task, ok := <-taskCh:
			if !ok {
				return false
			}
			downloadURL := ""
			if task.Status == model.TaskStatusCompleted {
				downloadURL = fmt.Sprintf("/api/v1/exports/download/%s", task.DownloadToken)
			}
			ctx.SSEvent("progress", task.ToResponse(downloadURL))
			return task.Status != model.TaskStatusCompleted && task.Status != model.TaskStatusFailed
		case <-ctx.Request.Context().Done():
			return false
		}
	})
}

// DownloadFile 文件下载
// @Summary 下载导出文件
// @Description 通过下载令牌下载导出文件
// @Tags 导出
// @Produce octet-stream
// @Param token path string true "下载令牌"
// @Success 200 {file} file
// @Router /api/v1/exports/download/{token} [get]
func (c *ExportController) DownloadFile(ctx *gin.Context) {
	token := ctx.Param("token")
	if token == "" {
		response.BadRequest(ctx, "下载令牌不能为空")
		return
	}

	task, err := c.taskSvc.GetTaskByToken(token)
	if err != nil {
		response.NotFound(ctx, "文件不存在或已过期")
		return
	}

	if task.Status != model.TaskStatusCompleted {
		response.BadRequest(ctx, "文件尚未生成完成")
		return
	}

	// 检查文件是否存在
	if _, err := os.Stat(task.FilePath); os.IsNotExist(err) {
		response.NotFound(ctx, "文件不存在")
		return
	}

	// 打开文件
	file, err := os.Open(task.FilePath)
	if err != nil {
		response.InternalServerError(ctx, "打开文件失败")
		return
	}
	defer file.Close()

	// 获取文件信息
	fileInfo, _ := file.Stat()

	contentType := "text/csv"
	if filepath.Ext(task.FileName) == ".xlsx" {
		contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
	}

	ctx.Header("Content-Description", "File Transfer")
	ctx.Header("Content-Type", contentType)
	ctx.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", task.FileName))
	ctx.Header("Content-Length", fmt.Sprintf("%d", fileInfo.Size()))
	ctx.Header("Content-Transfer-Encoding", "binary")
	ctx.Header("Expires", "0")
	ctx.Header("Cache-Control", "must-revalidate")
	ctx.Header("Pragma", "public")

	http.ServeContent(ctx.Writer, ctx.Request, task.FileName, fileInfo.ModTime(), file)
}

// ExportStream 流式导出
// @Summary 流式导出订单
// @Description 流式导出订单数据，边生成边返回
// @Tags 导出
// @Accept json
// @Produce octet-stream
// @Param request query model.ExportRequest true "导出参数"
// @Success 200 {file} file
// @Router /api/v1/exports/stream [post]
func (c *ExportController) ExportStream(ctx *gin.Context) {
	var params model.ExportRequest
	if err := ctx.ShouldBindQuery(&params); err != nil {
		response.BadRequest(ctx, "参数错误: "+err.Error())
		return
	}

	contentType := "text/csv"
	fileName := fmt.Sprintf("orders_stream.csv")
	if params.GetFormat() == "xlsx" {
		contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
		fileName = fmt.Sprintf("orders_stream.xlsx")
	}

	ctx.Header("Content-Type", contentType)
	ctx.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	ctx.Header("Transfer-Encoding", "chunked")

	err := c.exportSvc.ExportStream(&params, func(data []byte) error {
		_, err := ctx.Writer.Write(data)
		ctx.Writer.Flush()
		return err
	})

	if err != nil {
		response.InternalServerError(ctx, "导出失败: "+err.Error())
		return
	}
}
