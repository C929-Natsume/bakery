-- =============================================
-- 字符集: 统一使用 utf8mb4_general_ci
-- =============================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 如果数据库不存在则创建
CREATE DATABASE IF NOT EXISTS `july` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE july;

-- 设置数据库默认字符集
ALTER DATABASE july CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- =============================================
-- 1. 版本控制表
-- =============================================
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- 2. 用户表
-- =============================================
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `openid` VARCHAR(64) NOT NULL COMMENT '微信openid',
  `nickname` VARCHAR(32) DEFAULT NULL COMMENT '昵称',
  `avatar` VARCHAR(256) DEFAULT NULL COMMENT '头像',
  `poster` VARCHAR(256) DEFAULT NULL COMMENT '封面',
  `signature` VARCHAR(64) DEFAULT NULL COMMENT '个性签名',
  `gender` ENUM('MAN','WOMAN','UN_KNOW') DEFAULT NULL COMMENT '性别',
  `city` VARCHAR(128) DEFAULT NULL COMMENT '城市',
  `province` VARCHAR(128) DEFAULT NULL COMMENT '省份',
  `country` VARCHAR(128) DEFAULT NULL COMMENT '国家',
  `is_admin` TINYINT(1) DEFAULT NULL COMMENT '是否为管理员',
  `remark` VARCHAR(64) DEFAULT NULL COMMENT '备注',
  `ip_belong` VARCHAR(128) DEFAULT NULL COMMENT 'IP归属地',
  PRIMARY KEY (`id`),
  UNIQUE KEY `openid` (`openid`),
  KEY `ix_user_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户表';

-- 插入示例用户数据
INSERT INTO `user` VALUES 
('1667e5003dac411b9668a43e1bdbe8cc', '2023-12-17 13:35:35', '2023-12-18 13:25:43', NULL, 'o7yGX4kanSwICk6R3Mes1U9hNY_0', '仓鼠不怕猫咪', 'https://th.bing.com/th/id/OIP.SF_aG_oJS2nwzVeRKn7R9AAAAA?w=196&h=196&c=7&r=0&o=7&dpr=1.5&pid=1.7&rm=3', 'https://img.yejiefeng.com/poster/d91a7d41ff0f480e8e8a471158a66c45', '左脑编程，右脑写诗', 'MAN', '', '', '', 1, NULL, '芬兰'),
('4e81a014c199449f9602ed264fb05663', '2023-12-17 13:00:07', NULL, NULL, 'o37HjWxF3fVLwe2UFweR7SWJd5R', 'wiki', 'https://th.bing.com/th/id/OIP.EQmg_yEaUKoAPR--nhMeWwAAAA?w=208&h=207&c=7&r=0&o=7&dpr=1.5&pid=1.7&rm=3', NULL, '爱生活，爱自然', 'WOMAN', '绍兴', '浙江', '中国', 0, NULL, '浙江'),
('7301687ab38e4e73a0a9eb6c28bcdc3b', '2023-12-29 12:45:28', '2023-12-29 12:56:36', NULL, 'o7yGX4ou0MpbtcgSZK2KCdGIEefp', '可可西里', 'https://img.yejiefeng.com/avatar/65189e5cb2f6470ab6645cd2f0b5071a', NULL, NULL, 'MAN', '', '', '', 0, NULL, NULL),
('82e7c8c3bee2481589c80a66ab429aea', '2023-12-17 13:01:34', NULL, NULL, 'oScas2xF3fVLWvsd2gbR7SffEVn', 'Eve', 'https://img.yejiefeng.com/avatar/dw2cew0d8-4t6u-gh8s-sca2-1sd2a9s5sd22', NULL, '我想要两颗西柚', 'MAN', '杭州', '浙江', '中国', 0, NULL, '上海'),
-- 开发测试用户
('d8e5ae1bc666459e856e0e05d6bbdcbf', '2025-10-25 00:00:00', NULL, NULL, 'test_openid_dev_001', 'kiki', 'https://c-ssl.dtstatic.com/uploads/blog/202301/24/20230124103727_88953.thumb.400_0.jpg', NULL, 'good', 'UN_KNOW', NULL, NULL, NULL, 0, NULL, NULL);

-- =============================================
-- 3. 情绪标签表 (新增)
-- =============================================
DROP TABLE IF EXISTS `emotion_label`;
CREATE TABLE `emotion_label` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `name` VARCHAR(20) NOT NULL COMMENT '标签名称',
  `icon` VARCHAR(256) DEFAULT NULL COMMENT '标签图标URL',
  `color` VARCHAR(7) DEFAULT '#337559' COMMENT '标签颜色',
  `type` ENUM('SYSTEM', 'CUSTOM') DEFAULT 'SYSTEM' COMMENT '标签类型：系统/自定义',
  `user_id` VARCHAR(32) DEFAULT NULL COMMENT '创建用户ID（自定义标签）',
  `use_count` INT DEFAULT 0 COMMENT '使用次数',
  `status` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_type` (`type`),
  INDEX `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='情绪标签表';

-- 插入系统默认情绪标签
INSERT INTO `emotion_label` (`id`, `name`, `icon`, `color`, `type`, `use_count`, `status`) VALUES
('8fda3742b16d11f0846e08bfb8c2c035', '开心', '😊', '#FFD700', 'SYSTEM', 0, 1),
('8fda3c1eb16d11f0846e08bfb8c2c035', '平静', '😌', '#87CEEB', 'SYSTEM', 0, 1),
('8fda489db16d11f0846e08bfb8c2c035', '难过', '😢', '#4682B4', 'SYSTEM', 0, 1),
('8fda4a8eb16d11f0846e08bfb8c2c035', '焦虑', '😰', '#FFA500', 'SYSTEM', 0, 1),
('8fda4b9eb16d11f0846e08bfb8c2c035', '愤怒', '😠', '#DC143C', 'SYSTEM', 0, 1),
('8fda4cdeb16d11f0846e08bfb8c2c035', '兴奋', '🤩', '#FF69B4', 'SYSTEM', 0, 1),
('8fda4dbeb16d11f0846e08bfb8c2c035', '疲惫', '😴', '#808080', 'SYSTEM', 0, 1),
('8fda4e81b16d11f0846e08bfb8c2c035', '感动', '🥺', '#FFB6C1', 'SYSTEM', 0, 1),
('8fda4f60b16d11f0846e08bfb8c2c035', '孤独', '😔', '#696969', 'SYSTEM', 0, 1),
('8fda5031b16d11f0846e08bfb8c2c035', '期待', '🤗', '#32CD32', 'SYSTEM', 0, 1);

-- =============================================
-- 4. 话题表 (扩展)
-- =============================================
DROP TABLE IF EXISTS `topic`;
CREATE TABLE `topic` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `title` VARCHAR(64) DEFAULT NULL COMMENT '标题',
  `content` VARCHAR(1024) NOT NULL COMMENT '内容',
  `is_anon` TINYINT(1) DEFAULT NULL COMMENT '是否匿名',
  `click_count` INT DEFAULT NULL COMMENT '点击次数',
  `images` JSON DEFAULT NULL COMMENT '图片',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户标识',
  `video_id` VARCHAR(32) DEFAULT NULL COMMENT '视频标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `ip_belong` VARCHAR(128) DEFAULT NULL COMMENT 'IP归属地',
  `star_count` INT DEFAULT NULL COMMENT '收藏次数',
  `comment_count` INT DEFAULT NULL COMMENT '评论次数',
  `emotion_label_id` VARCHAR(32) DEFAULT NULL COMMENT '情绪标签ID',
  PRIMARY KEY (`id`),
  KEY `ix_topic_user_id` (`user_id`),
  KEY `ix_topic_video_id` (`video_id`),
  KEY `ix_topic_create_time` (`create_time`),
  KEY `idx_emotion_label_id` (`emotion_label_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='话题表';

