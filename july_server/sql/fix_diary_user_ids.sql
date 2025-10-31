-- =============================================
-- 修复日记的user_id：将测试用户ID更新为真实微信用户ID
-- =============================================
USE july;

-- 查看当前需要修复的日记
SELECT 
    id,
    user_id,
    diary_date,
    content,
    create_time
FROM diary
WHERE user_id = 'test_user_diary_dev'
  AND delete_time IS NULL;

-- 如果需要更新为特定用户ID，请先确认该用户ID存在
-- 例如：更新为 1a32903d304142129a30a06970dfe43d
-- 
-- 方法1: 如果确定所有test_user_diary_dev的日记都属于某个微信用户
-- UPDATE diary 
-- SET user_id = '1a32903d304142129a30a06970dfe43d'
-- WHERE user_id = 'test_user_diary_dev'
--   AND delete_time IS NULL;

-- 方法2: 如果需要根据openid或其他信息匹配，可以先查看用户表
-- SELECT id, nickname, openid 
-- FROM user 
-- WHERE delete_time IS NULL;

-- ⚠️ 注意：执行UPDATE前请先备份数据！
-- ⚠️ 建议：先执行上面的SELECT查看需要更新的记录，确认无误后再执行UPDATE

