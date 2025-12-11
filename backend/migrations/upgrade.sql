-- ============================================================
-- 数据库升级脚本
-- 从旧版本升级到新版本
-- 执行前请务必备份数据库！
-- ============================================================

USE port_equipment_db;

-- ============================================================
-- 第一部分：更新现有表结构
-- ============================================================

-- 1. 更新 equipment 表
ALTER TABLE equipment
ADD COLUMN IF NOT EXISTS supplier VARCHAR(200) COMMENT '供应商',
ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(200) COMMENT '制造商',
ADD COLUMN IF NOT EXISTS purchase_date DATE COMMENT '采购日期',
ADD COLUMN IF NOT EXISTS warranty_date DATE COMMENT '质保期限',
ADD COLUMN IF NOT EXISTS last_maintenance_date DATE COMMENT '最后维护日期',
ADD COLUMN IF NOT EXISTS serial_number VARCHAR(100) COMMENT '序列号';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_supplier ON equipment(supplier);
CREATE INDEX IF NOT EXISTS idx_manufacturer ON equipment(manufacturer);

-- 2. 更新 billing 表
ALTER TABLE billing
ADD COLUMN IF NOT EXISTS discount FLOAT DEFAULT 0.0 COMMENT '折扣金额',
ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20) COMMENT '支付方式',
ADD COLUMN IF NOT EXISTS invoice_no VARCHAR(50) COMMENT '发票号',
ADD COLUMN IF NOT EXISTS paid_amount FLOAT DEFAULT 0.0 COMMENT '已支付金额';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_invoice_no ON billing(invoice_no);
CREATE INDEX IF NOT EXISTS idx_payment_method ON billing(payment_method);

-- 3. 更新 return_records 表
ALTER TABLE return_records
ADD COLUMN IF NOT EXISTS total_damage_fee FLOAT DEFAULT 0.0 COMMENT '总损坏赔偿费';

-- ============================================================
-- 第二部分：创建新表
-- ============================================================

