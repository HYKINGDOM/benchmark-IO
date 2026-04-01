package com.benchmark.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Order Entity
 *
 * @author Benchmark Team
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Order {

    private Long orderId;
    private String orderNo;
    private Long userId;
    private String userName;
    private String userPhone;
    private String userIdCard;
    private String userEmail;
    private String userAddress;
    private Long productId;
    private String productName;
    private String productCategory;
    private BigDecimal productPrice;
    private Integer quantity;
    private BigDecimal totalAmount;
    private BigDecimal discountAmount;
    private BigDecimal payAmount;
    private String orderStatus;
    private String paymentMethod;
    private LocalDateTime paymentTime;
    private String orderSource;
    private String shippingAddress;
    private String receiverName;
    private String receiverPhone;
    private String logisticsNo;
    private LocalDateTime deliveryTime;
    private LocalDateTime completeTime;
    private String remark;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Integer isDeleted;
}
