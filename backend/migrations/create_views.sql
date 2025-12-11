-- ============================================================
-- 创建数据库视图
-- 用于优化前端界面查询性能
-- ============================================================

USE port_equipment_db;

-- ============================================================
-- 1. 设备库存统计视图
-- 用途：设备库存管理界面，显示设备基本信息及库存状态
-- ============================================================
CREATE OR REPLACE VIEW v_equipment_inventory AS
SELECT 
    e.equipment_id,
    e.equipment_code,
    e.equipment_name,
    e.category,
    e.status,
    e.storage_location,
    e.purchase_price,
    e.daily_rental_rate,
    e.supplier,
    e.manufacturer,
    e.purchase_date,
    e.warranty_date,
    e.last_maintenance_date,
    e.serial_number,
    e.specifications,
    e.created_at,
    e.updated_at,
    -- 统计信息
    CASE 
        WHEN e.status = '在库' THEN 1 
        ELSE 0 
    END AS available_quantity,
    CASE 
        WHEN e.status = '已出库' THEN 1 
        ELSE 0 
    END AS rented_quantity,
    CASE 
        WHEN e.status = '维修中' THEN 1 
        ELSE 0 
    END AS maintenance_quantity,
    -- 租赁统计
    COALESCE(rental_stats.rental_count, 0) AS rental_count,
    COALESCE(rental_stats.total_rental_days, 0) AS total_rental_days,
    COALESCE(rental_stats.total_revenue, 0.0) AS total_revenue
FROM equipment e
LEFT JOIN (
    SELECT 
        oi.equipment_id,
        COUNT(DISTINCT oi.order_id) AS rental_count,
        SUM(oi.rental_days) AS total_rental_days,
        SUM(oi.subtotal) AS total_revenue
    FROM order_items oi
    JOIN lease_orders lo ON oi.order_id = lo.order_id
    WHERE lo.is_deleted = 0
    GROUP BY oi.equipment_id
) rental_stats ON e.equipment_id = rental_stats.equipment_id
WHERE e.is_deleted = 0;

-- ============================================================
-- 2. 订单汇总视图
-- 用途：订单管理界面，显示订单信息及关联的客户和明细汇总
-- ============================================================
CREATE OR REPLACE VIEW v_order_summary AS
SELECT 
    lo.order_id,
    lo.order_code,
    lo.customer_id,
    lo.customer_name,
    c.contact_person,
    c.phone AS customer_phone,
    c.email AS customer_email,
    c.credit_rating,
    lo.voyage_no,
    lo.start_date,
    lo.expected_return_date,
    lo.actual_return_date,
    lo.status AS order_status,
    lo.total_amount,
    lo.created_by,
    lo.created_at,
    lo.updated_at,
    -- 订单明细统计
    COALESCE(item_stats.equipment_count, 0) AS equipment_count,
    COALESCE(item_stats.total_rental_days, 0) AS total_rental_days,
    COALESCE(item_stats.avg_daily_rate, 0.0) AS avg_daily_rate,
    -- 账单信息
    b.bill_id,
    b.bill_code,
    b.status AS billing_status,
    b.total_amount AS billing_amount,
    b.payment_method,
    b.paid_amount,
    -- 归还信息
    rr.return_id,
    rr.return_code,
    rr.return_date,
    rr.inspection_status,
    rr.total_damage_fee
FROM lease_orders lo
LEFT JOIN customers c ON lo.customer_id = c.customer_id
LEFT JOIN (
    SELECT 
        order_id,
        COUNT(*) AS equipment_count,
        SUM(rental_days) AS total_rental_days,
        AVG(daily_rate) AS avg_daily_rate
    FROM order_items
    GROUP BY order_id
) item_stats ON lo.order_id = item_stats.order_id
LEFT JOIN billing b ON lo.order_id = b.order_id AND b.is_deleted = 0
LEFT JOIN return_records rr ON lo.order_id = rr.order_id
WHERE lo.is_deleted = 0;

-- ============================================================
-- 3. 客户租赁统计视图
-- 用途：客户分析界面，显示客户租赁历史统计
-- ============================================================
CREATE OR REPLACE VIEW v_customer_rental_stats AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.contact_person,
    c.phone,
    c.email,
    c.address,
    c.credit_rating,
    c.created_at,
    -- 订单统计
    COALESCE(order_stats.total_orders, 0) AS total_orders,
    COALESCE(order_stats.completed_orders, 0) AS completed_orders,
    COALESCE(order_stats.in_progress_orders, 0) AS in_progress_orders,
    COALESCE(order_stats.pending_orders, 0) AS pending_orders,
    -- 财务统计
    COALESCE(order_stats.total_amount, 0.0) AS total_rental_amount,
    COALESCE(order_stats.paid_amount, 0.0) AS paid_amount,
    COALESCE(order_stats.pending_amount, 0.0) AS pending_amount,
    -- 设备统计
    COALESCE(order_stats.total_equipment_count, 0) AS total_equipment_count,
    -- 最近订单
    order_stats.last_order_date,
    order_stats.last_order_code
