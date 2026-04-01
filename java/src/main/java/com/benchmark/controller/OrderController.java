package com.benchmark.controller;

import com.benchmark.model.ApiResponse;
import com.benchmark.model.Order;
import com.benchmark.model.OrderQueryRequest;
import com.benchmark.model.PageResponse;
import com.benchmark.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Order Controller
 *
 * @author Benchmark Team
 */
@Slf4j
@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Tag(name = "Order API", description = "订单查询接口")
public class OrderController {

    private final OrderService orderService;

    /**
     * Query orders with pagination
     */
    @GetMapping("/orders")
    @Operation(summary = "订单查询", description = "支持分页、时间范围、状态、金额、用户ID、订单编号筛选")
    public ApiResponse<PageResponse<Order>> queryOrders(
            @Parameter(description = "页码") @RequestParam(required = false) Integer page,
            @Parameter(description = "每页条数") @RequestParam(required = false) Integer pageSize,
            @Parameter(description = "开始时间 (yyyy-MM-dd)") @RequestParam(required = false) LocalDate startTime,
            @Parameter(description = "结束时间 (yyyy-MM-dd)") @RequestParam(required = false) LocalDate endTime,
            @Parameter(description = "订单状态") @RequestParam(required = false) String status,
            @Parameter(description = "最小金额") @RequestParam(required = false) BigDecimal minAmount,
            @Parameter(description = "最大金额") @RequestParam(required = false) BigDecimal maxAmount,
            @Parameter(description = "用户ID") @RequestParam(required = false) String userId,
            @Parameter(description = "订单编号") @RequestParam(required = false) String orderNo
    ) {
        log.info("Query orders request - page: {}, pageSize: {}, status: {}", page, pageSize, status);

        OrderQueryRequest request = OrderQueryRequest.builder()
                .page(page)
                .pageSize(pageSize)
                .startTime(startTime)
                .endTime(endTime)
                .status(status)
                .minAmount(minAmount)
                .maxAmount(maxAmount)
                .userId(userId)
                .orderNo(orderNo)
                .build();

        PageResponse<Order> response = orderService.queryOrders(request);

        log.info("Query orders completed - total: {}, page: {}", response.getTotal(), response.getPage());

        return ApiResponse.success(response);
    }
}
