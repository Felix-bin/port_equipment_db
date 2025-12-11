-- ============================================================
-- 添加用户信息扩展字段
-- 注意：如果列已存在，执行时会报错，可以忽略
-- ============================================================

USE port_equipment_db;

-- 添加用户信息扩展字段
-- 注意：OceanBase/MySQL 不支持 IF NOT EXISTS，如果列已存在会报错
-- 可以手动检查或忽略错误

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

-- 创建索引（如果索引已存在会报错，可以忽略）
-- 注意：先检查索引是否存在，避免重复创建
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_phone ON users(phone);

SELECT '用户信息扩展字段添加完成！' AS status;