FROM customers c
LEFT JOIN (
    SELECT 
        lo.customer_id,
        COUNT(DISTINCT lo.order_id) AS total_orders,
        SUM(CASE WHEN lo.status = '已完结' THEN 1 ELSE 0 END) AS completed_orders,
        SUM(CASE WHEN lo.status = '航次执行中' THEN 1 ELSE 0 END) AS in_progress_orders,
        SUM(CASE WHEN lo.status = '待提货' THEN 1 ELSE 0 END) AS pending_orders,
        SUM(lo.total_amount) AS total_amount,
        SUM(COALESCE(b.paid_amount, 0)) AS paid_amount,
        SUM(CASE 
            WHEN b.status IN ('待确认', '已确认') THEN COALESCE(b.total_amount, 0) 
            ELSE 0 
        END) AS pending_amount,
        SUM(oi_stats.equipment_count) AS total_equipment_count,
        MAX(lo.created_at) AS last_order_date,
        MAX(lo.order_code) AS last_order_code
    FROM lease_orders lo
    LEFT JOIN billing b ON lo.order_id = b.order_id AND b.is_deleted = 0
    LEFT JOIN (
        SELECT order_id, COUNT(*) AS equipment_count
        FROM order_items
        GROUP BY order_id
    ) oi_stats ON lo.order_id = oi_stats.order_id
    WHERE lo.is_deleted = 0
    GROUP BY lo.customer_id
) order_stats ON c.customer_id = order_stats.customer_id
WHERE c.is_deleted = 0;

-- ============================================================
-- 4. 财务汇总视图
-- 用途：结算管理界面，显示账单及关联的订单和客户信息
-- ============================================================
CREATE OR REPLACE VIEW v_billing_summary AS
SELECT 
    b.bill_id,
    b.bill_code,
    b.order_id,
    lo.order_code,
    b.customer_name,
    c.customer_id,
    c.contact_person,
    c.phone AS customer_phone,
    c.email AS customer_email,
    b.rental_fee,
    b.repair_fee,
    b.other_fee,
    b.discount,
    b.total_amount,
    b.paid_amount,
    (b.total_amount - COALESCE(b.paid_amount, 0)) AS unpaid_amount,
    b.status AS billing_status,
    b.payment_method,
    b.invoice_no,
    b.billing_date,
    b.payment_date,
    b.remarks,
    b.created_at,
    b.updated_at,
    -- 订单信息
    lo.voyage_no,
    lo.start_date,
    lo.expected_return_date,
    lo.actual_return_date,
    lo.status AS order_status,
    -- 订单明细统计
    COALESCE(item_stats.equipment_count, 0) AS equipment_count,
    COALESCE(item_stats.total_rental_days, 0) AS total_rental_days
FROM billing b
LEFT JOIN lease_orders lo ON b.order_id = lo.order_id
LEFT JOIN customers c ON lo.customer_id = c.customer_id
LEFT JOIN (
    SELECT 
        order_id,
        COUNT(*) AS equipment_count,
        SUM(rental_days) AS total_rental_days
    FROM order_items
    GROUP BY order_id
) item_stats ON b.order_id = item_stats.order_id
WHERE b.is_deleted = 0;

-- ============================================================
-- 5. 设备使用情况视图
-- 用途：设备分析界面，显示设备使用统计和收益
-- ============================================================
CREATE OR REPLACE VIEW v_equipment_usage AS
SELECT 
    e.equipment_id,
    e.equipment_code,
    e.equipment_name,
    e.category,
    e.status,
    e.storage_location,
    e.purchase_price,
    e.daily_rental_rate,
    e.supplier,
    e.manufacturer,
    e.purchase_date,
    e.warranty_date,
    e.last_maintenance_date,
    e.created_at,
    -- 租赁统计
    COALESCE(usage_stats.rental_count, 0) AS rental_count,
    COALESCE(usage_stats.total_rental_days, 0) AS total_rental_days,
    COALESCE(usage_stats.total_revenue, 0.0) AS total_revenue,
    COALESCE(usage_stats.avg_rental_days, 0.0) AS avg_rental_days,
    -- 最近租赁
    usage_stats.last_rental_date,
    usage_stats.last_customer_name,
    -- 维修统计
    COALESCE(maintenance_stats.maintenance_count, 0) AS maintenance_count,
    COALESCE(maintenance_stats.total_maintenance_cost, 0.0) AS total_maintenance_cost,
    -- 利用率计算
    CASE 
        WHEN e.purchase_date IS NOT NULL THEN
            ROUND(COALESCE(usage_stats.total_rental_days, 0) / 
                  DATEDIFF(CURDATE(), e.purchase_date) * 100, 2)
        ELSE 0
    END AS utilization_rate
