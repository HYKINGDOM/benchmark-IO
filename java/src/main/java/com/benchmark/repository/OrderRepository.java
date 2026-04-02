package com.benchmark.repository;

import com.benchmark.model.Order;
import com.benchmark.model.OrderQueryRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jooq.Condition;
import org.jooq.Cursor;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.SelectConditionStep;
import org.jooq.Table;
import org.jooq.impl.DSL;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;
import java.util.stream.Collectors;

import static org.jooq.impl.DSL.*;

/**
 * Order Repository using JOOQ
 *
 * @author Benchmark Team
 */
@Slf4j
@Repository
@RequiredArgsConstructor
public class OrderRepository {

    private final DSLContext dsl;

    // Table and field definitions
    private static final Table<?> ORDERS = table(name("orders"));
    private static final Field<Long> ORDER_ID = field(name("order_id"), Long.class);
    private static final Field<String> ORDER_NO = field(name("order_no"), String.class);
    private static final Field<Long> USER_ID = field(name("user_id"), Long.class);
    private static final Field<String> USER_NAME = field(name("user_name"), String.class);
    private static final Field<String> USER_PHONE = field(name("user_phone"), String.class);
    private static final Field<String> USER_ID_CARD = field(name("user_id_card"), String.class);
    private static final Field<String> USER_EMAIL = field(name("user_email"), String.class);
    private static final Field<String> USER_ADDRESS = field(name("user_address"), String.class);
    private static final Field<Long> PRODUCT_ID = field(name("product_id"), Long.class);
    private static final Field<String> PRODUCT_NAME = field(name("product_name"), String.class);
    private static final Field<String> PRODUCT_CATEGORY = field(name("product_category"), String.class);
    private static final Field<BigDecimal> PRODUCT_PRICE = field(name("product_price"), BigDecimal.class);
    private static final Field<?> QUANTITY = field(name("quantity"));
    private static final Field<BigDecimal> TOTAL_AMOUNT = field(name("total_amount"), BigDecimal.class);
    private static final Field<BigDecimal> DISCOUNT_AMOUNT = field(name("discount_amount"), BigDecimal.class);
    private static final Field<BigDecimal> PAY_AMOUNT = field(name("pay_amount"), BigDecimal.class);
    private static final Field<String> ORDER_STATUS = field(name("order_status"), String.class);
    private static final Field<String> PAYMENT_METHOD = field(name("payment_method"), String.class);
    private static final Field<LocalDateTime> PAYMENT_TIME = field(name("payment_time"), LocalDateTime.class);
    private static final Field<String> ORDER_SOURCE = field(name("order_source"), String.class);
    private static final Field<String> SHIPPING_ADDRESS = field(name("shipping_address"), String.class);
    private static final Field<String> RECEIVER_NAME = field(name("receiver_name"), String.class);
    private static final Field<String> RECEIVER_PHONE = field(name("receiver_phone"), String.class);
    private static final Field<String> LOGISTICS_NO = field(name("logistics_no"), String.class);
    private static final Field<LocalDateTime> DELIVERY_TIME = field(name("delivery_time"), LocalDateTime.class);
    private static final Field<LocalDateTime> COMPLETE_TIME = field(name("complete_time"), LocalDateTime.class);
    private static final Field<String> REMARK = field(name("remark"), String.class);
    private static final Field<LocalDateTime> CREATED_AT = field(name("created_at"), LocalDateTime.class);
    private static final Field<LocalDateTime> UPDATED_AT = field(name("updated_at"), LocalDateTime.class);
    private static final Field<?> IS_DELETED = field(name("is_deleted"));

    /**
     * Query orders with pagination
     */
    public List<Order> queryOrders(OrderQueryRequest request) {
        SelectConditionStep<?> query = dsl.select()
                .from(ORDERS)
                .where(buildConditions(request));

        // Apply pagination
        int offset = (request.getPage() - 1) * request.getPageSize();
        return query.orderBy(CREATED_AT.desc())
                .offset(offset)
                .limit(request.getPageSize())
                .fetch()
                .stream()
                .map(this::mapToOrder)
                .collect(Collectors.toList());
    }

    /**
     * Count total orders
     */
    public Long countOrders(OrderQueryRequest request) {
        return dsl.selectCount()
                .from(ORDERS)
                .where(buildConditions(request))
                .fetchOne(0, Long.class);
    }

    /**
     * Query orders for export (with limit)
     */
    public List<Order> queryOrdersForExport(OrderQueryRequest request, Integer limit) {
        SelectConditionStep<?> query = dsl.select()
                .from(ORDERS)
                .where(buildConditions(request));

        if (limit != null && limit > 0) {
            return query.orderBy(CREATED_AT.desc())
                    .limit(limit)
                    .fetch()
                    .stream()
                    .map(this::mapToOrder)
                    .collect(Collectors.toList());
        }

        return query.orderBy(CREATED_AT.desc())
                .fetch()
                .stream()
                .map(this::mapToOrder)
                .collect(Collectors.toList());
    }

