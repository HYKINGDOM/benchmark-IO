package com.benchmark.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Order Query Request
 *
 * @author Benchmark Team
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrderQueryRequest {

    private Integer page;
    private Integer pageSize;
    private LocalDate startTime;
    private LocalDate endTime;
    private String status;
    private BigDecimal minAmount;
    private BigDecimal maxAmount;
    private String userId;
    private String orderNo;

    public Integer getPage() {
        return page != null && page > 0 ? page : 1;
    }

    public Integer getPageSize() {
        return pageSize != null && pageSize > 0 && pageSize <= 1000 ? pageSize : 20;
    }
}
