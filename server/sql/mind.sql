-- Mind feature tables
CREATE TABLE IF NOT EXISTS `mind_knowledge` (
  `id` varchar(32) NOT NULL COMMENT '主键标识',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `delete_time` datetime DEFAULT NULL COMMENT '删除时间',
  `title` varchar(128) NOT NULL COMMENT '标题',
  `tags` text DEFAULT NULL COMMENT '标签(JSON字符串)',
  `source` varchar(64) DEFAULT NULL COMMENT '来源',
  `category` varchar(32) DEFAULT NULL COMMENT '分类',
  `content` longtext NOT NULL COMMENT '内容',
  `read_count` int DEFAULT 0 COMMENT '阅读数',
  PRIMARY KEY (`id`),
  KEY `idx_mind_title` (`title`),
  KEY `idx_mind_category` (`category`),
  KEY `idx_mind_create` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='心灵配方-知识';

CREATE TABLE IF NOT EXISTS `mind_star` (
  `id` varchar(32) NOT NULL COMMENT '主键标识',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `delete_time` datetime DEFAULT NULL COMMENT '删除时间',
  `user_id` varchar(32) NOT NULL COMMENT '用户ID',
  `knowledge_id` varchar(32) NOT NULL COMMENT '知识ID',
  UNIQUE KEY `uq_mind_star_user_knowledge` (`user_id`,`knowledge_id`),
  KEY `idx_mind_star_user` (`user_id`),
  KEY `idx_mind_star_knowledge` (`knowledge_id`),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='心灵配方-收藏';