-- 插入示例话题数据
INSERT INTO `topic` VALUES 
('1693d2c3018a42b3a6b26df468016048', '2023-12-29 12:54:18', NULL, NULL, '初心易得，始终难守', 0, 1, '[\"http://t4dbz3ztq.hd-bkt.clouddn.com/avatar/55c32c03e9cd417082a9bcbc9dcf203e?e=1762177795&token=CVc4VEK1Zn4l46-rjGN_-lvV-ybYjQsEMJJewiDu:9Rrh2_OPfJmk0yZn9U2uIURSNoU=\"]', '4e81a014c199449f9602ed264fb05663', NULL, '2023-12-18 14:55:43', NULL, 0, 1, NULL),
('8bc105340e5443cd8e4860477e318197', '2023-12-18 14:21:34', NULL, NULL, '分享两只爱玩逗猫棒的喵喵！', 0, 83, '[\"http://t4dbz3ztq.hd-bkt.clouddn.com/avatar/53c4c8fd03e0461c9d3831b7d1cbd0a3?e=1762177058&token=CVc4VEK1Zn4l46-rjGN_-lvV-ybYjQsEMJJewiDu:1OJP9dsup0hNWVKm02gezNTBihQ=\"]', '1667e5003dac411b9668a43e1bdbe8cc', NULL, '2023-12-17 16:20:50', '上海', 1, 2, NULL),
('998bfea4d7814c0986d8ff07d990be78', '2023-12-29 12:49:13', NULL, NULL, 'nice。', 0, 4, '[]', '1667e5003dac411b9668a43e1bdbe8cc', NULL, '2023-12-18 16:51:39', NULL, 2, 1, NULL),
('b4c16d8d692f4399a831ea55c10240e9', NOW(), NULL, NULL, '今天天气晴', 0, 0, '[]', 'd8e5ae1bc666459e856e0e05d6bbdcbf', NULL, '2025-10-22 22:56:55', NULL, 0, 0, NULL),
('40c1b656b01545d6a20ad4b9e5c09397', NOW(), NULL, NULL, '心情好', 0, 0, '[]', 'd8e5ae1bc666459e856e0e05d6bbdcbf', NULL, '2025-10-25 15:30:06', NULL, 0, 0, '8fda3742b16d11f0846e08bfb8c2c035');

