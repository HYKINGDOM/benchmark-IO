package repository

import (
	"benchmark-api/internal/model"
	"time"

	"gorm.io/gorm"
)

type OrderRepository struct {
	db *gorm.DB
}

func NewOrderRepository(db *gorm.DB) *OrderRepository {
	return &OrderRepository{db: db}
}

func (r *OrderRepository) FindByParams(params *model.OrderQueryParams) ([]model.Order, int64, error) {
	var orders []model.Order
	var total int64

	query := r.db.Model(&model.Order{}).Where("is_deleted = 0")

	// 应用过滤条件
	if params.StartTime != nil {
		query = query.Where("created_at >= ?", params.StartTime)
	}
	if params.EndTime != nil {
		query = query.Where("created_at <= ?", params.EndTime)
	}
	if params.OrderNo != "" {
		query = query.Where("order_no LIKE ?", "%"+params.OrderNo+"%")
	}
	if params.UserID != nil {
		query = query.Where("user_id = ?", *params.UserID)
	}
	if params.Status != "" {
		query = query.Where("order_status = ?", params.Status)
	}
	if params.MinAmount != nil {
		query = query.Where("total_amount >= ?", *params.MinAmount)
	}
	if params.MaxAmount != nil {
		query = query.Where("total_amount <= ?", *params.MaxAmount)
	}

	// 获取总数
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// 排序
	orderBy := "created_at"
	if params.SortBy != "" {
		orderBy = params.SortBy
	}
	orderDir := "DESC"
	if params.SortOrder != "" && params.SortOrder == "asc" {
		orderDir = "ASC"
	}
	query = query.Order(orderBy + " " + orderDir)

	// 分页
	offset := params.GetOffset()
	limit := params.GetLimit()

	if err := query.Offset(offset).Limit(limit).Find(&orders).Error; err != nil {
		return nil, 0, err
	}

	return orders, total, nil
}

func (r *OrderRepository) CountByParams(params *model.ExportRequest) (int64, error) {
	var total int64

	query := r.db.Model(&model.Order{}).Where("is_deleted = 0")

	if params.StartTime != nil {
		startTime, err := time.Parse(time.RFC3339, *params.StartTime)
		if err == nil {
			query = query.Where("created_at >= ?", startTime)
		}
	}
	if params.EndTime != nil {
		endTime, err := time.Parse(time.RFC3339, *params.EndTime)
		if err == nil {
			query = query.Where("created_at <= ?", endTime)
		}
	}
	if params.OrderNo != "" {
		query = query.Where("order_no LIKE ?", "%"+params.OrderNo+"%")
	}
	if params.UserID != nil {
		query = query.Where("user_id = ?", *params.UserID)
	}
	if params.Status != "" {
		query = query.Where("order_status = ?", params.Status)
	}
	if params.MinAmount != nil {
		query = query.Where("total_amount >= ?", *params.MinAmount)
	}
	if params.MaxAmount != nil {
		query = query.Where("total_amount <= ?", *params.MaxAmount)
	}

	if err := query.Count(&total).Error; err != nil {
		return 0, err
	}

	return total, nil
}

func (r *OrderRepository) FindByParamsStream(params *model.ExportRequest, chunkSize int, callback func([]model.Order) error) error {
	query := r.db.Model(&model.Order{}).Where("is_deleted = 0")

	if params.StartTime != nil {
		startTime, err := time.Parse(time.RFC3339, *params.StartTime)
		if err == nil {
			query = query.Where("created_at >= ?", startTime)
		}
	}
	if params.EndTime != nil {
		endTime, err := time.Parse(time.RFC3339, *params.EndTime)
		if err == nil {
			query = query.Where("created_at <= ?", endTime)
		}
	}
	if params.OrderNo != "" {
		query = query.Where("order_no LIKE ?", "%"+params.OrderNo+"%")
	}
	if params.UserID != nil {
		query = query.Where("user_id = ?", *params.UserID)
	}
	if params.Status != "" {
		query = query.Where("order_status = ?", params.Status)
	}
	if params.MinAmount != nil {
		query = query.Where("total_amount >= ?", *params.MinAmount)
	}
	if params.MaxAmount != nil {
		query = query.Where("total_amount <= ?", *params.MaxAmount)
	}

	query = query.Order("created_at DESC")

	rows, err := query.Rows()
	if err != nil {
		return err
	}
	defer rows.Close()

	orders := make([]model.Order, 0, chunkSize)
	for rows.Next() {
		var order model.Order
		if err := r.db.ScanRows(rows, &order); err != nil {
			return err
		}
		orders = append(orders, order)

		if len(orders) >= chunkSize {
			if err := callback(orders); err != nil {
				return err
			}
			orders = orders[:0]
		}
	}

	// 处理剩余数据
	if len(orders) > 0 {
		if err := callback(orders); err != nil {
			return err
		}
	}

	return nil
}
