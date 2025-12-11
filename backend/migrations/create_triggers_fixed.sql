-- ============================================================
-- 创建数据库触发器（修复版 - 不使用DELIMITER）
-- 用于自动化业务逻辑处理
-- ============================================================

USE port_equipment_db;

-- 删除已存在的触发器（如果存在）
DROP TRIGGER IF EXISTS trg_order_item_insert;
DROP TRIGGER IF EXISTS trg_order_item_update;
DROP TRIGGER IF EXISTS trg_order_item_delete;
DROP TRIGGER IF EXISTS trg_order_created;
DROP TRIGGER IF EXISTS trg_return_record_created;
DROP TRIGGER IF EXISTS trg_inspection_record_created;
DROP TRIGGER IF EXISTS trg_billing_before_insert;
DROP TRIGGER IF EXISTS trg_billing_before_update;
DROP TRIGGER IF EXISTS trg_billing_after_update;
DROP TRIGGER IF EXISTS trg_equipment_status_change;
DROP TRIGGER IF EXISTS trg_outbound_record_created;
DROP TRIGGER IF EXISTS trg_inbound_record_created;

-- ============================================================
-- 1. 订单明细插入触发器 - 自动更新订单总金额
-- ============================================================
CREATE TRIGGER trg_order_item_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE lease_orders
    SET total_amount = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM order_items
        WHERE order_id = NEW.order_id
    ),
    updated_at = NOW()
    WHERE order_id = NEW.order_id;
    
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '订单金额触发器', 'INSERT', 'order_items', NEW.item_id, 
            CONCAT('订单明细插入，订单ID: ', NEW.order_id, '，设备: ', COALESCE(NEW.equipment_name, ''), '，小计: ¥', NEW.subtotal));
END;

-- ============================================================
-- 2. 订单明细更新触发器 - 自动更新订单总金额
-- ============================================================
CREATE TRIGGER trg_order_item_update
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    UPDATE lease_orders
    SET total_amount = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM order_items
        WHERE order_id = NEW.order_id
    ),
    updated_at = NOW()
    WHERE order_id = NEW.order_id;
    
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('info', '订单金额触发器', 'UPDATE', 'order_items', NEW.item_id, 
            CONCAT('订单明细更新，订单ID: ', NEW.order_id, '，小计从 ¥', COALESCE(OLD.subtotal, 0), ' 变更为 ¥', NEW.subtotal));
END;

-- ============================================================
-- 3. 订单明细删除触发器 - 自动更新订单总金额
-- ============================================================
CREATE TRIGGER trg_order_item_delete
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE lease_orders
    SET total_amount = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM order_items
        WHERE order_id = OLD.order_id
    ),
    updated_at = NOW()
    WHERE order_id = OLD.order_id;
    
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('info', '订单金额触发器', 'DELETE', 'order_items', OLD.item_id, 
            CONCAT('订单明细删除，订单ID: ', OLD.order_id, '，设备: ', COALESCE(OLD.equipment_name, '')));
END;

-- ============================================================
-- 4. 订单创建触发器 - 自动更新设备状态为"已出库"
-- ============================================================
CREATE TRIGGER trg_order_created
AFTER INSERT ON lease_orders
FOR EACH ROW
BEGIN
    UPDATE equipment e
    INNER JOIN order_items oi ON e.equipment_id = oi.equipment_id
    SET e.status = '已出库',
        e.updated_at = NOW()
    WHERE oi.order_id = NEW.order_id
      AND e.status = '在库'
      AND e.is_deleted = 0;
    
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '订单创建触发器', 'INSERT', 'lease_orders', NEW.order_id, 
            CONCAT('订单创建，订单号: ', NEW.order_code, '，客户: ', NEW.customer_name, '，总金额: ¥', COALESCE(NEW.total_amount, 0)));
END;

-- ============================================================
-- 5. 归还记录创建触发器 - 记录归还操作
-- ============================================================
CREATE TRIGGER trg_return_record_created
AFTER INSERT ON return_records
FOR EACH ROW
BEGIN
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '归还记录触发器', 'INSERT', 'return_records', NEW.return_id, 
            CONCAT('归还记录创建，归还单号: ', NEW.return_code, '，订单ID: ', NEW.order_id, '，设备数量: ', NEW.equipment_count));
END;

-- ============================================================
-- 6. 质检记录创建触发器 - 根据质检结果自动更新设备状态
-- ============================================================
CREATE TRIGGER trg_inspection_record_created
AFTER INSERT ON inspection_records
FOR EACH ROW
BEGIN
    DECLARE new_status VARCHAR(20);
    
    IF NEW.repair_needed = 1 OR NEW.function_test = '故障' THEN
        SET new_status = '维修中';
    ELSE
        SET new_status = '在库';
    END IF;
    
    UPDATE equipment
    SET status = new_status,
        updated_at = NOW()
    WHERE equipment_id = NEW.equipment_id
      AND is_deleted = 0;
    
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '质检记录触发器', 'INSERT', 'inspection_records', NEW.inspection_id, 
            CONCAT('质检记录创建，设备: ', NEW.equipment_code, '，质检结果: ', NEW.result, '，设备状态更新为: ', new_status));
