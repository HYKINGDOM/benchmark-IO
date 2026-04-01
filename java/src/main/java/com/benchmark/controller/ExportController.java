package com.benchmark.controller;

import com.benchmark.model.ApiResponse;
import com.benchmark.model.ExportRequest;
import com.benchmark.model.ExportTask;
import com.benchmark.model.OrderQueryRequest;
import com.benchmark.service.AsyncTaskService;
import com.benchmark.service.ExportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Export Controller
 *
 * @author Benchmark Team
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/exports")
@RequiredArgsConstructor
@Tag(name = "Export API", description = "数据导出接口")
public class ExportController {

    private final ExportService exportService;
    private final AsyncTaskService asyncTaskService;

    /**
     * Sync export - return file stream directly
     */
    @PostMapping("/sync")
    @Operation(summary = "同步导出", description = "同步导出订单数据，直接返回文件流")
    public void syncExport(
            @RequestBody ExportRequest request,
            HttpServletResponse response
    ) throws IOException {
        log.info("Sync export request - format: {}, limit: {}", request.getFormat(), request.getLimit());
        exportService.syncExport(request, response);
    }

    /**
     * Async export - return task ID
     */
    @PostMapping("/async")
    @Operation(summary = "异步导出", description = "异步导出订单数据，返回任务ID")
    public ApiResponse<Map<String, Object>> asyncExport(@RequestBody ExportRequest request) {
        log.info("Async export request - format: {}, limit: {}", request.getFormat(), request.getLimit());

        ExportTask task = asyncTaskService.createTask(request);

        Map<String, Object> data = new HashMap<>();
        data.put("task_id", task.getTaskId());
        data.put("status", task.getStatus().name().toLowerCase());

        log.info("Async export task created - taskId: {}", task.getTaskId());

        return ApiResponse.success(data);
    }

    /**
     * Get task status
     */
    @GetMapping("/tasks/{task_id}")
    @Operation(summary = "任务状态查询", description = "查询异步导出任务状态")
    public ApiResponse<Map<String, Object>> getTaskStatus(
            @Parameter(description = "任务ID") @PathVariable("task_id") String taskId
    ) {
        log.debug("Get task status - taskId: {}", taskId);

        ExportTask task = asyncTaskService.getTask(taskId);
        if (task == null) {
            return ApiResponse.error(404, "Task not found");
        }

        Map<String, Object> data = new HashMap<>();
        data.put("task_id", task.getTaskId());
        data.put("status", task.getStatus().name().toLowerCase());
        data.put("progress", task.getProgress());
        data.put("created_at", task.getCreatedAt());
        data.put("completed_at", task.getCompletedAt());

        if (task.getStatus() == ExportTask.TaskStatus.COMPLETED) {
            data.put("download_url", "/api/v1/exports/download/" + task.getDownloadToken());
        } else if (task.getStatus() == ExportTask.TaskStatus.FAILED) {
            data.put("error", task.getErrorMessage());
        }

        return ApiResponse.success(data);
    }

    /**
     * SSE progress streaming
     */
    @GetMapping("/sse/{task_id}")
    @Operation(summary = "SSE进度推送", description = "通过SSE实时推送任务进度")
    public SseEmitter subscribeToTask(
            @Parameter(description = "任务ID") @PathVariable("task_id") String taskId
    ) {
        log.info("SSE subscription - taskId: {}", taskId);

        // Create SSE emitter with 30 minutes timeout
        SseEmitter emitter = new SseEmitter(30 * 60 * 1000L);

        // Register emitter
        asyncTaskService.registerSseEmitter(taskId, emitter);

        // Send initial connection event
        try {
            emitter.send(SseEmitter.event()
                    .name("connected")
                    .data(Map.of("task_id", taskId)));
        } catch (IOException e) {
            log.error("Failed to send initial SSE event", e);
        }

        return emitter;
    }

    /**
     * Download file by token
     */
    @GetMapping("/download/{token}")
    @Operation(summary = "文件下载", description = "通过下载token获取导出文件")
    public ResponseEntity<Resource> downloadFile(
            @Parameter(description = "下载token") @PathVariable String token
    ) {
        log.info("Download file request - token: {}", token);

        ExportTask task = asyncTaskService.getTaskByToken(token);
        if (task == null) {
            log.warn("Invalid download token: {}", token);
            return ResponseEntity.notFound().build();
        }

        if (task.getStatus() != ExportTask.TaskStatus.COMPLETED) {
            log.warn("Task not completed - taskId: {}, status: {}", task.getTaskId(), task.getStatus());
            return ResponseEntity.badRequest().build();
        }

        File file = new File(task.getFilePath());
        if (!file.exists()) {
            log.warn("File not found - path: {}", task.getFilePath());
            return ResponseEntity.notFound().build();
        }

        Resource resource = new FileSystemResource(file);
        String contentType = "xlsx".equals(task.getFormat())
                ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                : "text/csv";

        String filename = file.getName();

        log.info("Downloading file - filename: {}, size: {} bytes", filename, file.length());

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body(resource);
    }

    /**
     * Stream export - SSE streaming
     */
    @PostMapping("/stream")
    @Operation(summary = "流式导出", description = "通过SSE流式导出数据")
    public void streamExport(
            @RequestBody ExportRequest request,
            HttpServletResponse response
    ) throws IOException {
        log.info("Stream export request - format: {}, limit: {}", request.getFormat(), request.getLimit());
        exportService.streamExport(request, response);
    }
}
