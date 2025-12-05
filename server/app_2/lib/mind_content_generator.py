# -*- coding: utf-8 -*-
"""
轻量级心理知识正文生成器（用于开发环境种子与 API 后备内容的批量扩写）。
该模块基于条目标题、标签与来源合成原创性的结构化文本，长度目标 600-800 字。
不会抓取或复制外部受版权保护文本，仅会在结尾附上公开来源链接作为参考。
"""
from typing import List

REF_MAP = {
    'WHO': 'https://www.who.int/health-topics/mental-health',
    'WHO 心理健康指南': 'https://www.who.int/health-topics/mental-health',
    'NIMH': 'https://www.nimh.nih.gov/health/topics',
    '中国心理学会科普工作委员会': 'http://www.cpa.org.cn',
    '中国心理学会': 'http://www.cpa.org.cn',
    '国家卫生健康委员会': 'http://www.nhc.gov.cn',
    '睡眠医学': 'https://www.sleepfoundation.org/',
}


def _join_paragraphs(paragraphs: List[str]) -> str:
    return "\n\n".join(p.strip() for p in paragraphs if p and p.strip())


def generate_content(title: str, tags: List[str] = None, source: str = None) -> str:
    """
    基于标题、标签与来源合成一段 600–800 字的中文原创性心理科普/指南文本。
    返回值已包含分段。此函数尽量通用以覆盖大多数条目类型。
    """
    tags = tags or []
    # 简短描述（定义 / 概述）
    intro = f"{title}。" if title else "本条内容介绍相关心理主题。"
    intro += (
        " 本文从定义、常见表现、可能成因、自助与何时寻求专业帮助等方面，" 
        "为你提供实用可行的建议，便于在日常情境中应用与判断。"
    )

    # 常见表现（根据标签推断）
    presents = []
    if any(t for t in tags if '焦虑' in t or '惊恐' in t):
        presents.append("常见的体验包括紧张不安、心跳加速、呼吸急促、注意力分散与睡眠困难；情绪上可能伴随担忧、易怒或回避倾向。")
    if any(t for t in tags if '抑郁' in t):
        presents.append("抑郁通常表现为持续性低落、兴趣明显下降、精力不足、睡眠与食欲改变以及负性自评。")
    if any(t for t in tags if '睡眠' in t):
        presents.append("睡眠相关问题常见为入睡困难、维持睡眠能力下降、或醒后疲惫感，白天可能出现注意力下降与情绪波动。")
    if any(t for t in tags if '人际' in t or '沟通' in t):
        presents.append("在人际情境中，表现可能为回避、冲突升级、无法表达需求或边界模糊。")
    if not presents:
        presents.append("个体可能在情绪、认知或行为层面出现不同程度的困扰，影响日常学习、工作与人际。")

    # 可能成因（通用化）
    causes = (
        "其成因往往为生物、心理与社会环境多因素共同作用：包括遗传易感性、长期压力或突发事件、睡眠与生活方式失衡、以及对事件的认知加工方式。"
    )

    # 自助建议（可操作）
    self_help = (
        "可行的自助策略包括：一是建立规律的作息与适量运动，二是练习基础的呼吸与放松训练以调节生理激活，"
        "三是将困扰拆分为可执行的小目标并逐步暴露于不适情境以降低回避，四是使用情绪记录或认知重建来检视与挑战极端化想法。"
    )

    # 何时寻求专业帮助
    when = (
        "当上述策略无法改善、症状持续并明显影响到学习、工作或人际功能，或出现自伤/自杀想法时，应尽快联系心理健康专业人员或急救服务。"
    )

    # 参考链接（基于 source 或通用权威）
    ref = None
    if source and source in REF_MAP:
        ref = REF_MAP[source]
    else:
        # 优先 WHO / 国家/中文心理学会
        if 'WHO' in (source or '') or any('WHO' == t for t in tags):
            ref = REF_MAP.get('WHO')
        elif '睡眠' in (" ".join(tags)):
            ref = REF_MAP.get('睡眠医学')
        else:
            # 默认使用中国心理学会或国家卫生健康委员会作为参考
            ref = REF_MAP.get('中国心理学会') or REF_MAP.get('国家卫生健康委员会')

    ref_line = f"参考与延伸阅读：{ref}" if ref else "参考与延伸阅读：请参见本地卫生与心理健康机构的权威指南。"

    paragraphs = [intro, _join_paragraphs(presents), causes, self_help, when, ref_line]
    full = _join_paragraphs(paragraphs)

    # 目标长度：600-800 字（汉字）。如果不足则补充"日常可做"的小步骤，风格根据标签调整
    target_min = 600
    if len(full) < target_min:
        def _daily_steps(tags):
            t = ' '.join(tags or [])
            # 焦虑/惊恐类——短时减压与具体行为
            if '焦虑' in t or '惊恐' in t:
                return (
                    "日常可做的小步骤（易执行）：\n"
                    "1) 先做一件小事：花 10 分钟整理桌面或清理一封邮件，完成后给自己一个小奖励；\n"
                    "2) 设定 5 分钟的呼吸练习（吸 4 秒、呼 6 秒），坐着完成并把注意力放回当下；\n"
                    "3) 写下此刻最烦恼的一件事，并列出 1–2 个能马上做的小动作来减少焦虑；\n"
                    "4) 今天尝试与一位信任的人说一句真实的感受，获得支持。"
                )
            # 抑郁类——行为激活与温和计划
            if '抑郁' in t:
                return (
                    "日常可做的小步骤（温和可持续）：\n"
                    "1) 设定当日三小任务（例如：喝一杯水、出门散步 10 分钟、给好友发一条消息），完成任意两个就算成功；\n"
                    "2) 把一天分块，用手机计时法给自己 20 分钟专注休息或做喜欢的小事；\n"
                    "3) 在日记里写下一件让你感激的事，哪怕很小；\n"
                    "4) 若感到太沉重，拨打本地心理支持热线或联系家庭/朋友寻求陪伴。"
                )
            # 睡眠类——就寝前的简单流程
            if '睡眠' in t:
                return (
                    "今晚就能做的睡前步骤：\n"
                    "1) 提前 30 分钟关闭手机通知，做 5 分钟轻度拉伸；\n"
                    "2) 喝一杯温水（非含咖啡因），把房间调暗，保持舒适温度；\n"
                    "3) 在床上若 20 分钟未入睡，起身做一项轻松活动再回床；\n"
                    "4) 明早记录睡眠时间与醒来感受，连续 7 天观察变化。"
                )
            # 人际/沟通类——练习表达与界限
            if '人际' in t or '沟通' in t:
                return (
                    "日常练习（可当作社交小实验）：\n"
                    "1) 今天选择一次场景练习'我信息'：用一句话表达你的感受和需要（例如：我今天有点累，能否晚一点讨论？）；\n"
                    "2) 练习说'不'的简短版本，例如：谢谢你的邀请，但我这次不能参加；\n"
                    "3) 记录对方反应与自己的感受，作为下次调整的依据；\n"
                    "4) 给自己设一项小奖励以强化练习行为。"
                )
            # 默认更日常的建议
            return (
                "日常可做的小步骤：\n"
                "1) 先从 10 分钟的简单任务开始（如收拾一角落、整理待办），体验完成感；\n"
                "2) 做 3 次深呼吸（缓慢吸气 4 秒，呼气 6 秒），观察身体放松程度；\n"
                "3) 写下今天一件让你感到安慰的小事；\n"
                "4) 若需要，联系一位可以倾听你的朋友或专业人员。"
            )

        # 将日常步骤插入正文末尾，避免机械重复同一措辞
        extra = _daily_steps(tags)
        # 添加一个温和的"贴士"结尾，按条目类型略作变化
        tip = "小贴士：若情绪持续或出现危机，请及时联系专业人员或本地危机热线。"
        full = full + "\n\n" + extra + "\n\n" + tip

    # 最终略微截断或保留，保持在合理区间
    if len(full) > 900:
        full = full[:900]

    return full