END;

-- ============================================================
-- 7. 账单创建前触发器 - 自动计算总金额
-- ============================================================
CREATE TRIGGER trg_billing_before_insert
BEFORE INSERT ON billing
FOR EACH ROW
BEGIN
    IF NEW.total_amount IS NULL OR NEW.total_amount = 0 THEN
        SET NEW.total_amount = COALESCE(NEW.rental_fee, 0) + 
                               COALESCE(NEW.repair_fee, 0) + 
                               COALESCE(NEW.other_fee, 0) - 
                               COALESCE(NEW.discount, 0);
    END IF;
END;

-- ============================================================
-- 8. 账单更新触发器 - 自动重新计算总金额
-- ============================================================
CREATE TRIGGER trg_billing_before_update
BEFORE UPDATE ON billing
FOR EACH ROW
BEGIN
    IF (NEW.rental_fee != OLD.rental_fee) OR 
       (NEW.repair_fee != OLD.repair_fee) OR 
       (NEW.other_fee != OLD.other_fee) OR 
       (NEW.discount != OLD.discount) THEN
        SET NEW.total_amount = COALESCE(NEW.rental_fee, 0) + 
                               COALESCE(NEW.repair_fee, 0) + 
                               COALESCE(NEW.other_fee, 0) - 
                               COALESCE(NEW.discount, 0);
    END IF;
END;

-- ============================================================
-- 8b. 账单更新后触发器 - 记录日志
-- ============================================================
CREATE TRIGGER trg_billing_after_update
AFTER UPDATE ON billing
FOR EACH ROW
BEGIN
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('info', '账单更新触发器', 'UPDATE', 'billing', NEW.bill_id, 
            CONCAT('账单更新，账单号: ', NEW.bill_code, '，总金额: ¥', NEW.total_amount));
END;

-- ============================================================
-- 9. 设备状态变更触发器 - 记录状态变更日志
-- ============================================================
CREATE TRIGGER trg_equipment_status_change
AFTER UPDATE ON equipment
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
        VALUES ('info', '设备状态触发器', 'STATUS_CHANGE', 'equipment', NEW.equipment_id, 
                CONCAT('设备状态变更，设备: ', NEW.equipment_name, ' (', NEW.equipment_code, ')，状态从 "', 
                       OLD.status, '" 变更为 "', NEW.status, '"'));
    END IF;
END;

-- ============================================================
-- 10. 出库记录创建触发器 - 自动更新设备状态
-- ============================================================
CREATE TRIGGER trg_outbound_record_created
AFTER INSERT ON outbound_records
FOR EACH ROW
BEGIN
    UPDATE equipment e
    INNER JOIN outbound_items oi ON e.equipment_id = oi.equipment_id
    SET e.status = '已出库',
        e.updated_at = NOW()
    WHERE oi.outbound_id = NEW.outbound_id
      AND e.status = '在库'
      AND e.is_deleted = 0;
    
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '出库记录触发器', 'INSERT', 'outbound_records', NEW.outbound_id, 
            CONCAT('出库记录创建，出库单号: ', NEW.outbound_code, '，设备数量: ', NEW.total_quantity));
END;

-- ============================================================
-- 11. 入库记录创建触发器 - 记录入库操作
-- ============================================================
CREATE TRIGGER trg_inbound_record_created
AFTER INSERT ON inbound_records
FOR EACH ROW
BEGIN
    UPDATE equipment e
    INNER JOIN inbound_items ii ON e.equipment_id = ii.equipment_id
    SET e.status = '在库',
        e.updated_at = NOW()
    WHERE ii.inbound_id = NEW.inbound_id
      AND e.is_deleted = 0;
    
    INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description)
    VALUES ('success', '入库记录触发器', 'INSERT', 'inbound_records', NEW.inbound_id, 
            CONCAT('入库记录创建，入库单号: ', NEW.inbound_code, '，供应商: ', COALESCE(NEW.supplier, '未知'), '，设备数量: ', NEW.total_quantity));
END;

-- ============================================================
-- 验证触发器创建
-- ============================================================
SELECT '触发器创建完成！' AS status;

-- 查看所有触发器
SELECT 
    TRIGGER_NAME AS trigger_name,
    EVENT_MANIPULATION AS event_type,
    EVENT_OBJECT_TABLE AS table_name,
    ACTION_TIMING AS timing
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = 'port_equipment_db'
ORDER BY TRIGGER_NAME;