FROM equipment e
LEFT JOIN (
    SELECT 
        oi.equipment_id,
        COUNT(DISTINCT oi.order_id) AS rental_count,
        SUM(oi.rental_days) AS total_rental_days,
        SUM(oi.subtotal) AS total_revenue,
        AVG(oi.rental_days) AS avg_rental_days,
        MAX(lo.created_at) AS last_rental_date,
        MAX(lo.customer_name) AS last_customer_name
    FROM order_items oi
    JOIN lease_orders lo ON oi.order_id = lo.order_id
    WHERE lo.is_deleted = 0
    GROUP BY oi.equipment_id
) usage_stats ON e.equipment_id = usage_stats.equipment_id
LEFT JOIN (
    SELECT 
        equipment_id,
        COUNT(*) AS maintenance_count,
        SUM(maintenance_cost + parts_cost + labor_cost) AS total_maintenance_cost
    FROM maintenance_records
    WHERE is_deleted = 0
    GROUP BY equipment_id
) maintenance_stats ON e.equipment_id = maintenance_stats.equipment_id
WHERE e.is_deleted = 0;

-- ============================================================
-- 6. 入库出库汇总视图
-- 用途：仓储管理界面，显示入库出库记录及明细汇总
-- ============================================================
CREATE OR REPLACE VIEW v_inbound_outbound_summary AS
SELECT 
    'inbound' AS record_type,
    ir.inbound_id AS record_id,
    ir.inbound_code AS record_code,
    ir.supplier,
    ir.purchase_date,
    ir.inbound_date AS operation_date,
    ir.operator,
    ir.total_quantity,
    ir.total_amount,
    ir.status,
    ir.remarks,
    ir.created_at,
    -- 明细统计
    COUNT(DISTINCT ii.item_id) AS item_count,
    GROUP_CONCAT(DISTINCT ii.equipment_name SEPARATOR ', ') AS equipment_names
FROM inbound_records ir
LEFT JOIN inbound_items ii ON ir.inbound_id = ii.inbound_id
WHERE ir.is_deleted = 0
GROUP BY ir.inbound_id, ir.inbound_code, ir.supplier, ir.purchase_date, 
         ir.inbound_date, ir.operator, ir.total_quantity, ir.total_amount, 
         ir.status, ir.remarks, ir.created_at

UNION ALL

SELECT 
    'outbound' AS record_type,
    or_rec.outbound_id AS record_id,
    or_rec.outbound_code AS record_code,
    NULL AS supplier,
    NULL AS purchase_date,
    or_rec.outbound_date AS operation_date,
    or_rec.operator,
    or_rec.total_quantity,
    0.0 AS total_amount,
    or_rec.status,
    or_rec.remarks,
    or_rec.created_at,
    -- 明细统计
    COUNT(DISTINCT oi.item_id) AS item_count,
    GROUP_CONCAT(DISTINCT oi.equipment_name SEPARATOR ', ') AS equipment_names
FROM outbound_records or_rec
LEFT JOIN outbound_items oi ON or_rec.outbound_id = oi.outbound_id
LEFT JOIN lease_orders lo ON or_rec.order_id = lo.order_id
WHERE or_rec.is_deleted = 0
GROUP BY or_rec.outbound_id, or_rec.outbound_code, or_rec.outbound_date, 
         or_rec.operator, or_rec.total_quantity, or_rec.status, 
         or_rec.remarks, or_rec.created_at;

-- ============================================================
-- 7. 设备类别统计视图
-- 用途：设备分类统计，用于数据分析和报表
-- ============================================================
CREATE OR REPLACE VIEW v_equipment_category_stats AS
SELECT 
    e.category,
    COUNT(*) AS total_count,
    SUM(CASE WHEN e.status = '在库' THEN 1 ELSE 0 END) AS in_stock_count,
    SUM(CASE WHEN e.status = '已出库' THEN 1 ELSE 0 END) AS out_stock_count,
    SUM(CASE WHEN e.status = '维修中' THEN 1 ELSE 0 END) AS maintenance_count,
    SUM(e.purchase_price) AS total_purchase_value,
    AVG(e.daily_rental_rate) AS avg_daily_rate,
    -- 租赁统计
    COALESCE(rental_stats.total_rental_count, 0) AS total_rental_count,
    COALESCE(rental_stats.total_revenue, 0.0) AS total_revenue
FROM equipment e
LEFT JOIN (
    SELECT 
        e2.category,
        COUNT(DISTINCT oi.order_id) AS total_rental_count,
        SUM(oi.subtotal) AS total_revenue
    FROM equipment e2
    JOIN order_items oi ON e2.equipment_id = oi.equipment_id
    JOIN lease_orders lo ON oi.order_id = lo.order_id
    WHERE e2.is_deleted = 0 AND lo.is_deleted = 0
    GROUP BY e2.category
) rental_stats ON e.category = rental_stats.category
WHERE e.is_deleted = 0
GROUP BY e.category;

-- ============================================================
-- 验证视图创建
-- ============================================================
SELECT '视图创建完成！' AS status;
SELECT TABLE_NAME AS view_name 
FROM INFORMATION_SCHEMA.VIEWS 
WHERE TABLE_SCHEMA = 'port_equipment_db'
ORDER BY TABLE_NAME;

