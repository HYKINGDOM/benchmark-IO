use std::path::Path;

use xlsxwriter::*;

use crate::models::Order;

/// 写入 Excel 文件
pub fn write_excel(filepath: &Path, orders: &[Order]) -> Result<(), String> {
    let workbook = Workbook::new(filepath.to_str().unwrap())
        .map_err(|e| format!("Failed to create Excel file: {:?}", e))?;

    let mut worksheet = workbook.add_worksheet(Some("订单数据"))
        .map_err(|e| format!("Failed to add worksheet: {:?}", e))?;

    // 设置表头
    let headers = [
        "订单ID", "订单编号", "用户ID", "用户姓名", "用户手机", "用户身份证",
        "用户邮箱", "用户地址", "商品ID", "商品名称", "商品分类", "商品单价",
        "数量", "订单总额", "优惠金额", "实付金额", "订单状态", "支付方式",
        "支付时间", "订单来源", "收货地址", "收货人", "收货电话", "物流单号",
        "发货时间", "完成时间", "备注", "创建时间", "更新时间",
    ];

    // 创建表头格式
    let header_format = workbook.add_format()
        .set_font_name("微软雅黑")
        .set_font_size(11)
        .set_bold()
        .set_background_color(FormatColor::LightBlue)
        .set_border(FormatBorder::Thin);

    // 写入表头
    for (col, header) in headers.iter().enumerate() {
        worksheet.write_string(0, col as u16, header, Some(&header_format))
            .map_err(|e| format!("Failed to write header: {:?}", e))?;
    }

    // 创建数据格式
    let data_format = workbook.add_format()
        .set_font_name("微软雅黑")
        .set_font_size(10)
        .set_border(FormatBorder::Thin);

    // 写入数据行
    for (row_idx, order) in orders.iter().enumerate() {
        let row = (row_idx + 1) as u32;

        write_cell(&mut worksheet, row, 0, &order.order_id.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 1, &order.order_no, &data_format)?;
        write_cell(&mut worksheet, row, 2, &order.user_id.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 3, &order.user_name, &data_format)?;
        write_cell(&mut worksheet, row, 4, &order.user_phone, &data_format)?;
        write_cell(&mut worksheet, row, 5, &order.user_id_card, &data_format)?;
        write_cell(&mut worksheet, row, 6, &order.user_email, &data_format)?;
        write_cell(&mut worksheet, row, 7, &order.user_address, &data_format)?;
        write_cell(&mut worksheet, row, 8, &order.product_id.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 9, &order.product_name, &data_format)?;
        write_cell(&mut worksheet, row, 10, &order.product_category, &data_format)?;
        write_cell(&mut worksheet, row, 11, &order.product_price.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 12, &order.quantity.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 13, &order.total_amount.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 14, &order.discount_amount.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 15, &order.pay_amount.to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 16, &order.order_status, &data_format)?;
        write_cell(&mut worksheet, row, 17, &order.payment_method, &data_format)?;
        write_cell(&mut worksheet, row, 18, &format_optional_datetime(&order.payment_time), &data_format)?;
        write_cell(&mut worksheet, row, 19, &order.order_source, &data_format)?;
        write_cell(&mut worksheet, row, 20, &order.shipping_address, &data_format)?;
        write_cell(&mut worksheet, row, 21, &order.receiver_name, &data_format)?;
        write_cell(&mut worksheet, row, 22, &order.receiver_phone, &data_format)?;
        write_cell(&mut worksheet, row, 23, &format_optional_string(&order.logistics_no), &data_format)?;
        write_cell(&mut worksheet, row, 24, &format_optional_datetime(&order.delivery_time), &data_format)?;
        write_cell(&mut worksheet, row, 25, &format_optional_datetime(&order.complete_time), &data_format)?;
        write_cell(&mut worksheet, row, 26, &format_optional_string(&order.remark), &data_format)?;
        write_cell(&mut worksheet, row, 27, &order.created_at.format("%Y-%m-%d %H:%M:%S").to_string(), &data_format)?;
        write_cell(&mut worksheet, row, 28, &order.updated_at.format("%Y-%m-%d %H:%M:%S").to_string(), &data_format)?;
    }

    // 自动调整列宽
    for col in 0..headers.len() {
        worksheet.set_column(col as u16, col as u16, 15.0, None)
            .map_err(|e| format!("Failed to set column width: {:?}", e))?;
    }

    // 冻结首行
    worksheet.freeze_panes(1, 0)
        .map_err(|e| format!("Failed to freeze panes: {:?}", e))?;

    workbook.close()
        .map_err(|e| format!("Failed to close workbook: {:?}", e))?;

    Ok(())
}

/// 写入单元格
fn write_cell(
    worksheet: &mut Worksheet,
    row: u32,
    col: u16,
    value: &str,
    format: &Format,
) -> Result<(), String> {
    worksheet.write_string(row, col, value, Some(format))
        .map_err(|e| format!("Failed to write cell: {:?}", e))
}

/// 格式化可选时间
fn format_optional_datetime(dt: &Option<chrono::NaiveDateTime>) -> String {
    match dt {
        Some(t) => t.format("%Y-%m-%d %H:%M:%S").to_string(),
        None => String::new(),
    }
}

/// 格式化可选字符串
fn format_optional_string(s: &Option<String>) -> String {
    match s {
        Some(v) => v.clone(),
        None => String::new(),
    }
}
