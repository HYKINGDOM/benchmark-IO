package com.benchmark.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Paginated Response
 *
 * @author Benchmark Team
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PageResponse<T> {

    private Long total;
    private Integer page;
    private Integer pageSize;
    private List<T> items;
}
