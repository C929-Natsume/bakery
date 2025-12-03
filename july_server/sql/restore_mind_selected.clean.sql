-- Restore selected mind_knowledge rows from seed data
-- Each block inserts only if a row with same title does not exist

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''),
       '时间管理：四象限与能量曲线',
       '["时间管理","执行功能"]',
       '效率工具',
       '工具',
       '四象限法将任务按重要/紧急分类，优先处理重要且紧急事项并为重要非紧急事项安排时间。结合个人能量曲线在高效时段安排深度工作，有助于效率与精力管理。',
       54
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title = '时间管理：四象限与能量曲线');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''),
       '自我关怀清单：身心需要的 ABC',
       '["自我关怀","情绪调节"]',
       '心理自助',
       '工具',
       '自我关怀包括三个层面：身体关照（充足睡眠、营养与运动），情绪关照（允许并表达情绪、寻求安抚），以及认知关照（温和的自我对话与重评）。日常小行动如短暂休息与边界设定即为有效自我关怀实践。',
       52
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title = '自我关怀清单：身心需要的 ABC');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''),
       '成瘾恢复：诱发因素日记',
       '["成瘾","复发预防"]',
       '临床指南',
       '工具',
       '成瘾恢复中使用诱发因素日记，记录“人物-地点-情绪-想法-行为”五维信息，帮助识别复发链条并提前规划替代行为或应对策略。与支持人员共享计划并定期评估能提升执行力。',
       60
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title = '成瘾恢复：诱发因素日记');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''),
       '人际界限：学会说"否"的三步法',
       '["人际","自我保护"]',
       '人际沟通技巧',
       '技巧',
       '学会设置界限可保护心理资源。三步法为：首先陈述事实（描述具体情境），其次表达感受或需求，最后明确提出可接受的请求或替代方案。练习时保持语气平和、言辞具体，有助于既维护关系又保护自我界限。',
       65
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title = '人际界限：学会说"否"的三步法');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''),
       '正念冥想：5 分钟呼吸练习',
       '["正念","放松"]',
       'MBSR 练习',
       '训练',
       '找一个安静的坐姿，闭或半闭眼，关注呼吸的进出。每当注意力分散时，不评判地将其温和带回呼吸上。此练习每日 5 分钟即可开始，长期坚持能提升当下感与情绪稳定。',
       52
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title = '正念冥想：5 分钟呼吸练习');
