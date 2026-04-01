package service

import (
	"benchmark-api/internal/model"
	"benchmark-api/internal/repository"
)

type OrderService struct {
	repo *repository.OrderRepository
}

func NewOrderService(repo *repository.OrderRepository) *OrderService {
	return &OrderService{repo: repo}
}

func (s *OrderService) GetOrders(params *model.OrderQueryParams) (*model.OrderListResponse, error) {
	orders, total, err := s.repo.FindByParams(params)
	if err != nil {
		return nil, err
	}

	return &model.OrderListResponse{
		Total: total,
		Page:  params.Page,
		Size:  params.PageSize,
		Items: orders,
	}, nil
}
