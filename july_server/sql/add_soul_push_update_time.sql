-- 为 soul_push 表添加 update_time 字段
-- 使用方式：
--   mysql -u root -p july < sql/add_soul_push_update_time.sql

-- 检查字段是否存在，如果不存在则添加
SET @exist := (SELECT COUNT(*) FROM information_schema.columns 
               WHERE table_schema = DATABASE() 
               AND table_name = 'soul_push' 
               AND column_name = 'update_time');

SET @sqlstmt := IF(@exist = 0, 
    'ALTER TABLE `soul_push` ADD COLUMN `update_time` DATETIME DEFAULT NULL COMMENT ''更新时间'' AFTER `create_time`',
    'SELECT ''update_time column already exists'' AS message');

PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 同时更新 source_type 枚举，添加 CUSTOM 类型（如果还没有）
ALTER TABLE `soul_push` MODIFY COLUMN `source_type` ENUM('DIARY', 'TOPIC', 'EMOTION', 'RANDOM', 'CUSTOM') DEFAULT 'RANDOM' COMMENT '来源类型';