-- 1. 供应商表
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '供应商ID',
    supplier_code VARCHAR(50) UNIQUE NOT NULL COMMENT '供应商编号',
    supplier_name VARCHAR(200) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(100) COMMENT '联系人',
    phone VARCHAR(50) COMMENT '电话',
    email VARCHAR(100) COMMENT '邮箱',
    address VARCHAR(500) COMMENT '地址',
    bank_account VARCHAR(100) COMMENT '银行账户',
    credit_rating VARCHAR(20) COMMENT '信用评级',
    remarks TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted INT DEFAULT 0 COMMENT '删除标记',
    INDEX idx_supplier_code (supplier_code),
    INDEX idx_supplier_name (supplier_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商表';

-- 2. 入库记录主表
CREATE TABLE IF NOT EXISTS inbound_records (
    inbound_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '入库记录ID',
    inbound_code VARCHAR(50) UNIQUE NOT NULL COMMENT '入库单号',
    supplier VARCHAR(200) COMMENT '供应商',
    purchase_date DATE COMMENT '采购日期',
    inbound_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '入库日期',
    operator VARCHAR(100) COMMENT '操作员',
    total_quantity INT DEFAULT 0 COMMENT '入库总数量',
    total_amount FLOAT DEFAULT 0.0 COMMENT '入库总金额',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态：pending/completed/cancelled',
    remarks TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted INT DEFAULT 0 COMMENT '删除标记',
    INDEX idx_inbound_code (inbound_code),
    INDEX idx_supplier (supplier),
    INDEX idx_inbound_date (inbound_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库记录表';

-- 3. 入库明细表
CREATE TABLE IF NOT EXISTS inbound_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细ID',
    inbound_id INT NOT NULL COMMENT '入库记录ID',
    equipment_id INT COMMENT '设备ID',
    equipment_code VARCHAR(50) NOT NULL COMMENT '设备编号',
    equipment_name VARCHAR(200) NOT NULL COMMENT '设备名称',
    category VARCHAR(100) NOT NULL COMMENT '设备类型',
    specifications TEXT COMMENT '规格型号',
    quantity INT DEFAULT 1 COMMENT '数量',
    unit_price FLOAT DEFAULT 0.0 COMMENT '单价',
    subtotal FLOAT DEFAULT 0.0 COMMENT '小计',
    storage_location VARCHAR(100) COMMENT '存放位置',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (inbound_id) REFERENCES inbound_records(inbound_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE SET NULL,
    INDEX idx_inbound_id (inbound_id),
    INDEX idx_equipment_code (equipment_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库明细表';

-- 4. 出库记录主表
CREATE TABLE IF NOT EXISTS outbound_records (
    outbound_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '出库记录ID',
    outbound_code VARCHAR(50) UNIQUE NOT NULL COMMENT '出库单号',
    order_id INT COMMENT '关联订单ID',
    outbound_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '出库日期',
    operator VARCHAR(100) COMMENT '操作员',
    recipient VARCHAR(100) COMMENT '接收人',
    recipient_phone VARCHAR(50) COMMENT '接收人电话',
    total_quantity INT DEFAULT 0 COMMENT '出库总数量',
    status VARCHAR(20) DEFAULT 'completed' COMMENT '状态：pending/completed/cancelled',
    remarks TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted INT DEFAULT 0 COMMENT '删除标记',
    FOREIGN KEY (order_id) REFERENCES lease_orders(order_id) ON DELETE SET NULL,
    INDEX idx_outbound_code (outbound_code),
    INDEX idx_order_id (order_id),
    INDEX idx_outbound_date (outbound_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='出库记录表';

-- 5. 出库明细表
CREATE TABLE IF NOT EXISTS outbound_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细ID',
    outbound_id INT NOT NULL COMMENT '出库记录ID',
    equipment_id INT NOT NULL COMMENT '设备ID',
    equipment_code VARCHAR(50) NOT NULL COMMENT '设备编号',
    equipment_name VARCHAR(200) NOT NULL COMMENT '设备名称',
    quantity INT DEFAULT 1 COMMENT '数量',
    daily_rate FLOAT DEFAULT 0.0 COMMENT '日租金',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (outbound_id) REFERENCES outbound_records(outbound_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE RESTRICT,
    INDEX idx_outbound_id (outbound_id),
    INDEX idx_equipment_id (equipment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='出库明细表';

-- 6. 归还明细表
CREATE TABLE IF NOT EXISTS return_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细ID',
    return_id INT NOT NULL COMMENT '归还记录ID',
    equipment_id INT NOT NULL COMMENT '设备ID',
    equipment_code VARCHAR(50) NOT NULL COMMENT '设备编号',
    equipment_name VARCHAR(200) NOT NULL COMMENT '设备名称',
    equipment_condition VARCHAR(20) DEFAULT 'good' COMMENT '设备状况：good/normal/damaged',
    damage_description TEXT COMMENT '损坏描述',
    damage_fee FLOAT DEFAULT 0.0 COMMENT '损坏赔偿费',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (return_id) REFERENCES return_records(return_id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE RESTRICT,
    INDEX idx_return_id (return_id),
    INDEX idx_equipment_id (equipment_id),
    INDEX idx_condition (equipment_condition)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='归还明细表';

-- 7. 设备维修记录表
CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '维修记录ID',
    maintenance_code VARCHAR(50) UNIQUE NOT NULL COMMENT '维修单号',
    equipment_id INT NOT NULL COMMENT '设备ID',
    equipment_code VARCHAR(50) NOT NULL COMMENT '设备编号',
    maintenance_type VARCHAR(50) COMMENT '维护类型：routine/repair/overhaul',
    problem_description TEXT COMMENT '问题描述',
    maintenance_content TEXT COMMENT '维护内容',
    maintenance_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '维护日期',
    completion_date DATETIME COMMENT '完成日期',
    technician VARCHAR(100) COMMENT '技术员',
    maintenance_cost FLOAT DEFAULT 0.0 COMMENT '维护费用',
    parts_cost FLOAT DEFAULT 0.0 COMMENT '配件费用',
    labor_cost FLOAT DEFAULT 0.0 COMMENT '人工费用',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态：pending/in-progress/completed/cancelled',
    remarks TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted INT DEFAULT 0 COMMENT '删除标记',
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id) ON DELETE RESTRICT,
    INDEX idx_maintenance_code (maintenance_code),
    INDEX idx_equipment_id (equipment_id),
    INDEX idx_maintenance_date (maintenance_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备维修记录表';

-- ============================================================
-- 第三部分：验证
-- ============================================================

-- 查看所有表
SHOW TABLES;

-- 查看关键表的结构
DESCRIBE equipment;
DESCRIBE billing;
DESCRIBE return_records;
DESCRIBE suppliers;
DESCRIBE inbound_records;
DESCRIBE outbound_records;
DESCRIBE maintenance_records;

-- ============================================================
-- 升级完成
-- ============================================================
SELECT '数据库升级完成！' AS status;

