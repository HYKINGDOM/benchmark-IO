package controller

import (
	"benchmark-api/internal/model"
	"benchmark-api/internal/service"
	"benchmark-api/pkg/response"

	"github.com/gin-gonic/gin"
)

type OrderController struct {
	svc *service.OrderService
}

func NewOrderController(svc *service.OrderService) *OrderController {
	return &OrderController{svc: svc}
}

// GetOrders 获取订单列表
// @Summary 订单查询
// @Description 支持分页、时间范围、状态、金额、用户ID、订单编号筛选
// @Tags 订单
// @Accept json
// @Produce json
// @Param page query int false "页码" default(1)
// @Param page_size query int false "每页数量" default(20)
// @Param start_time query string false "开始时间 (RFC3339格式)"
// @Param end_time query string false "结束时间 (RFC3339格式)"
// @Param order_no query string false "订单编号"
// @Param user_id query int false "用户ID"
// @Param status query string false "订单状态"
// @Param min_amount query number false "最小金额"
// @Param max_amount query number false "最大金额"
// @Param sort_by query string false "排序字段"
// @Param sort_order query string false "排序方向 (asc/desc)"
// @Success 200 {object} response.Response
// @Router /api/v1/orders [get]
func (c *OrderController) GetOrders(ctx *gin.Context) {
	var params model.OrderQueryParams
	if err := ctx.ShouldBindQuery(&params); err != nil {
		response.BadRequest(ctx, "参数错误: "+err.Error())
		return
	}

	result, err := c.svc.GetOrders(&params)
	if err != nil {
		response.InternalServerError(ctx, "查询失败: "+err.Error())
		return
	}

	response.Paginated(ctx, result.Total, result.Page, result.Size, result.Items)
}
