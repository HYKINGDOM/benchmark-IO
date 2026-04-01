package util

import (
	"benchmark-api/internal/model"
	"fmt"
	"strconv"
	"time"

	"github.com/xuri/excelize/v2"
)

type ExcelWriter struct {
	file     *excelize.File
	sheet    string
	rowNum   int
	hasWrite bool
}

func NewExcelWriter() *ExcelWriter {
	f := excelize.NewFile()
	sheet := "Sheet1"
	
	return &ExcelWriter{
		file:   f,
		sheet:  sheet,
		rowNum: 1,
	}
}

func (w *ExcelWriter) WriteHeader() error {
	headers := []string{
		"订单ID", "订单号", "用户ID", "用户姓名", "用户手机", "用户身份证",
		"用户邮箱", "用户地址", "商品ID", "商品名称", "商品分类", "商品单价",
		"数量", "订单总金额", "优惠金额", "实付金额", "订单状态", "支付方式",
		"支付时间", "订单来源", "收货地址", "收货人", "收货人电话", "物流单号",
		"发货时间", "完成时间", "备注", "创建时间", "更新时间",
	}

	for i, header := range headers {
		cell, err := excelize.CoordinatesToCellName(i+1, w.rowNum)
		if err != nil {
			return err
		}
		if err := w.file.SetCellValue(w.sheet, cell, header); err != nil {
			return err
		}
	}

	// 设置表头样式
	style, err := w.file.NewStyle(&excelize.Style{
		Font: &excelize.Font{Bold: true},
		Fill: excelize.Fill{Type: "pattern", Color: []string{"#CCCCCC"}, Pattern: 1},
	})
	if err == nil {
		endCol, _ := excelize.CoordinatesToCellName(len(headers), w.rowNum)
		w.file.SetCellStyle(w.sheet, "A1", endCol, style)
	}

	w.rowNum++
	w.hasWrite = true
	return nil
}

func (w *ExcelWriter) WriteOrders(orders []model.Order) error {
	if !w.hasWrite {
		if err := w.WriteHeader(); err != nil {
			return err
		}
	}

	for _, order := range orders {
		values := []interface{}{
			order.OrderID,
			order.OrderNo,
			order.UserID,
			order.UserName,
			order.UserPhone,
			order.UserIDCard,
			order.UserEmail,
			order.UserAddress,
			order.ProductID,
			order.ProductName,
			order.ProductCategory,
			order.ProductPrice,
			order.Quantity,
			order.TotalAmount,
			order.DiscountAmount,
			order.PayAmount,
			order.OrderStatus,
			order.PaymentMethod,
			formatTimeExcel(order.PaymentTime),
			order.OrderSource,
			order.ShippingAddress,
			order.ReceiverName,
			order.ReceiverPhone,
			order.LogisticsNo,
			formatTimeExcel(order.DeliveryTime),
			formatTimeExcel(order.CompleteTime),
			order.Remark,
			order.CreatedAt.Format("2006-01-02 15:04:05"),
			order.UpdatedAt.Format("2006-01-02 15:04:05"),
		}

		for i, value := range values {
			cell, err := excelize.CoordinatesToCellName(i+1, w.rowNum)
			if err != nil {
				return err
			}
			if err := w.file.SetCellValue(w.sheet, cell, value); err != nil {
				return err
			}
		}

		w.rowNum++
	}

	return nil
}

func (w *ExcelWriter) Save() ([]byte, error) {
	// 自动调整列宽
	for i := 1; i <= 29; i++ {
		col, _ := excelize.ColumnNumberToName(i)
		w.file.SetColWidth(w.sheet, col, col, 15)
	}

	buffer, err := w.file.WriteToBuffer()
	if err != nil {
		return nil, err
	}
	return buffer.Bytes(), nil
}

func (w *ExcelWriter) Close() error {
	return w.file.Close()
}

func formatTimeExcel(t *time.Time) string {
	if t == nil {
		return ""
	}
	return t.Format("2006-01-02 15:04:05")
}

// StreamExcelWriter 用于流式写入 Excel
type StreamExcelWriter struct {
	file   *excelize.File
	sheet  string
	rowNum int
}

func NewStreamExcelWriter() *StreamExcelWriter {
	f := excelize.NewFile()
	return &StreamExcelWriter{
		file:   f,
		sheet:  "Sheet1",
		rowNum: 1,
	}
}

func (w *StreamExcelWriter) WriteHeader() error {
	headers := []string{
		"订单ID", "订单号", "用户ID", "用户姓名", "用户手机", "用户身份证",
		"用户邮箱", "用户地址", "商品ID", "商品名称", "商品分类", "商品单价",
		"数量", "订单总金额", "优惠金额", "实付金额", "订单状态", "支付方式",
		"支付时间", "订单来源", "收货地址", "收货人", "收货人电话", "物流单号",
		"发货时间", "完成时间", "备注", "创建时间", "更新时间",
	}

	for i, header := range headers {
		cell := string(rune('A'+i)) + strconv.Itoa(w.rowNum)
		if err := w.file.SetCellValue(w.sheet, cell, header); err != nil {
			return err
		}
	}

	w.rowNum++
	return nil
}

func (w *StreamExcelWriter) WriteRow(order *model.Order) error {
	values := []interface{}{
		order.OrderID,
		order.OrderNo,
		order.UserID,
		order.UserName,
		order.UserPhone,
		order.UserIDCard,
		order.UserEmail,
		order.UserAddress,
		order.ProductID,
		order.ProductName,
		order.ProductCategory,
		order.ProductPrice,
		order.Quantity,
		order.TotalAmount,
		order.DiscountAmount,
		order.PayAmount,
		order.OrderStatus,
		order.PaymentMethod,
		formatTimeExcel(order.PaymentTime),
		order.OrderSource,
		order.ShippingAddress,
		order.ReceiverName,
		order.ReceiverPhone,
		order.LogisticsNo,
		formatTimeExcel(order.DeliveryTime),
		formatTimeExcel(order.CompleteTime),
		order.Remark,
		order.CreatedAt.Format("2006-01-02 15:04:05"),
		order.UpdatedAt.Format("2006-01-02 15:04:05"),
	}

	for i, value := range values {
		cell := string(rune('A'+i)) + strconv.Itoa(w.rowNum)
		if err := w.file.SetCellValue(w.sheet, cell, value); err != nil {
			return err
		}
	}

	w.rowNum++
	return nil
}

func (w *StreamExcelWriter) Save() ([]byte, error) {
	buffer, err := w.file.WriteToBuffer()
	if err != nil {
		return nil, err
	}
	return buffer.Bytes(), nil
}

func (w *StreamExcelWriter) Close() error {
	return w.file.Close()
}
