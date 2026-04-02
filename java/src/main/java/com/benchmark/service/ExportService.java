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
import org.springframework.stereotype.Service;

import jakarta.servlet.http.HttpServletResponse;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;

/**
 * Export Service
 *
 * @author Benchmark Team
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ExportService {

    private final OrderRepository orderRepository;
    private final AsyncTaskService asyncTaskService;

    @Value("${export.temp-dir}")
    private String tempDir;

    @Value("${export.max-rows}")
    private Integer maxRows;

    /**
     * Sync export - return file stream directly
     */
    public void syncExport(ExportRequest request, HttpServletResponse response) throws IOException {
        log.info("Starting sync export with format: {}", request.getFormat());

        OrderQueryRequest queryRequest = request.getConditions() != null
                ? request.getConditions()
                : new OrderQueryRequest();

        Integer limit = request.getLimit() != null ? Math.min(request.getLimit(), maxRows) : maxRows;

        // Set response headers
        String filename = generateFilename(request.getFormat());
        setResponseHeaders(response, filename, request.getFormat());

        // Stream data directly to response
        try (OutputStream outputStream = response.getOutputStream()) {
            if ("xlsx".equals(request.getFormat())) {
                exportToExcel(queryRequest, limit, outputStream);
            } else {
                exportToCsv(queryRequest, limit, outputStream);
            }
        }

        log.info("Sync export completed");
    }

    /**
     * Stream export - SSE streaming
     */
    public void streamExport(ExportRequest request, HttpServletResponse response) throws IOException {
        log.info("Starting stream export with format: {}", request.getFormat());

        OrderQueryRequest queryRequest = request.getConditions() != null
                ? request.getConditions()
                : new OrderQueryRequest();

        Integer limit = request.getLimit() != null ? Math.min(request.getLimit(), maxRows) : maxRows;

        // Set SSE headers
        response.setContentType("text/event-stream");
        response.setCharacterEncoding("UTF-8");
        response.setHeader("Cache-Control", "no-cache");
        response.setHeader("X-Accel-Buffering", "no");

        PrintWriter writer = response.getWriter();

        try {
            // Send start event
            writer.write("event: start\ndata: {\"message\":\"Export started\"}\n\n");
            writer.flush();

            // Stream data
            try (Cursor<?> cursor = orderRepository.streamOrders(queryRequest, limit)) {
                long count = 0;
                StringBuilder buffer = new StringBuilder();

                for (Record record : cursor) {
                    Order order = mapRecordToOrder(record);
                    String line = formatOrderLine(order, request.getFormat());
                    buffer.append(line).append("\n");

                    count++;

                    // Send progress every 1000 records
                    if (count % 1000 == 0) {
                        writer.write(String.format("event: progress\ndata: {\"count\":%d}\n\n", count));
                        writer.flush();
                    }

                    // Send data in batches
                    if (buffer.length() > 10000) {
                        writer.write("event: data\ndata: " + escapeJson(buffer.toString()) + "\n\n");
                        writer.flush();
                        buffer.setLength(0);
                    }
                }

                // Send remaining data
                if (buffer.length() > 0) {
                    writer.write("event: data\ndata: " + escapeJson(buffer.toString()) + "\n\n");
                    writer.flush();
                }

                // Send completion event
                writer.write(String.format("event: completed\ndata: {\"count\":%d}\n\n", count));
                writer.flush();
            }
        } catch (Exception e) {
            log.error("Stream export failed", e);
            writer.write(String.format("event: error\ndata: {\"error\":\"%s\"}\n\n",
                    escapeJson(e.getMessage())));
            writer.flush();
        }

        log.info("Stream export completed");
    }

    /**
     * Export to CSV
     */
    private void exportToCsv(OrderQueryRequest request, Integer limit, OutputStream outputStream) throws IOException {
        try (Cursor<?> cursor = orderRepository.streamOrders(request, limit)) {
            CsvWriter csvWriter = new CsvWriter(outputStream);
            csvWriter.writeHeader();

            long count = 0;
            for (Record record : cursor) {
                Order order = mapRecordToOrder(record);
                csvWriter.writeRow(order);
                count++;
            }

            log.info("Exported {} records to CSV", count);
        }
    }

    /**
     * Export to Excel
     */
    private void exportToExcel(OrderQueryRequest request, Integer limit, OutputStream outputStream) throws IOException {
        try (Cursor<?> cursor = orderRepository.streamOrders(request, limit)) {
            ExcelWriter excelWriter = new ExcelWriter(outputStream);
            excelWriter.writeHeader();

            long count = 0;
            for (Record record : cursor) {
                Order order = mapRecordToOrder(record);
                excelWriter.writeRow(order);
                count++;

                // Flush periodically to avoid memory issues
                if (count % 10000 == 0) {
                    excelWriter.flush();
                }
            }

            excelWriter.close();
            log.info("Exported {} records to Excel", count);
        }
    }

    /**
     * Generate export filename
     */
    private String generateFilename(String format) {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        return String.format("orders_export_%s.%s", timestamp, format);
    }

    /**
     * Set response headers for file download
     */
    private void setResponseHeaders(HttpServletResponse response, String filename, String format) {
        response.setContentType("xlsx".equals(format)
                ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                : "text/csv");
        response.setHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");
        response.setHeader("Cache-Control", "no-cache");
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

    /**
     * Format order as CSV or Excel line
     */
    private String formatOrderLine(Order order, String format) {
        if ("xlsx".equals(format)) {
            return String.join(",",
                    String.valueOf(order.getOrderId()),
                    order.getOrderNo(),
                    String.valueOf(order.getUserId()),
                    order.getUserName(),
                    order.getUserPhone(),
                    order.getUserIdCard(),
                    order.getUserEmail(),
                    order.getUserAddress(),
                    String.valueOf(order.getProductId()),
                    order.getProductName(),
                    order.getProductCategory(),
                    String.valueOf(order.getProductPrice()),
                    String.valueOf(order.getQuantity()),
                    String.valueOf(order.getTotalAmount()),
                    String.valueOf(order.getDiscountAmount()),
                    String.valueOf(order.getPayAmount()),
                    order.getOrderStatus(),
                    order.getPaymentMethod(),
                    order.getPaymentTime() != null ? order.getPaymentTime().toString() : "",
                    order.getOrderSource(),
                    order.getShippingAddress(),
                    order.getReceiverName(),
                    order.getReceiverPhone(),
                    order.getLogisticsNo(),
                    order.getDeliveryTime() != null ? order.getDeliveryTime().toString() : "",
                    order.getCompleteTime() != null ? order.getCompleteTime().toString() : "",
                    order.getRemark(),
                    order.getCreatedAt() != null ? order.getCreatedAt().toString() : "",
                    order.getUpdatedAt() != null ? order.getUpdatedAt().toString() : "",
                    String.valueOf(order.getIsDeleted())
            );
        } else {
            return String.join(",",
                    String.valueOf(order.getOrderId()),
                    order.getOrderNo(),
                    String.valueOf(order.getUserId()),
                    order.getUserName(),
                    order.getUserPhone(),
                    order.getUserIdCard(),
                    order.getUserEmail(),
                    order.getUserAddress(),
                    String.valueOf(order.getProductId()),
                    order.getProductName(),
                    order.getProductCategory(),
                    String.valueOf(order.getProductPrice()),
                    String.valueOf(order.getQuantity()),
                    String.valueOf(order.getTotalAmount()),
                    String.valueOf(order.getDiscountAmount()),
                    String.valueOf(order.getPayAmount()),
                    order.getOrderStatus(),
                    order.getPaymentMethod(),
                    order.getPaymentTime() != null ? order.getPaymentTime().toString() : "",
                    order.getOrderSource(),
                    order.getShippingAddress(),
                    order.getReceiverName(),
                    order.getReceiverPhone(),
                    order.getLogisticsNo(),
                    order.getDeliveryTime() != null ? order.getDeliveryTime().toString() : "",
                    order.getCompleteTime() != null ? order.getCompleteTime().toString() : "",
                    order.getRemark(),
                    order.getCreatedAt() != null ? order.getCreatedAt().toString() : "",
                    order.getUpdatedAt() != null ? order.getUpdatedAt().toString() : "",
                    String.valueOf(order.getIsDeleted())
            );
        }
    }

    /**
     * Escape JSON string
     */
    private String escapeJson(String str) {
        if (str == null) {
            return "";
        }
        return str.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }
}
