-- =============================================
-- 添加"待定"情绪标签
-- =============================================
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
USE july;

-- 检查是否存在"待定"标签，如果不存在则插入
INSERT INTO `emotion_label` (`id`, `name`, `icon`, `color`, `type`, `use_count`, `status`, `create_time`)
SELECT 
    '8fda6000b16d11f0846e08bfb8c2c035' as `id`,
    '待定' as `name`,
    '🤔' as `icon`,
    '#A0A0A0' as `color`,
    'SYSTEM' as `type`,
    0 as `use_count`,
    1 as `status`,
    NOW() as `create_time`
WHERE NOT EXISTS (
    SELECT 1 FROM `emotion_label` 
    WHERE `name` = '待定' AND `delete_time` IS NULL
);

