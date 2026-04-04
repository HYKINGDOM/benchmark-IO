use std::fs::File;
use std::io::Write;
use std::path::Path;

use crate::models::Order;

/// 写入 CSV 文件
pub fn write_csv(filepath: &Path, orders: &[Order]) -> Result<(), String> {
    let mut file = File::create(filepath)
        .map_err(|e| format!("Failed to create CSV file: {}", e))?;

    // 写入 BOM (UTF-8)
    file.write_all(b"\xEF\xBB\xBF")
        .map_err(|e| format!("Failed to write BOM: {}", e))?;

    // 写入表头
    let headers = [
        "订单ID", "订单编号", "用户ID", "用户姓名", "用户手机", "用户身份证",
        "用户邮箱", "用户地址", "商品ID", "商品名称", "商品分类", "商品单价",
        "数量", "订单总额", "优惠金额", "实付金额", "订单状态", "支付方式",
        "支付时间", "订单来源", "收货地址", "收货人", "收货电话", "物流单号",
        "发货时间", "完成时间", "备注", "创建时间", "更新时间",
    ];

    let header_line = headers.join(",");
    writeln!(file, "{}", header_line)
        .map_err(|e| format!("Failed to write headers: {}", e))?;

    // 写入数据行
    for order in orders {
        let row = format!(
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            order.order_id,
            escape_csv_field(&order.order_no),
            order.user_id,
            escape_csv_field(order.user_name.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.user_phone.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.user_id_card.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.user_email.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.user_address.as_ref().unwrap_or(&String::new())),
            order.product_id,
            escape_csv_field(order.product_name.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.product_category.as_ref().unwrap_or(&String::new())),
            order.product_price,
            order.quantity,
            order.total_amount,
            order.discount_amount.as_ref().map(|d| d.to_string()).unwrap_or_else(|| "0".to_string()),
            order.pay_amount,
            escape_csv_field(&order.order_status),
            escape_csv_field(order.payment_method.as_ref().unwrap_or(&String::new())),
            format_optional_datetime(&order.payment_time),
            escape_csv_field(order.order_source.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.shipping_address.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.receiver_name.as_ref().unwrap_or(&String::new())),
            escape_csv_field(order.receiver_phone.as_ref().unwrap_or(&String::new())),
            format_optional_string(&order.logistics_no),
            format_optional_datetime(&order.delivery_time),
            format_optional_datetime(&order.complete_time),
            format_optional_string(&order.remark),
            order.created_at.format("%Y-%m-%d %H:%M:%S"),
            order.updated_at.format("%Y-%m-%d %H:%M:%S"),
        );

        writeln!(file, "{}", row)
            .map_err(|e| format!("Failed to write row: {}", e))?;
    }

    file.flush()
        .map_err(|e| format!("Failed to flush file: {}", e))?;

    Ok(())
}

/// CSV 字段转义
fn escape_csv_field(field: &str) -> String {
    if field.contains(',') || field.contains('"') || field.contains('\n') {
        format!("\"{}\"", field.replace('"', "\"\""))
    } else {
        field.to_string()
    }
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
        Some(v) => escape_csv_field(v),
        None => String::new(),
    }
}