-- =============================================
-- 5. 标签表
-- =============================================
DROP TABLE IF EXISTS `label`;
CREATE TABLE `label` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `name` VARCHAR(32) NOT NULL COMMENT '名称',
  `allowed_anon` TINYINT(1) DEFAULT NULL COMMENT '是否可以匿名',
  `click_count` INT DEFAULT NULL COMMENT '点击次数',
  `priority` INT DEFAULT NULL COMMENT '优先级',
  PRIMARY KEY (`id`),
  KEY `ix_label_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='话题标签表';

-- 插入示例标签
INSERT INTO `label` VALUES 
('5683ad4d2a0b4c3f8aced7c2e3268e34', '2023-12-17 12:49:27', '2023-12-20 16:21:15', NULL, '工作', 0, 6, 68),
('6e98d7faed8d4f2bbb54674a7cac9430', '2023-12-17 12:49:54', '2023-12-18 14:52:38', NULL, '学习', 0, 5, 69),
('785c8cc53afd4151936d74ac52c177bc', '2023-12-17 12:49:39', '2023-12-20 16:21:14', NULL, '生活', 0, 11, 70),
('7baf91cdcc864d5e8ee9c8b8fd786cad', '2023-12-17 12:46:46', '2023-12-29 12:50:51', NULL, '旅游攻略', 0, 7, 100),
('a004f6e481634e0280fc7bedb625950a', '2023-12-17 12:48:58', '2023-12-29 12:52:26', NULL, '正能量', 0, 10, 80);

-- =============================================
-- 6. 话题标签关联表
-- =============================================
DROP TABLE IF EXISTS `topic_label_rel`;
CREATE TABLE `topic_label_rel` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `topic_id` VARCHAR(32) NOT NULL COMMENT '话题标识',
  `label_id` VARCHAR(32) NOT NULL COMMENT '标签标识',
  PRIMARY KEY (`id`),
  KEY `ix_topic_label_rel_create_time` (`create_time`),
  KEY `ix_topic_label_rel_label_id` (`label_id`),
  KEY `ix_topic_label_rel_topic_id` (`topic_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='话题标签关联表';