    /**
     * Stream orders for large export
     */
    @SuppressWarnings("unchecked")
    public Cursor<?> streamOrders(OrderQueryRequest request, Integer limit) {
        SelectConditionStep<?> query = dsl.select()
                .from(ORDERS)
                .where(buildConditions(request));

        if (limit != null && limit > 0) {
            return query.orderBy(CREATED_AT.desc())
                    .limit(limit)
                    .fetchLazy();
        }

        return query.orderBy(CREATED_AT.desc())
                .fetchLazy();
    }

    /**
     * Build query conditions
     */
    private Condition buildConditions(OrderQueryRequest request) {
        Condition condition = condition("is_deleted = 0");

        if (request.getStartTime() != null) {
            LocalDateTime startDateTime = request.getStartTime().atStartOfDay();
            condition = condition.and(CREATED_AT.greaterOrEqual(startDateTime));
        }

        if (request.getEndTime() != null) {
            LocalDateTime endDateTime = request.getEndTime().atTime(LocalTime.MAX);
            condition = condition.and(CREATED_AT.lessOrEqual(endDateTime));
        }

        if (request.getStatus() != null && !request.getStatus().isEmpty()) {
            condition = condition.and(ORDER_STATUS.eq(request.getStatus()));
        }

        if (request.getMinAmount() != null) {
            condition = condition.and(TOTAL_AMOUNT.greaterOrEqual(request.getMinAmount()));
        }

        if (request.getMaxAmount() != null) {
            condition = condition.and(TOTAL_AMOUNT.lessOrEqual(request.getMaxAmount()));
        }

        if (request.getUserId() != null && !request.getUserId().isEmpty()) {
            try {
                Long userId = Long.parseLong(request.getUserId());
                condition = condition.and(USER_ID.eq(userId));
            } catch (NumberFormatException e) {
                log.warn("Invalid user_id format: {}", request.getUserId());
            }
        }

        if (request.getOrderNo() != null && !request.getOrderNo().isEmpty()) {
            condition = condition.and(ORDER_NO.eq(request.getOrderNo()));
        }

        return condition;
    }

    /**
     * Map Record to Order entity
     */
    private Order mapToOrder(Record record) {
        return Order.builder()
                .orderId(record.get(ORDER_ID))
                .orderNo(record.get(ORDER_NO))
                .userId(record.get(USER_ID))
                .userName(record.get(USER_NAME))
                .userPhone(record.get(USER_PHONE))
                .userIdCard(record.get(USER_ID_CARD))
                .userEmail(record.get(USER_EMAIL))
                .userAddress(record.get(USER_ADDRESS))
                .productId(record.get(PRODUCT_ID))
                .productName(record.get(PRODUCT_NAME))
                .productCategory(record.get(PRODUCT_CATEGORY))
                .productPrice(record.get(PRODUCT_PRICE))
                .quantity(toInt(record.get(QUANTITY)))
                .totalAmount(record.get(TOTAL_AMOUNT))
                .discountAmount(record.get(DISCOUNT_AMOUNT))
                .payAmount(record.get(PAY_AMOUNT))
                .orderStatus(record.get(ORDER_STATUS))
                .paymentMethod(record.get(PAYMENT_METHOD))
                .paymentTime(toLocalDateTime(record.get(PAYMENT_TIME)))
                .orderSource(record.get(ORDER_SOURCE))
                .shippingAddress(record.get(SHIPPING_ADDRESS))
                .receiverName(record.get(RECEIVER_NAME))
                .receiverPhone(record.get(RECEIVER_PHONE))
                .logisticsNo(record.get(LOGISTICS_NO))
                .deliveryTime(toLocalDateTime(record.get(DELIVERY_TIME)))
                .completeTime(toLocalDateTime(record.get(COMPLETE_TIME)))
                .remark(record.get(REMARK))
                .createdAt(toLocalDateTime(record.get(CREATED_AT)))
                .updatedAt(toLocalDateTime(record.get(UPDATED_AT)))
                .isDeleted(toInt(record.get(IS_DELETED)))
                .build();
    }

    private LocalDateTime toLocalDateTime(Object value) {
        if (value == null) return null;
        if (value instanceof LocalDateTime) return (LocalDateTime) value;
        if (value instanceof java.sql.Timestamp) return ((java.sql.Timestamp) value).toLocalDateTime();
        if (value instanceof java.sql.Date) return ((java.sql.Date) value).toLocalDate().atStartOfDay();
        return null;
    }

    private Integer toInt(Object value) {
        if (value == null) return null;
        if (value instanceof Integer) return (Integer) value;
        if (value instanceof Number) return ((Number) value).intValue();
        return null;
    }
}
