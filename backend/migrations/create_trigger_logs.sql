-- ============================================================
-- 创建触发器日志表
-- ============================================================

USE port_equipment_db;

-- 创建触发器日志表
CREATE TABLE IF NOT EXISTS trigger_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    log_type VARCHAR(20) NOT NULL COMMENT '日志类型：success/info/warning/error',
    trigger_name VARCHAR(100) NOT NULL COMMENT '触发器名称',
    operation VARCHAR(50) NOT NULL COMMENT '操作类型',
    table_name VARCHAR(100) COMMENT '影响的表名',
    record_id INT COMMENT '记录ID',
    description TEXT COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_log_type (log_type),
    INDEX idx_trigger_name (trigger_name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='触发器日志表';

-- 插入一些示例数据
INSERT INTO trigger_logs (log_type, trigger_name, operation, table_name, record_id, description, created_at) VALUES
('success', '库存触发器', 'UPDATE', 'equipment', 1001, '装备"门式起重机 QZ-50T"出库后，库存数量自动减1，状态更新为"租赁中"', '2024-12-09 10:32:15'),
('success', '费用触发器', 'CALCULATE', 'return_records', 2001, '自动计算租赁费用：30天 × ¥1,500/天 × 1件 = ¥45,000', '2024-12-09 09:45:30'),
('info', '日志触发器', 'STATUS_CHANGE', 'equipment', 1002, '装备"电动叉车 CPCD-3T"状态从"在库"变更为"已出库"', '2024-12-09 09:20:45'),
('warning', '提醒触发器', 'REMINDER', 'lease_orders', NULL, '已检查租赁到期提醒，发送 3 条提醒通知', '2024-12-09 08:55:10'),
('success', '库存触发器', 'UPDATE', 'equipment', 1003, '装备"桥式起重机 QD-32T"归还后，可用数量自动+1，状态更新为"在库"', '2024-12-09 08:30:22'),
('success', '审核触发器', 'AUTO_APPROVE', 'lease_orders', 3001, '租赁申请自动审核通过：订单号 RA202401001，装备库存充足，用户信用良好', '2024-12-09 08:15:55'),
('info', '审核触发器', 'MANUAL_REVIEW', 'lease_orders', 3002, '租赁申请需人工审核：订单号 RA202401002，库存或信用不满足自动审核条件', '2024-12-09 08:10:30'),
('success', '结算触发器', 'AUTO_GENERATE', 'billing', 4001, '自动生成费用结算：订单 LD202401001，总金额 ¥45,000', '2024-12-09 07:55:18'),
('warning', '维护触发器', 'MAINTENANCE_ALERT', 'equipment', 1004, '装备"塔式起重机 QTZ-80"使用次数已达 100次，需要进行维护保养', '2024-12-09 07:30:45'),
('info', '日志触发器', 'STATUS_CHANGE', 'equipment', 1005, '装备"集装箱 40英尺"状态从"已出库"变更为"在库"', '2024-12-09 07:15:20');

SELECT '触发器日志表创建完成！' AS status;
SELECT COUNT(*) AS total_logs FROM trigger_logs;

