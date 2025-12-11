-- ============================================================
-- 添加用户信息扩展字段（安全版本 - 带错误处理）
-- 适用于 OceanBase/MySQL
-- ============================================================

USE port_equipment_db;

-- 使用存储过程安全地添加列
DELIMITER $$

DROP PROCEDURE IF EXISTS add_user_profile_columns$$

CREATE PROCEDURE add_user_profile_columns()
BEGIN
    DECLARE CONTINUE HANDLER FOR 1060 BEGIN END; -- 忽略"Duplicate column name"错误
    
    -- 添加 nickname 列
    ALTER TABLE users ADD COLUMN nickname VARCHAR(100) COMMENT '昵称';
    
    -- 添加 address 列
    ALTER TABLE users ADD COLUMN address VARCHAR(500) COMMENT '地址';
    
    -- 添加 profile 列
    ALTER TABLE users ADD COLUMN profile TEXT COMMENT '个人简介';
    
    -- 添加 country_region 列
    ALTER TABLE users ADD COLUMN country_region VARCHAR(100) COMMENT '国家/地区';
    
    -- 添加 area 列
    ALTER TABLE users ADD COLUMN area VARCHAR(200) COMMENT '地区';
    
    -- 添加 avatar 列
    ALTER TABLE users ADD COLUMN avatar VARCHAR(500) COMMENT '头像URL';
END$$

DELIMITER ;

-- 执行存储过程
CALL add_user_profile_columns();

-- 删除存储过程
DROP PROCEDURE IF EXISTS add_user_profile_columns;

-- 创建索引（使用错误处理）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_user_indexes$$

CREATE PROCEDURE add_user_indexes()
BEGIN
    DECLARE CONTINUE HANDLER FOR 1061 BEGIN END; -- 忽略"Duplicate key name"错误
    
    CREATE INDEX idx_user_email ON users(email);
    CREATE INDEX idx_user_phone ON users(phone);
END$$

DELIMITER ;

-- 执行索引创建
CALL add_user_indexes();

-- 删除存储过程
DROP PROCEDURE IF EXISTS add_user_indexes;

SELECT '用户信息扩展字段添加完成！' AS status;

