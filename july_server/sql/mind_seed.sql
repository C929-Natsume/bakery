-- 初始化心灵配方示例数据（仅用于本地开发）
-- 可反复执行，依赖唯一标题去重插入
INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '认识焦虑：症状、成因与自助方法', '["焦虑","科普"]', '中国心理学会科普工作委员会', '科普', '焦虑是对未来威胁的警觉与担心……（内容占位）', 128
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='认识焦虑：症状、成因与自助方法');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '抑郁情绪的识别与求助指南', '["抑郁","求助"]', 'WHO 心理健康指南', '指南', '持续两周以上的低落、兴趣减退、睡眠饮食改变……（内容占位）', 96
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='抑郁情绪的识别与求助指南');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '睡眠卫生：提高睡眠质量的10个建议', '["睡眠","行为建议"]', 'NIMH 睡眠建议', '建议', '固定作息、睡前减少电子设备、咖啡因限制……（内容占位）', 210
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='睡眠卫生：提高睡眠质量的10个建议');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '认知重建：识别与修正消极自动化思维', '["认知行为疗法","技巧"]', 'CBT 实践手册', '技巧', '识别常见思维谬误：过度概括、非黑即白、灾难化……（内容占位）', 88
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='认知重建：识别与修正消极自动化思维');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '压力管理：ABCDE 技术与呼吸放松', '["压力","放松"]', '心理咨询基础', '训练', 'ABCDE：触发-信念-后果-辩论-效果；配合腹式呼吸训练……（内容占位）', 77
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='压力管理：ABCDE 技术与呼吸放松');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '人际界限：学会说“否”的三步法', '["人际","自我保护"]', '人际沟通技巧', '技巧', '表达事实-表达感受-提出请求，保持尊重而坚定……（内容占位）', 65
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='人际界限：学会说“否”的三步法');
