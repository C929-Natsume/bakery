# -*- coding: utf-8 -*-
"""
向数据库写入“心灵配方”示例数据（幂等，可重复执行）。
使用方式（Windows PowerShell）：
  .\\july_server\\.venv\\Scripts\\python.exe .\\july_server\\scripts\\seed_mind.py
"""
import json
from app import create_app
from app.model.base import db
from app.model.mind import MindKnowledge

SEEDS = [
    {
        'title': '认识焦虑：症状、成因与自助方法',
        'tags': ['焦虑', '科普'],
        'source': '中国心理学会科普工作委员会',
        'category': '科普',
        'content': '焦虑是对未来威胁的警觉与担心……（内容占位）',
        'read_count': 128
    },
    {
        'title': '抑郁情绪的识别与求助指南',
        'tags': ['抑郁', '求助'],
        'source': 'WHO 心理健康指南',
        'category': '指南',
        'content': '持续两周以上的低落、兴趣减退、睡眠饮食改变……（内容占位）',
        'read_count': 96
    },
    {
        'title': '睡眠卫生：提高睡眠质量的10个建议',
        'tags': ['睡眠', '行为建议'],
        'source': 'NIMH 睡眠建议',
        'category': '建议',
        'content': '固定作息、睡前减少电子设备、咖啡因限制……（内容占位）',
        'read_count': 210
    },
    {
        'title': '认知重建：识别与修正消极自动化思维',
        'tags': ['认知行为疗法', '技巧'],
        'source': 'CBT 实践手册',
        'category': '技巧',
        'content': '识别常见思维谬误：过度概括、非黑即白、灾难化……（内容占位）',
        'read_count': 88
    },
    {
        'title': '压力管理：ABCDE 技术与呼吸放松',
        'tags': ['压力', '放松'],
        'source': '心理咨询基础',
        'category': '训练',
        'content': 'ABCDE：触发-信念-后果-辩论-效果；配合腹式呼吸训练……（内容占位）',
        'read_count': 77
    },
    {
        'title': '人际界限：学会说“否”的三步法',
        'tags': ['人际', '自我保护'],
        'source': '人际沟通技巧',
        'category': '技巧',
        'content': '表达事实-表达感受-提出请求，保持尊重而坚定……（内容占位）',
        'read_count': 65
    },
    # 追加：权威与常见主题（14 条），可幂等插入
    {
        'title': '正念冥想：5 分钟呼吸练习',
        'tags': ['正念', '放松'],
        'source': 'MBSR 练习',
        'category': '训练',
        'content': '安静坐姿，将注意力温和带回呼吸的进出，分心时不评判地拉回……（内容占位）',
        'read_count': 52
    },
    {
        'title': '运动与心理健康：每周 150 分钟',
        'tags': ['运动', '生活方式'],
        'source': 'WHO 建议',
        'category': '建议',
        'content': '中等强度有氧运动每周 150 分钟可显著改善情绪与睡眠质量……（内容占位）',
        'read_count': 73
    },
    {
        'title': '社交焦虑自助：暴露与安全行为识别',
        'tags': ['焦虑', '暴露疗法'],
        'source': 'CBT 技术',
        'category': '技巧',
        'content': '列出回避/安全行为，分级面对社交情境，记录期待与实际结果差异……（内容占位）',
        'read_count': 68
    },
    {
        'title': '惊恐发作应对卡片',
        'tags': ['惊恐', '呼吸'],
        'source': '临床建议',
        'category': '指南',
        'content': '识别症状是无害的生理反应；进行缓慢呼吸与地面化技巧，等待峰值自然消退……（内容占位）',
        'read_count': 81
    },
    {
        'title': '复原力：意义-联结-掌控三柱模型',
        'tags': ['复原力', '积极心理'],
        'source': '心理学会科普',
        'category': '科普',
        'content': '通过明确价值与目标、建立支持网络、提升可控性来增强逆境适应……（内容占位）',
        'read_count': 44
    },
    {
        'title': '情绪日记：ABC 记录表模板',
        'tags': ['记录', '认知行为'],
        'source': 'CBT 工具',
        'category': '工具',
        'content': 'A 触发事件、B 信念、C 情绪后果；增加 D 驳斥 与 E 新效果，促进认知重评……（内容占位）',
        'read_count': 59
    },
    {
        'title': '失眠的刺激控制法',
        'tags': ['睡眠', '失眠'],
        'source': '睡眠医学建议',
        'category': '指南',
        'content': '困了再上床；仅将床用于睡眠；睡不着 20 分钟起身做安静活动，困了再回床……（内容占位）',
        'read_count': 97
    },
    {
        'title': '青少年情绪波动与求助途径',
        'tags': ['青少年', '家庭'],
        'source': '儿少心理科普',
        'category': '科普',
        'content': '青春期情绪起伏常见；当持续影响学习与关系时，尽早与家长/老师/专业人士沟通……（内容占位）',
        'read_count': 58
    },
    {
        'title': '悲伤与哀悼：正常过程与照料',
        'tags': ['哀伤', '适应'],
        'source': '临床心理建议',
        'category': '科普',
        'content': '否认-愤怒-讨价还价-抑郁-接受并非线性；允许情绪、维持日常、寻求支持……（内容占位）',
        'read_count': 42
    },
    {
        'title': '自杀风险识别五个信号与干预热线',
        'tags': ['危机', '预防'],
        'source': '公共卫生科普',
        'category': '指南',
        'content': '谈及死亡/绝望、剧烈情绪波动、告别/遗物处理等为警示信号；请立即联系当地危机干预热线或急救……（内容占位）',
        'read_count': 120
    },
    {
        'title': '物质成瘾：渴求管理与复发预防',
        'tags': ['成瘾', '复发预防'],
        'source': '临床指南',
        'category': '技巧',
        'content': '识别高风险线索与情境，运用延迟/分散/替代策略，建立支持计划与危机预案……（内容占位）',
        'read_count': 55
    },
    {
        'title': '注意力训练：番茄工作法与环境优化',
        'tags': ['注意力', '执行功能'],
        'source': '时间管理方法',
        'category': '工具',
        'content': '25 分钟专注 + 5 分钟休息；降低干扰、明确单一任务、外化待办清单……（内容占位）',
        'read_count': 64
    },
    {
        'title': '家庭沟通：非暴力沟通四要素',
        'tags': ['人际', '家庭'],
        'source': 'NVC',
        'category': '技巧',
        'content': '观察-感受-需要-请求；用我信息表达，不贴标签不指责，关注具体可行请求……（内容占位）',
        'read_count': 70
    },
    {
        'title': '情绪调节：RULER 模型入门',
        'tags': ['情绪调节', 'SEL'],
        'source': 'SEL 框架',
        'category': '科普',
        'content': '识别-理解-标记-表达-调节（RULER）；结合情绪温度计与情境策略库……（内容占位）',
        'read_count': 39
    },
    {
        'title': '职场压力：需求-控制-支持模型',
        'tags': ['职场', '压力'],
        'source': '职场心理',
        'category': '科普',
        'content': '高需求低控制是高压源；通过提升可控性与社会支持来缓冲压力影响……（内容占位）',
        'read_count': 63
    },
    {
        'title': '完美主义：识别标准与设定可行目标',
        'tags': ['完美主义', '目标设定'],
        'source': 'CBT 技术',
        'category': '技巧',
        'content': '区分高标准与僵化标准；采用 SMART 目标与渐进式暴露于“不完美”……（内容占位）',
        'read_count': 66
    },
    # 进一步扩充各分类/标签（10 条）
    {
        'title': '焦虑的身体信号与认知解读',
        'tags': ['焦虑', '科普'],
        'source': '心理科普',
        'category': '科普',
        'content': '心跳加速、出汗、肌肉紧张是战斗或逃跑反应，不等于危险正在发生……（内容占位）',
        'read_count': 41
    },
    {
        'title': '抑郁自评与就医指南（PHQ-9）',
        'tags': ['抑郁', '筛查'],
        'source': '公共卫生',
        'category': '指南',
        'content': 'PHQ-9 仅作初筛；如评分偏高或功能受损，请尽快就医评估与干预……（内容占位）',
        'read_count': 88
    },
    {
        'title': '睡前仪式感：放松清单模板',
        'tags': ['睡眠', '工具'],
        'source': '睡眠卫生',
        'category': '工具',
        'content': '温水泡脚、轻度拉伸、呼吸训练、低照度环境，固定时间上床……（内容占位）',
        'read_count': 72
    },
    {
        'title': '压力缓冲：社会支持地图',
        'tags': ['压力', '社交'],
        'source': '积极心理',
        'category': '工具',
        'content': '绘制个人支持网络（家庭/朋友/同事/专业资源），明确可以求助的具体人和方式……（内容占位）',
        'read_count': 47
    },
    {
        'title': '人际冲突的“暂停-复述-共情-协商”',
        'tags': ['人际', '沟通'],
        'source': '沟通技巧',
        'category': '技巧',
        'content': '先暂停情绪、复述对方要点、表达共情，再进入方案协商，尽量提出可选项……（内容占位）',
        'read_count': 58
    },
    {
        'title': '正念步行：关注足部触地感',
        'tags': ['正念', '训练'],
        'source': 'MBSR',
        'category': '训练',
        'content': '慢速行走时，将注意力放在脚掌触地与抬起的感觉，思绪飘走时温和带回……（内容占位）',
        'read_count': 53
    },
    {
        'title': '青少年亲子冲突的界限设定',
        'tags': ['青少年', '家庭'],
        'source': '家庭治疗',
        'category': '指南',
        'content': '明确家庭规则与后果，正向关注与一致执行，鼓励表达与协商……（内容占位）',
        'read_count': 46
    },
    {
        'title': '工作倦怠：情绪耗竭-去人格化-低成就感',
        'tags': ['职场', '倦怠'],
        'source': '职业健康',
        'category': '科普',
        'content': '三维度识别倦怠；建议与上级沟通负荷、进行任务分解与恢复性安排……（内容占位）',
        'read_count': 61
    },
    {
        'title': '创伤触发识别与地面化技巧',
        'tags': ['创伤', '地面化'],
        'source': '创伤治疗',
        'category': '技巧',
        'content': '5-4-3-2-1 感官锚定、手持冰块、关注脚踏地面，用以降低侵入性记忆带来的激活……（内容占位）',
        'read_count': 75
    },
    {
        'title': '饮食与情绪：规律进食与血糖稳定',
        'tags': ['饮食', '生活方式'],
        'source': '营养与心理',
        'category': '建议',
        'content': '均衡膳食与规律进食有助于维持能量与情绪稳定，避免空腹与高糖暴食循环……（内容占位）',
        'read_count': 50
    },
    # 再补 12 条，覆盖标签：创伤/亲密关系/孕产/考试/社交/时间管理/睡眠/成瘾/复原力/自我关怀/悲伤/注意力
    {
        'title': '考试焦虑：模拟暴露与放松结合',
        'tags': ['焦虑', '考试'],
        'source': '学生心理指南',
        'category': '技巧',
        'content': '在可控环境下模拟考试情境，配合呼吸/肌肉放松，逐步降低生理与认知激活……（内容占位）',
        'read_count': 67
    },
    {
        'title': '社交自我表露的层级法',
        'tags': ['社交', '人际'],
        'source': '人际技巧',
        'category': '技巧',
        'content': '从兴趣爱好等低风险话题逐级到情绪与价值观，匹配对方开放程度……（内容占位）',
        'read_count': 49
    },
    {
        'title': '亲密关系的情绪验证',
        'tags': ['亲密关系', '沟通'],
        'source': '关系修复',
        'category': '技巧',
        'content': '先命名对方情绪并表达理解，再进入问题解决；避免立即给建议或反驳……（内容占位）',
        'read_count': 62
    },
    {
        'title': '产后情绪波动与求助清单',
        'tags': ['孕产', '抑郁'],
        'source': '妇幼健康',
        'category': '指南',
        'content': '区分产后忧郁与产后抑郁；若持续两周以上或影响功能，应及时就医并寻求家人支持……（内容占位）',
        'read_count': 71
    },
    {
        'title': '时间管理：四象限与能量曲线',
        'tags': ['时间管理', '执行功能'],
        'source': '效率工具',
        'category': '工具',
        'content': '重要紧急四象限安排任务；结合个人能量高峰时段安排深度工作……（内容占位）',
        'read_count': 54
    },
    {
        'title': '睡眠限制疗法：逐步延长床上时间',
        'tags': ['睡眠', '失眠'],
        'source': '睡眠医学',
        'category': '指南',
        'content': '初始以平均睡眠时长设定就寝时段，睡效提升后逐步延长，避免长时间卧床清醒……（内容占位）',
        'read_count': 83
    },
    {
        'title': '复原力练习：感恩三件事',
        'tags': ['复原力', '积极心理'],
        'source': '积极心理',
        'category': '训练',
        'content': '每日记录三件值得感恩的小事，帮助大脑捕捉积极线索，平衡消极偏向……（内容占位）',
        'read_count': 45
    },
    {
        'title': '自我关怀清单：身心需要的 ABC',
        'tags': ['自我关怀', '情绪调节'],
        'source': '心理自助',
        'category': '工具',
        'content': 'A 身体关照（饮食/睡眠/活动），B 情绪关照（表达/安抚），C 认知关照（重评/自我对话）……（内容占位）',
        'read_count': 52
    },
    {
        'title': '悲伤周年反应：提前准备与纪念仪式',
        'tags': ['哀伤', '适应'],
        'source': '临床建议',
        'category': '指南',
        'content': '周年反应可能加重情绪；可安排纪念仪式、与支持者相伴，并降低负荷……（内容占位）',
        'read_count': 38
    },
    {
        'title': '注意力分散的环境改造',
        'tags': ['注意力', '环境'],
        'source': '执行功能',
        'category': '建议',
        'content': '减少手机干扰、清理桌面、准备噪音耳机/白噪音、设置番茄钟……（内容占位）',
        'read_count': 57
    },
    {
        'title': '成瘾恢复：诱发因素日记',
        'tags': ['成瘾', '复发预防'],
        'source': '临床指南',
        'category': '工具',
        'content': '记录“人物-地点-情绪-想法-行为”五维线索，识别复发链条并制定替代行为……（内容占位）',
        'read_count': 60
    },
    {
        'title': '创伤后梦魇的影像排练法',
        'tags': ['创伤', '睡眠'],
        'source': '治疗技术',
        'category': '技巧',
        'content': '在安全环境中重写梦魇剧本并反复排练，减少噩梦频率和强度……（内容占位）',
        'read_count': 69
    }
]


def main():
    app = create_app()
    with app.app_context():
        inserted = 0
        for s in SEEDS:
            exist = MindKnowledge.get_one(title=s['title'])
            if exist:
                continue
            MindKnowledge.create(
                title=s['title'],
                content=s['content'],
                tags=json.dumps(s['tags'], ensure_ascii=False),
                source=s.get('source'),
                category=s.get('category'),
                read_count=s.get('read_count', 0)
            )
            inserted += 1
        db.session.commit()
        print(f"mind_knowledge seeded. inserted={inserted}")


if __name__ == '__main__':
    main()
