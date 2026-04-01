package com.benchmark.service;

import com.benchmark.model.Order;
import com.benchmark.model.OrderQueryRequest;
import com.benchmark.model.PageResponse;
import com.benchmark.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Order Service
 *
 * @author Benchmark Team
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;

    /**
     * Query orders with pagination
     */
    public PageResponse<Order> queryOrders(OrderQueryRequest request) {
        log.debug("Querying orders with request: {}", request);

        List<Order> orders = orderRepository.queryOrders(request);
        Long total = orderRepository.countOrders(request);

        return PageResponse.<Order>builder()
                .total(total)
                .page(request.getPage())
                .pageSize(request.getPageSize())
                .items(orders)
                .build();
    }

    /**
     * Query orders for export
     */
    public List<Order> queryOrdersForExport(OrderQueryRequest request, Integer limit) {
        log.debug("Querying orders for export with request: {}, limit: {}", request, limit);
        return orderRepository.queryOrdersForExport(request, limit);
    }
}