-- =============================================
-- 7. 收藏表 (扩展)
-- =============================================
DROP TABLE IF EXISTS `star`;
CREATE TABLE `star` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户标识',
  `topic_id` VARCHAR(32) NOT NULL COMMENT '话题标识',
  `interaction_type` ENUM('STAR', 'HUG', 'PAT') DEFAULT 'STAR' COMMENT '互动类型：收藏/拥抱/拍拍',
  PRIMARY KEY (`id`),
  KEY `ix_star_create_time` (`create_time`),
  KEY `ix_star_topic_id` (`topic_id`),
  KEY `ix_star_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='收藏表';

-- =============================================
-- 8. 评论表
-- =============================================
DROP TABLE IF EXISTS `comment`;
CREATE TABLE `comment` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `content` VARCHAR(256) NOT NULL COMMENT '内容',
  `is_anon` TINYINT(1) DEFAULT NULL COMMENT '是否匿名',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户标识',
  `topic_id` VARCHAR(32) NOT NULL COMMENT '话题标识',
  `comment_id` VARCHAR(32) DEFAULT NULL COMMENT '父评论标识',
  `ip_belong` VARCHAR(128) DEFAULT NULL COMMENT 'IP归属地',
  PRIMARY KEY (`id`),
  KEY `ix_comment_comment_id` (`comment_id`),
  KEY `ix_comment_create_time` (`create_time`),
  KEY `ix_comment_topic_id` (`topic_id`),
  KEY `ix_comment_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='评论表';

