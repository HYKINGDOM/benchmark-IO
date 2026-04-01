package com.benchmark.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Export Task Entity
 *
 * @author Benchmark Team
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExportTask {

    private String taskId;
    private TaskStatus status;
    private Integer progress;
    private String format;
    private Long totalCount;
    private Long processedCount;
    private LocalDateTime createdAt;
    private LocalDateTime completedAt;
    private String downloadToken;
    private String filePath;
    private String errorMessage;

    public enum TaskStatus {
        PENDING,
        PROCESSING,
        COMPLETED,
        FAILED
    }
}
