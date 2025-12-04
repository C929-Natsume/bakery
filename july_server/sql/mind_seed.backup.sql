-- Backup of mind_seed.sql created before replacement

-- Original content saved for safety. If needed, restore by copying this file back to mind_seed.sql

-- (file begins below)

-- 初始化心灵配方示例数据（仅用于本地开发）
-- 可反复执行，依赖唯一标题去重插入
-- 注意：此 SQL 文件为历史备份。项目已经将“详尽正文生成”逻辑移入
-- `july_server/app/lib/mind_content_generator.py`，请优先使用
-- `python -m scripts.seed_mind` 在应用上下文中（并在虚拟环境中安装依赖）
-- 以批量生成 600–800 字的扩写内容并写入数据库。SQL 文件可能未包含最新扩写文本.
INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '认识焦虑：症状、成因与自助方法', '["焦虑","科普"]', '中国心理学会科普工作委员会', '科普', '焦虑是一种面对未知或可能的威胁时产生的警觉和担心。常见表现包括心跳加速、出汗、注意力受损与睡眠困难。成因通常由遗传易感性、环境压力与认知偏差共同作用。自助方法包括规律作息、呼吸与放松训练、分步暴露不适情境以及记录并挑战灾难化想法；若影响日常功能，建议及时寻求专业评估与支持。', 128
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='认识焦虑：症状、成因与自助方法');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '抑郁情绪的识别与求助指南', '["抑郁","求助"]', 'WHO 心理健康指南', '指南', '抑郁是一种以持续低落心情、兴趣或快感丧失、能量下降为核心的状态，常伴随睡眠与食欲改变、负性自评与注意力受损。若这些症状持续两周以上并影响学习或工作，应重视并寻求评估。初步自助可包括活动安排（行为激活）、规律作息与社会支持；严重时可考虑专业心理治疗或药物治疗，并联系当地心理卫生资源或危机干预热线。', 96
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='抑郁情绪的识别与求助指南');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '睡眠卫生：提高睡眠质量的10个建议', '["睡眠","行为建议"]', 'NIMH 睡眠建议', '建议', '改善睡眠的关键在于睡眠卫生：保持固定的就寝与起床时间，睡前一小时减少屏幕与强刺激活动，限制咖啡因与酒精摄入，创造安静黑暗的睡眠环境。白天适度运动与避免长时间午睡也有帮助。若长期失眠影响日常功能，可尝试睡眠限制疗法与认知行为治疗（CBT-I），必要时寻求专业睡眠医学评估。', 210
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='睡眠卫生：提高睡眠质量的10个建议');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '认知重建：识别与修正消极自动化思维', '["认知行为疗法","技巧"]', 'CBT 实践手册', '技巧', '认知重建旨在识别自动出现的负面想法（如灾难化、过度概括）并通过证据检验与替代性解释来修正。实践步骤包括记录触发事件、自动思维和证据；提出更平衡的替代想法并在日常中练习。长期练习可减少情绪困扰并提升行为适应性。', 88
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='认知重建：识别与修正消极自动化思维');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '压力管理：ABCDE 技术与呼吸放松', '["压力","放松"]', '心理咨询基础', '训练', 'ABCDE 即识别触发事件（A）、辨认信念（B）、理解后果（C）、对信念进行辩论（D）并观察效果（E）。配合腹式呼吸或渐进性肌肉放松练习，可在紧张时刻快速调节生理激活。建议将这些技术作为常规工具，在压力情境中有意识地练习并记录效果。', 77
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='压力管理：ABCDE 技术与呼吸放松');

INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)
SELECT REPLACE(UUID(),'-',''), '人际界限：学会说“否”的三步法', '["人际","自我保护"]', '人际沟通技巧', '技巧', '学会设置界限可保护心理资源。三步法为：首先陈述事实（描述具体情境），其次表达感受或需求，最后明确提出可接受的请求或替代方案。练习时保持语气平和、言辞具体，有助于既维护关系又保护自我界限。', 65
WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title='人际界限：学会说“否”的三步法');
