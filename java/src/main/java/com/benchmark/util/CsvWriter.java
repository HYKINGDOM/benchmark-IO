package com.benchmark.util;

import com.benchmark.model.Order;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.time.format.DateTimeFormatter;

/**
 * CSV Writer Utility
 *
 * @author Benchmark Team
 */
public class CsvWriter {

    private static final String[] HEADERS = {
            "订单ID", "订单编号", "用户ID", "用户姓名", "用户手机号", "用户身份证号",
            "用户邮箱", "用户地址", "商品ID", "商品名称", "商品分类", "商品单价",
            "购买数量", "订单总金额", "优惠金额", "实付金额", "订单状态", "支付方式",
            "支付时间", "订单来源", "收货地址", "收货人姓名", "收货人手机号", "物流单号",
            "发货时间", "完成时间", "备注", "创建时间", "更新时间", "是否删除"
    };

    private static final DateTimeFormatter DATE_TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final CSVPrinter csvPrinter;

    public CsvWriter(OutputStream outputStream) throws IOException {
        OutputStreamWriter writer = new OutputStreamWriter(outputStream, StandardCharsets.UTF_8);
        // Add BOM for Excel compatibility
        writer.write('\ufeff');
        this.csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);
    }

    /**
     * Write CSV header
     */
    public void writeHeader() throws IOException {
        csvPrinter.printRecord((Object[]) HEADERS);
    }

    /**
     * Write order row
     */
    public void writeRow(Order order) throws IOException {
        csvPrinter.printRecord(
                order.getOrderId(),
                order.getOrderNo(),
                order.getUserId(),
                order.getUserName(),
                order.getUserPhone(),
                order.getUserIdCard(),
                order.getUserEmail(),
                order.getUserAddress(),
                order.getProductId(),
                order.getProductName(),
                order.getProductCategory(),
                formatBigDecimal(order.getProductPrice()),
                order.getQuantity(),
                formatBigDecimal(order.getTotalAmount()),
                formatBigDecimal(order.getDiscountAmount()),
                formatBigDecimal(order.getPayAmount()),
                order.getOrderStatus(),
                order.getPaymentMethod(),
                formatDateTime(order.getPaymentTime()),
                order.getOrderSource(),
                order.getShippingAddress(),
                order.getReceiverName(),
                order.getReceiverPhone(),
                order.getLogisticsNo(),
                formatDateTime(order.getDeliveryTime()),
                formatDateTime(order.getCompleteTime()),
                order.getRemark(),
                formatDateTime(order.getCreatedAt()),
                formatDateTime(order.getUpdatedAt()),
                order.getIsDeleted()
        );
    }

    /**
     * Flush buffer
     */
    public void flush() throws IOException {
        csvPrinter.flush();
    }

    /**
     * Close writer
     */
    public void close() throws IOException {
        csvPrinter.close();
    }

    /**
     * Format BigDecimal
     */
    private String formatBigDecimal(BigDecimal value) {
        return value != null ? value.toString() : "";
    }

    /**
     * Format LocalDateTime
     */
    private String formatDateTime(java.time.LocalDateTime dateTime) {
        return dateTime != null ? dateTime.format(DATE_TIME_FORMATTER) : "";
    }
}