-- =============================================
-- 9. 消息表
-- =============================================
DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `content` VARCHAR(256) NOT NULL COMMENT '内容',
  `category` ENUM('COMMENT','FOLLOWING','STAR') DEFAULT NULL COMMENT '类型',
  `is_read` TINYINT(1) DEFAULT NULL COMMENT '是否已读',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户标识',
  `topic_id` VARCHAR(32) DEFAULT NULL COMMENT '话题标识',
  `action_user_id` VARCHAR(32) NOT NULL COMMENT '发起用户标识',
  `is_anon` TINYINT(1) DEFAULT NULL COMMENT '是否匿名',
  PRIMARY KEY (`id`),
  KEY `ix_message_create_time` (`create_time`),
  KEY `ix_message_topic_id` (`topic_id`),
  KEY `ix_message_user_id` (`user_id`),
  KEY `ix_message_action_user_id` (`action_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='消息表';

-- =============================================
-- 10. 关注表
-- =============================================
DROP TABLE IF EXISTS `following`;
CREATE TABLE `following` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户标识',
  `follow_user_id` VARCHAR(32) NOT NULL COMMENT '被关注用户标识',
  PRIMARY KEY (`id`),
  KEY `ix_following_create_time` (`create_time`),
  KEY `ix_following_follow_user_id` (`follow_user_id`),
  KEY `ix_following_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='关注表';

-- =============================================
-- 11. 视频表
-- =============================================
DROP TABLE IF EXISTS `video`;
CREATE TABLE `video` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  `src` VARCHAR(256) NOT NULL COMMENT '地址',
  `cover` VARCHAR(256) DEFAULT NULL COMMENT '封面',
  `width` INT DEFAULT NULL COMMENT '宽度',
  `height` INT DEFAULT NULL COMMENT '高度',
  `duration` INT DEFAULT NULL COMMENT '时长',
  `size` INT DEFAULT NULL COMMENT '大小',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户标识',
  `video_status` ENUM('REVIEWING','NORMAL','VIOLATION') DEFAULT NULL COMMENT '状态',
  PRIMARY KEY (`id`),
  KEY `ix_video_create_time` (`create_time`),
  KEY `ix_video_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='视频表';

-- =============================================
-- 12. 日记表 (新增)
-- =============================================
DROP TABLE IF EXISTS `diary`;
CREATE TABLE `diary` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `diary_date` DATE NOT NULL COMMENT '日记日期',
  `content` TEXT NOT NULL COMMENT '日记内容',
  `emotion_label_id` VARCHAR(32) DEFAULT NULL COMMENT '情绪标签ID',
  `is_public` TINYINT(1) DEFAULT 0 COMMENT '是否公开',
  `weather` VARCHAR(50) DEFAULT NULL COMMENT '天气',
  `location` VARCHAR(100) DEFAULT NULL COMMENT '地点',
  `images` JSON DEFAULT NULL COMMENT '图片列表',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_date` (`user_id`, `diary_date`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_diary_date` (`diary_date`),
  KEY `idx_emotion_label` (`emotion_label_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='日记表';

-- =============================================
-- 13. 心灵鸡汤推送记录表 (新增)
-- =============================================
DROP TABLE IF EXISTS `soul_push`;
CREATE TABLE `soul_push` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `content` TEXT NOT NULL COMMENT '推送内容',
  `source_type` ENUM('DIARY', 'TOPIC', 'EMOTION', 'RANDOM') DEFAULT 'RANDOM' COMMENT '来源类型',
  `source_id` VARCHAR(32) DEFAULT NULL COMMENT '来源ID',
  `emotion_label_id` VARCHAR(32) DEFAULT NULL COMMENT '情绪标签ID',
  `is_collected` TINYINT(1) DEFAULT 0 COMMENT '是否收藏',
  `llm_model` VARCHAR(50) DEFAULT NULL COMMENT '使用的LLM模型',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `delete_time` DATETIME DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_source` (`source_type`, `source_id`),
  KEY `idx_collected` (`is_collected`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='心灵鸡汤推送记录表';

-- =============================================
-- 14. 情绪统计表 (新增)
-- =============================================
DROP TABLE IF EXISTS `emotion_stat`;
CREATE TABLE `emotion_stat` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键标识',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `stat_date` DATE NOT NULL COMMENT '统计日期',
  `emotion_label_id` VARCHAR(32) NOT NULL COMMENT '情绪标签ID',
  `source_type` ENUM('DIARY', 'TOPIC') NOT NULL COMMENT '来源类型',
  `count` INT DEFAULT 1 COMMENT '次数',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_date` (`user_id`, `stat_date`),
  KEY `idx_emotion` (`emotion_label_id`),
  KEY `idx_source` (`source_type`),
  UNIQUE KEY `uk_user_date_emotion_source` (`user_id`, `stat_date`, `emotion_label_id`, `source_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='情绪统计表';

-- =============================================
-- 15. 创建视图：用户情绪趋势
-- =============================================
CREATE OR REPLACE VIEW `v_user_emotion_trend` AS
SELECT 
    es.user_id,
    es.stat_date,
    el.name AS emotion_name,
    el.color AS emotion_color,
    el.icon AS emotion_icon,
    SUM(es.count) AS total_count,
    es.source_type
FROM emotion_stat es
LEFT JOIN emotion_label el ON es.emotion_label_id = el.id
WHERE es.stat_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY es.user_id, es.stat_date, es.emotion_label_id, es.source_type
ORDER BY es.stat_date DESC;

-- =============================================
-- 16. 创建存储过程：更新情绪统计
-- =============================================
DROP PROCEDURE IF EXISTS `sp_update_emotion_stat`;

DELIMITER //

CREATE PROCEDURE `sp_update_emotion_stat`(
    IN p_user_id VARCHAR(32),
    IN p_emotion_label_id VARCHAR(32),
    IN p_source_type ENUM('DIARY', 'TOPIC'),
    IN p_stat_date DATE
)
BEGIN
    DECLARE v_id VARCHAR(32);
    
    -- 检查是否已存在记录
    SELECT id INTO v_id 
    FROM emotion_stat 
    WHERE user_id = p_user_id 
        AND emotion_label_id = p_emotion_label_id 
        AND source_type = p_source_type 
        AND stat_date = p_stat_date
    LIMIT 1;
    
    IF v_id IS NOT NULL THEN
        -- 更新计数
        UPDATE emotion_stat 
        SET count = count + 1, 
            update_time = NOW()
        WHERE id = v_id;
    ELSE
        -- 插入新记录
        INSERT INTO emotion_stat (id, user_id, emotion_label_id, source_type, stat_date, count)
        VALUES (REPLACE(UUID(), '-', ''), p_user_id, p_emotion_label_id, p_source_type, p_stat_date, 1);
    END IF;
END //

DELIMITER ;

-- =============================================
-- 17. 触发器已禁用说明
-- =============================================
-- 注意：为避免开发环境字符集冲突，触发器已禁用
-- 如需启用自动情绪统计功能，请在生产环境执行以下触发器创建语句：
--
-- DELIMITER //
-- CREATE TRIGGER `tr_topic_emotion_stat_insert` 
-- AFTER INSERT ON `topic`
-- FOR EACH ROW
-- BEGIN
--     IF NEW.emotion_label_id IS NOT NULL THEN
--         CALL sp_update_emotion_stat(NEW.user_id, NEW.emotion_label_id, 'TOPIC', DATE(NEW.create_time));
--     END IF;
-- END //
-- DELIMITER ;
--
-- DELIMITER //
-- CREATE TRIGGER `tr_diary_emotion_stat_insert` 
-- AFTER INSERT ON `diary`
-- FOR EACH ROW
-- BEGIN
--     IF NEW.emotion_label_id IS NOT NULL THEN
--         CALL sp_update_emotion_stat(NEW.user_id, NEW.emotion_label_id, 'DIARY', NEW.diary_date);
--     END IF;
-- END //
-- DELIMITER ;

-- =============================================
-- 18. 创建索引优化查询性能
-- =============================================
CREATE INDEX `idx_user_emotion_time` ON `emotion_stat` (`user_id`, `stat_date`, `emotion_label_id`);
CREATE INDEX `idx_diary_user_public` ON `diary` (`user_id`, `is_public`, `delete_time`);
CREATE INDEX `idx_soul_push_user_time` ON `soul_push` (`user_id`, `create_time`);

-- =============================================
-- 完成
-- =============================================
SET FOREIGN_KEY_CHECKS = 1;

SELECT '=' AS '', '========================================' AS '', '=' AS '';
SELECT '=' AS '', '  数据库初始化完成！' AS '', '=' AS '';
SELECT '=' AS '', '  Database: july' AS '', '=' AS '';
SELECT '=' AS '', '  Charset: utf8mb4_general_ci' AS '', '=' AS '';
SELECT '=' AS '', '  Version: v2.0 Final' AS '', '=' AS '';
SELECT '=' AS '', '========================================' AS '', '=' AS '';
SELECT '' AS '';
SELECT '已创建的表:' AS info;
SELECT TABLE_NAME AS '表名', TABLE_COMMENT AS '说明' 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'july' AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

SELECT '' AS '';
SELECT '数据库部署完成，可以启动服务器了！' AS message;

