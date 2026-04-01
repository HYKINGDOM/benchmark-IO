package com.benchmark.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Export Request
 *
 * @author Benchmark Team
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExportRequest {

    private String format; // csv or xlsx
    private Integer limit;
    private OrderQueryRequest conditions;

    public String getFormat() {
        return format != null && (format.equalsIgnoreCase("csv") || format.equalsIgnoreCase("xlsx"))
                ? format.toLowerCase()
                : "csv";
    }
}
