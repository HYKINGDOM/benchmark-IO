package com.benchmark.util;

import com.benchmark.model.Order;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.streaming.SXSSFRow;
import org.apache.poi.xssf.streaming.SXSSFSheet;
import org.apache.poi.xssf.streaming.SXSSFWorkbook;

import java.io.IOException;
import java.io.OutputStream;
import java.math.BigDecimal;
import java.time.format.DateTimeFormatter;

/**
 * Excel Writer Utility using Apache POI SXSSF (Streaming)
 *
 * @author Benchmark Team
 */
public class ExcelWriter {

    private static final String[] HEADERS = {
            "订单ID", "订单编号", "用户ID", "用户姓名", "用户手机号", "用户身份证号",
            "用户邮箱", "用户地址", "商品ID", "商品名称", "商品分类", "商品单价",
            "购买数量", "订单总金额", "优惠金额", "实付金额", "订单状态", "支付方式",
            "支付时间", "订单来源", "收货地址", "收货人姓名", "收货人手机号", "物流单号",
            "发货时间", "完成时间", "备注", "创建时间", "更新时间", "是否删除"
    };

    private static final DateTimeFormatter DATE_TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final SXSSFWorkbook workbook;
    private final SXSSFSheet sheet;
    private final CellStyle dateStyle;
    private int currentRow = 0;

    public ExcelWriter(OutputStream outputStream) {
        // Create streaming workbook with 100 rows in memory
        this.workbook = new SXSSFWorkbook(100);
        this.sheet = workbook.createSheet("订单数据");

        // Create date style
        CreationHelper createHelper = workbook.getCreationHelper();
        this.dateStyle = workbook.createCellStyle();
        this.dateStyle.setDataFormat(createHelper.createDataFormat().getFormat("yyyy-mm-dd hh:mm:ss"));

        // Set column widths
        for (int i = 0; i < HEADERS.length; i++) {
            sheet.trackColumnForAutoSizing(i);
        }
    }

    /**
     * Write Excel header
     */
    public void writeHeader() {
        SXSSFRow row = sheet.createRow(currentRow++);
        CellStyle headerStyle = createHeaderStyle();

        for (int i = 0; i < HEADERS.length; i++) {
            Cell cell = row.createCell(i);
            cell.setCellValue(HEADERS[i]);
            cell.setCellStyle(headerStyle);
        }
    }

    /**
     * Write order row
     */
    public void writeRow(Order order) {
        SXSSFRow row = sheet.createRow(currentRow++);

        int col = 0;
        createCell(row, col++, order.getOrderId());
        createCell(row, col++, order.getOrderNo());
        createCell(row, col++, order.getUserId());
        createCell(row, col++, order.getUserName());
        createCell(row, col++, order.getUserPhone());
        createCell(row, col++, order.getUserIdCard());
        createCell(row, col++, order.getUserEmail());
        createCell(row, col++, order.getUserAddress());
        createCell(row, col++, order.getProductId());
        createCell(row, col++, order.getProductName());
        createCell(row, col++, order.getProductCategory());
        createCell(row, col++, order.getProductPrice());
        createCell(row, col++, order.getQuantity());
        createCell(row, col++, order.getTotalAmount());
        createCell(row, col++, order.getDiscountAmount());
        createCell(row, col++, order.getPayAmount());
        createCell(row, col++, order.getOrderStatus());
        createCell(row, col++, order.getPaymentMethod());
        createCell(row, col++, formatDateTime(order.getPaymentTime()));
        createCell(row, col++, order.getOrderSource());
        createCell(row, col++, order.getShippingAddress());
        createCell(row, col++, order.getReceiverName());
        createCell(row, col++, order.getReceiverPhone());
        createCell(row, col++, order.getLogisticsNo());
        createCell(row, col++, formatDateTime(order.getDeliveryTime()));
        createCell(row, col++, formatDateTime(order.getCompleteTime()));
        createCell(row, col++, order.getRemark());
        createCell(row, col++, formatDateTime(order.getCreatedAt()));
        createCell(row, col++, formatDateTime(order.getUpdatedAt()));
        createCell(row, col++, order.getIsDeleted());
    }

    /**
     * Flush buffer
     */
    public void flush() throws IOException {
        // SXSSFWorkbook automatically flushes rows to disk
    }

    /**
     * Close writer and write to output stream
     */
    public void close() throws IOException {
        // Auto-size columns (only for rows in memory)
        for (int i = 0; i < HEADERS.length; i++) {
            try {
                sheet.autoSizeColumn(i);
            } catch (Exception e) {
                // Ignore auto-size errors for large datasets
            }
        }

        // Write to output stream (SXSSF uses different approach than XSSF)
        // The workbook should be written via workbook.write(OutputStream) by the caller
        workbook.dispose();
        workbook.close();
    }

    /**
     * Create cell with long value
     */
    private void createCell(SXSSFRow row, int col, Long value) {
        Cell cell = row.createCell(col);
        if (value != null) {
            cell.setCellValue(value);
        }
    }

    /**
     * Create cell with string value
     */
    private void createCell(SXSSFRow row, int col, String value) {
        Cell cell = row.createCell(col);
        if (value != null) {
            cell.setCellValue(value);
        }
    }

    /**
     * Create cell with integer value
     */
    private void createCell(SXSSFRow row, int col, Integer value) {
        Cell cell = row.createCell(col);
        if (value != null) {
            cell.setCellValue(value);
        }
    }

    /**
     * Create cell with BigDecimal value
     */
    private void createCell(SXSSFRow row, int col, BigDecimal value) {
        Cell cell = row.createCell(col);
        if (value != null) {
            cell.setCellValue(value.doubleValue());
        }
    }

    /**
     * Create header style
     */
    private CellStyle createHeaderStyle() {
        CellStyle style = workbook.createCellStyle();
        style.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
        style.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        style.setAlignment(HorizontalAlignment.CENTER);
        style.setVerticalAlignment(VerticalAlignment.CENTER);

        Font font = workbook.createFont();
        font.setBold(true);
        style.setFont(font);

        return style;
    }

    /**
     * Format LocalDateTime
     */
    private String formatDateTime(java.time.LocalDateTime dateTime) {
        return dateTime != null ? dateTime.format(DATE_TIME_FORMATTER) : "";
    }
}
