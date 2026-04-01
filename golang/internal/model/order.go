package model

import (
	"time"
)

type Order struct {
	OrderID         int64          `gorm:"primaryKey;autoIncrement" json:"order_id"`
	OrderNo         string         `gorm:"type:varchar(32);uniqueIndex;not null" json:"order_no"`
	UserID          int64          `gorm:"not null;index" json:"user_id"`
	UserName        string         `gorm:"type:varchar(64)" json:"user_name"`
	UserPhone       string         `gorm:"type:varchar(11)" json:"user_phone"`
	UserIDCard      string         `gorm:"type:varchar(18)" json:"user_id_card"`
	UserEmail       string         `gorm:"type:varchar(128)" json:"user_email"`
	UserAddress     string         `gorm:"type:varchar(256)" json:"user_address"`
	ProductID       int64          `gorm:"not null" json:"product_id"`
	ProductName     string         `gorm:"type:varchar(128)" json:"product_name"`
	ProductCategory string         `gorm:"type:varchar(64)" json:"product_category"`
	ProductPrice    float64        `gorm:"type:decimal(10,2);not null" json:"product_price"`
	Quantity        int            `gorm:"not null" json:"quantity"`
	TotalAmount     float64        `gorm:"type:decimal(12,2);not null;index" json:"total_amount"`
	DiscountAmount  float64        `gorm:"type:decimal(12,2);default:0" json:"discount_amount"`
	PayAmount       float64        `gorm:"type:decimal(12,2);not null" json:"pay_amount"`
	OrderStatus     string         `gorm:"type:varchar(16);not null;default:'pending';index" json:"order_status"`
	PaymentMethod   string         `gorm:"type:varchar(16)" json:"payment_method"`
	PaymentTime     *time.Time     `json:"payment_time"`
	OrderSource     string         `gorm:"type:varchar(32)" json:"order_source"`
	ShippingAddress string         `gorm:"type:varchar(512)" json:"shipping_address"`
	ReceiverName    string         `gorm:"type:varchar(64)" json:"receiver_name"`
	ReceiverPhone   string         `gorm:"type:varchar(11)" json:"receiver_phone"`
	LogisticsNo     string         `gorm:"type:varchar(32)" json:"logistics_no"`
	DeliveryTime    *time.Time     `json:"delivery_time"`
	CompleteTime    *time.Time     `json:"complete_time"`
	Remark          string         `gorm:"type:varchar(512)" json:"remark"`
	CreatedAt       time.Time      `gorm:"not null;default:CURRENT_TIMESTAMP;index" json:"created_at"`
	UpdatedAt       time.Time      `gorm:"not null;default:CURRENT_TIMESTAMP" json:"updated_at"`
	IsDeleted       int16          `gorm:"not null;default:0" json:"is_deleted"`
}

func (Order) TableName() string {
	return "orders"
}

type OrderQueryParams struct {
	Page       int        `form:"page" json:"page"`
	PageSize   int        `form:"page_size" json:"page_size"`
	StartTime  *time.Time `form:"start_time" json:"start_time" time_format:"2006-01-02T15:04:05Z07:00"`
	EndTime    *time.Time `form:"end_time" json:"end_time" time_format:"2006-01-02T15:04:05Z07:00"`
	OrderNo    string     `form:"order_no" json:"order_no"`
	UserID     *int64     `form:"user_id" json:"user_id"`
	Status     string     `form:"status" json:"status"`
	MinAmount  *float64   `form:"min_amount" json:"min_amount"`
	MaxAmount  *float64   `form:"max_amount" json:"max_amount"`
	SortBy     string     `form:"sort_by" json:"sort_by"`
	SortOrder  string     `form:"sort_order" json:"sort_order"`
}

func (p *OrderQueryParams) GetOffset() int {
	if p.Page <= 0 {
		p.Page = 1
	}
	if p.PageSize <= 0 {
		p.PageSize = 20
	}
	if p.PageSize > 1000 {
		p.PageSize = 1000
	}
	return (p.Page - 1) * p.PageSize
}

func (p *OrderQueryParams) GetLimit() int {
	if p.PageSize <= 0 {
		p.PageSize = 20
	}
	if p.PageSize > 1000 {
		p.PageSize = 1000
	}
	return p.PageSize
}

type OrderListResponse struct {
	Total int64   `json:"total"`
	Page  int     `json:"page"`
	Size  int     `json:"size"`
	Items []Order `json:"items"`
}
