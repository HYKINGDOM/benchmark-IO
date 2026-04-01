package com.benchmark.service;

import com.benchmark.model.ExportRequest;
import com.benchmark.model.ExportTask;
import com.benchmark.model.Order;
import com.benchmark.model.OrderQueryRequest;
import com.benchmark.repository.OrderRepository;
import com.benchmark.util.CsvWriter;
import com.benchmark.util.ExcelWriter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.Cursor;
import org.jooq.Record;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Async Task Service
 *
 * @author Benchmark Team
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AsyncTaskService {

    private final OrderRepository orderRepository;

    @Value("${export.temp-dir}")
    private String tempDir;

    @Value("${export.max-rows}")
    private Integer maxRows;

    // In-memory task storage (in production, use Redis or database)
    private final Map<String, ExportTask> taskStore = new ConcurrentHashMap<>();

    // SSE emitters for real-time progress
    private final Map<String, org.springframework.web.servlet.mvc.method.annotation.SseEmitter> sseEmitters = new ConcurrentHashMap<>();

    /**
     * Create async export task
     */
    public ExportTask createTask(ExportRequest request) {
        String taskId = UUID.randomUUID().toString();
        String downloadToken = UUID.randomUUID().toString();

        ExportTask task = ExportTask.builder()
                .taskId(taskId)
                .status(ExportTask.TaskStatus.PENDING)
                .progress(0)
                .format(request.getFormat())
                .totalCount(0L)
                .processedCount(0L)
                .createdAt(LocalDateTime.now())
                .downloadToken(downloadToken)
                .build();

        taskStore.put(taskId, task);

        // Start async processing
        processAsyncExport(taskId, request);

        return task;
    }

    /**
     * Get task by ID
     */
    public ExportTask getTask(String taskId) {
        return taskStore.get(taskId);
    }

    /**
     * Get task by download token
     */
    public ExportTask getTaskByToken(String token) {
        return taskStore.values().stream()
                .filter(task -> token.equals(task.getDownloadToken()))
                .findFirst()
                .orElse(null);
    }

    /**
     * Register SSE emitter
     */
    public void registerSseEmitter(String taskId, org.springframework.web.servlet.mvc.method.annotation.SseEmitter emitter) {
        sseEmitters.put(taskId, emitter);
        emitter.onCompletion(() -> sseEmitters.remove(taskId));
        emitter.onTimeout(() -> sseEmitters.remove(taskId));
    }

    /**
     * Async export processing
     */
    @Async
    public void processAsyncExport(String taskId, ExportRequest request) {
        ExportTask task = taskStore.get(taskId);
        if (task == null) {
            log.error("Task not found: {}", taskId);
            return;
        }

        try {
            log.info("Starting async export task: {}", taskId);

            // Update task status
            task.setStatus(ExportTask.TaskStatus.PROCESSING);
            task.setProgress(0);
            notifyTaskUpdate(task);

            // Prepare query
            OrderQueryRequest queryRequest = request.getConditions() != null
                    ? request.getConditions()
                    : new OrderQueryRequest();

            Integer limit = request.getLimit() != null ? Math.min(request.getLimit(), maxRows) : maxRows;

            // Create temp directory
            Path tempPath = Paths.get(tempDir);
            if (!Files.exists(tempPath)) {
                Files.createDirectories(tempPath);
            }

            // Generate filename
            String filename = generateFilename(taskId, request.getFormat());
            Path filePath = tempPath.resolve(filename);

            // Export to file
            try (OutputStream outputStream = new BufferedOutputStream(Files.newOutputStream(filePath))) {
                if ("xlsx".equals(request.getFormat())) {
                    exportToExcel(task, queryRequest, limit, outputStream);
                } else {
                    exportToCsv(task, queryRequest, limit, outputStream);
                }
            }

            // Update task completion
            task.setStatus(ExportTask.TaskStatus.COMPLETED);
            task.setProgress(100);
            task.setCompletedAt(LocalDateTime.now());
            task.setFilePath(filePath.toString());
            notifyTaskUpdate(task);

            log.info("Async export task completed: {}", taskId);

        } catch (Exception e) {
            log.error("Async export task failed: {}", taskId, e);

            task.setStatus(ExportTask.TaskStatus.FAILED);
            task.setErrorMessage(e.getMessage());
            task.setCompletedAt(LocalDateTime.now());
            notifyTaskUpdate(task);
        }
    }

    /**
     * Export to CSV with progress tracking
     */
    private void exportToCsv(ExportTask task, OrderQueryRequest request, Integer limit, OutputStream outputStream) throws IOException {
        try (Cursor<Record> cursor = orderRepository.streamOrders(request, limit)) {
            CsvWriter csvWriter = new CsvWriter(outputStream);
            csvWriter.writeHeader();

            long count = 0;
            for (Record record : cursor) {
                Order order = mapRecordToOrder(record);
                csvWriter.writeRow(order);
                count++;

                // Update progress every 1000 records
                if (count % 1000 == 0) {
                    task.setProcessedCount(count);
                    task.setProgress(calculateProgress(count, limit));
                    notifyTaskUpdate(task);
                }
            }

            task.setTotalCount(count);
            task.setProcessedCount(count);
            log.info("Exported {} records to CSV for task: {}", count, task.getTaskId());
        }
    }

    /**
     * Export to Excel with progress tracking
     */
    private void exportToExcel(ExportTask task, OrderQueryRequest request, Integer limit, OutputStream outputStream) throws IOException {
        try (Cursor<Record> cursor = orderRepository.streamOrders(request, limit)) {
            ExcelWriter excelWriter = new ExcelWriter(outputStream);
            excelWriter.writeHeader();

            long count = 0;
            for (Record record : cursor) {
                Order order = mapRecordToOrder(record);
                excelWriter.writeRow(order);
                count++;

                // Update progress every 1000 records
                if (count % 1000 == 0) {
                    task.setProcessedCount(count);
                    task.setProgress(calculateProgress(count, limit));
                    notifyTaskUpdate(task);
                    excelWriter.flush();
                }
            }

            excelWriter.close();

            task.setTotalCount(count);
            task.setProcessedCount(count);
            log.info("Exported {} records to Excel for task: {}", count, task.getTaskId());
        }
    }

    /**
     * Calculate progress percentage
     */
    private Integer calculateProgress(long processed, Integer limit) {
        if (limit == null || limit <= 0) {
            // If no limit, show progress based on processed count
            return Math.min((int) (processed / 10000), 99);
        }
        return (int) ((processed * 100) / limit);
    }

    /**
     * Notify task update via SSE
     */
    private void notifyTaskUpdate(ExportTask task) {
        org.springframework.web.servlet.mvc.method.annotation.SseEmitter emitter = sseEmitters.get(task.getTaskId());
        if (emitter != null) {
            try {
                if (task.getStatus() == ExportTask.TaskStatus.COMPLETED) {
                    emitter.send(org.springframework.web.servlet.mvc.method.annotation.SseEmitter.event()
                            .name("completed")
                            .data(Map.of(
                                    "progress", task.getProgress(),
                                    "download_url", "/api/v1/exports/download/" + task.getDownloadToken()
                            )));
                    emitter.complete();
                } else if (task.getStatus() == ExportTask.TaskStatus.FAILED) {
                    emitter.send(org.springframework.web.servlet.mvc.method.annotation.SseEmitter.event()
                            .name("failed")
                            .data(Map.of("error", task.getErrorMessage())));
                    emitter.complete();
                } else {
                    emitter.send(org.springframework.web.servlet.mvc.method.annotation.SseEmitter.event()
                            .name("progress")
                            .data(Map.of("progress", task.getProgress())));
                }
            } catch (Exception e) {
                log.error("Failed to send SSE update for task: {}", task.getTaskId(), e);
                sseEmitters.remove(task.getTaskId());
            }
        }
    }

    /**
     * Generate export filename
     */
    private String generateFilename(String taskId, String format) {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        return String.format("orders_%s_%s.%s", timestamp, taskId.substring(0, 8), format);
    }

    /**
     * Map Record to Order
     */
    private Order mapRecordToOrder(Record record) {
        return Order.builder()
                .orderId(record.get("order_id", Long.class))
                .orderNo(record.get("order_no", String.class))
                .userId(record.get("user_id", Long.class))
                .userName(record.get("user_name", String.class))
                .userPhone(record.get("user_phone", String.class))
                .userIdCard(record.get("user_id_card", String.class))
                .userEmail(record.get("user_email", String.class))
                .userAddress(record.get("user_address", String.class))
                .productId(record.get("product_id", Long.class))
                .productName(record.get("product_name", String.class))
                .productCategory(record.get("product_category", String.class))
                .productPrice(record.get("product_price", java.math.BigDecimal.class))
                .quantity(record.get("quantity", Integer.class))
                .totalAmount(record.get("total_amount", java.math.BigDecimal.class))
                .discountAmount(record.get("discount_amount", java.math.BigDecimal.class))
                .payAmount(record.get("pay_amount", java.math.BigDecimal.class))
                .orderStatus(record.get("order_status", String.class))
                .paymentMethod(record.get("payment_method", String.class))
                .paymentTime(record.get("payment_time", LocalDateTime.class))
                .orderSource(record.get("order_source", String.class))
                .shippingAddress(record.get("shipping_address", String.class))
                .receiverName(record.get("receiver_name", String.class))
                .receiverPhone(record.get("receiver_phone", String.class))
                .logisticsNo(record.get("logistics_no", String.class))
                .deliveryTime(record.get("delivery_time", LocalDateTime.class))
                .completeTime(record.get("complete_time", LocalDateTime.class))
                .remark(record.get("remark", String.class))
                .createdAt(record.get("created_at", LocalDateTime.class))
                .updatedAt(record.get("updated_at", LocalDateTime.class))
                .isDeleted(record.get("is_deleted", Integer.class))
                .build();
    }
}
