package util

import (
	"benchmark-api/internal/model"
	"bytes"
	"encoding/csv"
	"fmt"
	"io"
	"strconv"
	"time"
)

type CSVWriter struct {
	buffer   *bytes.Buffer
	writer   *csv.Writer
	headers  []string
	hasWrite bool
}

func NewCSVWriter() *CSVWriter {
	buffer := &bytes.Buffer{}
	writer := csv.NewWriter(buffer)
	
	headers := []string{
		"订单ID", "订单号", "用户ID", "用户姓名", "用户手机", "用户身份证",
		"用户邮箱", "用户地址", "商品ID", "商品名称", "商品分类", "商品单价",
		"数量", "订单总金额", "优惠金额", "实付金额", "订单状态", "支付方式",
		"支付时间", "订单来源", "收货地址", "收货人", "收货人电话", "物流单号",
		"发货时间", "完成时间", "备注", "创建时间", "更新时间",
	}

	return &CSVWriter{
		buffer:  buffer,
		writer:  writer,
		headers: headers,
	}
}

func (w *CSVWriter) WriteHeader() error {
	if err := w.writer.Write(w.headers); err != nil {
		return err
	}
	w.hasWrite = true
	return nil
}

func (w *CSVWriter) WriteOrders(orders []model.Order) error {
	if !w.hasWrite {
		if err := w.WriteHeader(); err != nil {
			return err
		}
	}

	for _, order := range orders {
		record := []string{
			fmt.Sprintf("%d", order.OrderID),
			order.OrderNo,
			fmt.Sprintf("%d", order.UserID),
			order.UserName,
			order.UserPhone,
			order.UserIDCard,
			order.UserEmail,
			order.UserAddress,
			fmt.Sprintf("%d", order.ProductID),
			order.ProductName,
			order.ProductCategory,
			fmt.Sprintf("%.2f", order.ProductPrice),
			strconv.Itoa(order.Quantity),
			fmt.Sprintf("%.2f", order.TotalAmount),
			fmt.Sprintf("%.2f", order.DiscountAmount),
			fmt.Sprintf("%.2f", order.PayAmount),
			order.OrderStatus,
			order.PaymentMethod,
			formatTime(order.PaymentTime),
			order.OrderSource,
			order.ShippingAddress,
			order.ReceiverName,
			order.ReceiverPhone,
			order.LogisticsNo,
			formatTime(order.DeliveryTime),
			formatTime(order.CompleteTime),
			order.Remark,
			order.CreatedAt.Format("2006-01-02 15:04:05"),
			order.UpdatedAt.Format("2006-01-02 15:04:05"),
		}

		if err := w.writer.Write(record); err != nil {
			return err
		}
	}

	w.writer.Flush()
	return w.writer.Error()
}

func (w *CSVWriter) Flush() {
	w.writer.Flush()
}

func (w *CSVWriter) Bytes() []byte {
	w.writer.Flush()
	return w.buffer.Bytes()
}

func (w *CSVWriter) WriteTo(writer io.Writer) (int64, error) {
	w.writer.Flush()
	return w.buffer.WriteTo(writer)
}

func formatTime(t *time.Time) string {
	if t == nil {
		return ""
	}
	return t.Format("2006-01-02 15:04:05")
}
