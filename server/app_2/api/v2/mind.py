# -*- coding: utf-8 -*-
"""
    心灵配方（专业心理知识） API（最小可运行雏形）
    - /v2/mind/knowledge  列表，分页返回 paginator_schema 兼容格式
    - /v2/mind/knowledge/<id> 详情
    - /v2/mind/nearby  腾讯位置服务 POI 搜索（降级为静态示例）
"""
from flask import request, current_app, g
import json
import re

from app_2.lib.exception import Success, NotFound, Forbidden, Created, Deleted
from app_2.lib.red_print import RedPrint
from app_2.lib.schema import paginator_schema
from app_2.model.mind import MindKnowledge, MindStar
from app_2.model.base import db
from app_2.service.lbs_service import search_nearby
from app_2.lib.token import auth
from sqlalchemy import and_

api = RedPrint('mind')


# 简单静态知识库（后续改为数据库）
_KNOWLEDGE = [
    {
        'id': 'k1',
        'title': '认识焦虑：症状、成因与自助方法',
        'tags': ['焦虑', '科普'],
        'source': '中国心理学会科普工作委员会',
        'content': '焦虑是一种面对未知或可能的威胁时产生的警觉和担心。常见表现包括心跳加速、出汗、注意力受损与睡眠困难。成因通常由遗传易感性、环境压力与认知偏差共同作用。自助方法包括规律作息、呼吸与放松训练、分步暴露不适情境以及记录并挑战灾难化想法；若影响日常功能，建议及时寻求专业评估与支持。',
        'read_count': 128
    },
    {
        'id': 'k2',
        'title': '抑郁情绪的识别与求助指南',
        'tags': ['抑郁', '求助'],
        'source': 'WHO 心理健康指南',
        'content': '抑郁是一种以持续低落心情、兴趣或快感丧失、能量下降为核心的状态，常伴随睡眠与食欲改变、负性自评与注意力受损。若这些症状持续两周以上并影响学习或工作，应重视并寻求评估。初步自助可包括活动安排（行为激活）、规律作息与社会支持；严重时可考虑专业心理治疗或药物治疗，并联系当地心理卫生资源或危机干预热线。',
        'read_count': 96
    },
    {
        'id': 'k3',
        'title': '睡眠卫生：提高睡眠质量的10个建议',
        'tags': ['睡眠', '行为建议'],
        'source': 'NIMH 睡眠建议',
        'content': '改善睡眠的关键在于睡眠卫生：保持固定的就寝与起床时间，睡前一小时减少屏幕与强刺激活动，限制咖啡因与酒精摄入，创造安静黑暗的睡眠环境。白天适度运动与避免长时间午睡也有帮助。若长期失眠影响日常功能，可尝试睡眠限制疗法与认知行为治疗（CBT-I），必要时寻求专业睡眠医学评估。',
        'read_count': 210
    },
    {
        'id': 'k4',
        'title': '认知重建：识别与修正消极自动化思维',
        'tags': ['认知行为疗法', '技巧'],
        'source': 'CBT 实践手册',
        'content': '认知重建旨在识别自动出现的负面想法（如灾难化、过度概括）并通过证据检验与替代性解释来修正。实践步骤包括记录触发事件、自动思维和证据；提出更平衡的替代想法并在日常中练习。长期练习可减少情绪困扰并提升行为适应性。',
        'read_count': 88
    },
    {
        'id': 'k5',
        'title': '压力管理：ABCDE 技术与呼吸放松',
        'tags': ['压力', '放松'],
        'source': '心理咨询基础',
        'content': 'ABCDE 即识别触发事件（A）、辨认信念（B）、理解后果（C）、对信念进行辩论（D）并观察效果（E）。配合腹式呼吸或渐进性肌肉放松练习，可在紧张时刻快速调节生理激活。建议将这些技术作为常规工具，在压力情境中有意识地练习并记录效果。',
        'read_count': 77
    },
    {
        'id': 'k6',
        'title': '人际界限：学会说"不"的三步法',
        'tags': ['人际', '自我保护'],
        'source': '人际沟通技巧',
        'content': '学会设置界限可保护心理资源。三步法为：首先陈述事实（描述具体情境），其次表达感受或需求，最后明确提出可接受的请求或替代方案。练习时保持语气平和、言辞具体，有助于既维护关系又保护自我界限。',
        'read_count': 65
    },
    {
        'id': 'k7',
        'title': '社交焦虑的识别与应对',
        'tags': ['社交', '焦虑'],
        'source': '心理健康实践',
        'content': '社交焦虑常表现为在社交场合过度担心被评判、说话或表现出尴尬而回避社交场景。识别要点包括：在聚会或公共场合感觉强烈紧张、担心被人注视并出现脸红、心跳加快或言语停顿。应对策略包括渐进暴露（从小范围练习社交开始）、事前准备与角色演练、关注对话而非内心评判、放松与呼吸训练；必要时寻求认知行为疗法（CBT）帮助，练习接纳不完美的社交表现。',
        'read_count': 42
    },
    {
        'id': 'k8',
        'title': '愤怒管理：识别与调节策略',
        'tags': ['情绪', '愤怒'],
        'source': '情绪管理指南',
        'content': '愤怒本身是正常情绪，但不受控的愤怒会损害关系与健康。识别愤怒的早期信号（肌肉紧张、加快呼吸、内心评判）并应用即时调节技巧非常关键。常用方法有：短时离场与冷静呼吸、使用 10 秒法缓冲冲动、用"我"语句表达感受而非指责、记录愤怒触发模式并在安全时检视替代性解释。长期可练习正念与情绪识别训练，必要时寻求咨询师支持。',
        'read_count': 36
    },
    {
        'id': 'k9',
        'title': '完美主义与自我宽容',
        'tags': ['完美主义', '自我成长'],
        'source': '心理自助资料',
        'content': '完美主义往往以過高標準、自我苛責與回避失敗為特徵，長期會造成焦慮、拖延與自尊受損。練習自我寬容有助緩解壓力：先識別不合理標準並逐步調整目標；用事實檢驗"必須完美"的信念；允許犯錯作為學習過程；在日常以肯定語句替代自我指責；記錄成功與小進步以增強自信。必要時尋求心理治療幫助打破長期的完美循環。',
        'read_count': 28
    },
    {
        'id': 'k10',
        'title': '亲密关系中的有效沟通',
        'tags': ['人际', '沟通'],
        'source': '关系技巧手册',
        'content': '亲密关系里的冲突常因沟通方式导致。有效沟通包含：用具体事实而非笼统批评开始对话（描述行为而非人格）、表达感受与需要而不是责备、给出可执行的请求或替代方案、在对方回应时主动聆听并复述要点以示理解（反馈式聆听）。遇到情绪高涨时暂停讨论，选择双方都平静时继续，必要时借助关系咨询促进长期模式的改变。',
        'read_count': 31
    },
    {
        'id': 'k11',
        'title': '青少年心理支持指南',
        'tags': ['青少年', '家庭'],
        'source': '学校心理服务',
        'content': '青少年阶段情绪波动與自我認同變化常見。作為家長或教育者，支持要點包括：傾聽並尊重感受、避免簡單化或否定情緒、協助建立規律的生活作息與身體活動、關注社交關係與網絡使用的影響、在出現功能受損（學習退步、長期孤立、自傷念頭）時及時尋求專業評估。提供穩定的支持網絡和適度的自主空間，有助促進心理成熟。',
        'read_count': 24
    },
    {
        'id': 'k12',
        'title': '情绪日志：记录与反思的实操方法',
        'tags': ['情绪', '练习'],
        'source': '自助工作手册',
        'content': '情绪日志是一个低门槛且有效的自我观察工具。每天记录触发事件、当时的情绪与强度、关联的想法与行为，以及可替代的解释或更平衡的想法。周期性回顾可以帮助识别情绪模式与触发器，衡量自我调节策略的效果。建议每天 5–10 分钟，坚持 2–4 周可见明显觉察能力提升。',
        'read_count': 19
    },
    {
        'id': 'k13',
        'title': '正念入门：如何开始每天五分钟练习',
        'tags': ['正念', '练习'],
        'source': '正念课程',
        'content': '正念练习旨在培养当下觉察，减少自动化反应。入门可从每天五分钟开始：选择安静地点，舒适坐姿，关注呼吸；当注意力游走，温和把注意力带回呼吸而不评判；用引导录音辅助（或按 5 分钟计时）。长期实践可以降低焦虑反应、提升情绪调节与注意力。逐步把正念融入日常行为（进食、走路）以巩固效果。',
        'read_count': 22
    },
    {
        'id': 'k14',
        'title': '求助与危机干预：如何联系专业服务',
        'tags': ['危机', '求助'],
        'source': '心理援助中心',
        'content': '当出现难以承受的情绪、严重自伤念头或持续功能下降，应立即寻求帮助。可以联系当地心理咨询机构、危机干预热线或医院精神科。在中国大陆，许多城市和高校提供 24 小时危机热线；若有自伤或伤害他人的即时风险，请先联系当地急救电话或前往医院急诊。准备好简要病史与当前困扰，有助专业人员快速评估并提供支持。',
        'read_count': 27
    }
]


def _paginate(items, page, size):
    """对静态列表进行分页处理"""
    total = len(items)
    start = (page - 1) * size
    end = start + size
    paginated_items = items[start:end]
    next_page = page + 1 if page * size < total else None
    prev_page = page - 1 if page > 1 else None
    return {
        'items': paginated_items,
        'current_page': page,
        'next_page': next_page,
        'prev_page': prev_page,
        'total_page': (total + size - 1) // size,
        'total_count': total
    }


@api.route('/knowledge', methods=['GET'])
def knowledge_list():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 16))
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category')
    tag = request.args.get('tag')

    try:
        q = MindKnowledge.query
        if keyword:
            q = q.filter(MindKnowledge.title.like(f"%{keyword}%"))
        if category:
            q = q.filter_by(category=category)
        if tag:
            q = q.filter(MindKnowledge.tags.like(f"%{tag}%"))
        q = q.filter_by(delete_time=None).order_by(MindKnowledge.create_time.desc())
        # 简易分页
        total = q.count()
        items = q.offset((page-1)*size).limit(size).all()
        # 将 ORM 对象转换为字典并处理 tags 字段，同时填充 summary 并覆盖 source，避免前端显示原始来源域名
        data = []
        for it in items:
            try:
                obj = dict(it)
            except Exception:
                # 如果 ORM 对象不可直接转为 dict，尝试手工构造
                obj = {
                    'id': getattr(it, 'id', None),
                    'title': getattr(it, 'title', None),
                    'tags': getattr(it, 'tags', None),
                    'source': getattr(it, 'source', None),
                    'content': getattr(it, 'content', None),
                    'read_count': getattr(it, 'read_count', 0),
                    'category': getattr(it, 'category', None)
                }
            # 处理 tags 字段：从 JSON 字符串转换为列表
            if isinstance(obj.get('tags'), str) and obj.get('tags'):
                try:
                    obj['tags'] = json.loads(obj['tags'])
                except Exception:
                    obj['tags'] = [t.strip() for t in obj['tags'].split(',') if t.strip()]
            # 记录原始来源（如果有），然后构建 summary（优先后端已有 summary 字段，再使用 category，最后使用标题前段作为回退）
            orig_source = obj.get('source')
            summary = obj.get('summary') or obj.get('category') or (obj.get('title') and str(obj.get('title'))[:12]) or '心理指南'
            obj['summary'] = summary
            # 覆盖 source 字段为短句，避免展示原始网站域名
            obj['source'] = summary
            # 从 content 中提取原始来源（例如“来源：wenda.xinlixue.cn”），保存在单独字段 origin，但不在 content 中展示
            origin = None
            if obj.get('content'):
                content = str(obj.get('content'))
                m = re.search(r"来源[:：]\s*([^；;\n\r]+)", content)
                if m:
                    origin = m.group(1).strip()
                # 清理 content 中的来源说明和原文链接
                content = re.sub(r"来源[:：].*?(；|;|$).*", "", content)
                content = re.sub(r"原文链接[:：].*", "", content)
                obj['content'] = content.strip()
            # 优先使用从 content 中提取的 origin，否则回退到原始 obj.source
            obj['origin'] = origin or orig_source
            data.append(obj)
        next_page = page + 1 if page*size < total else None
        prev_page = page - 1 if page > 1 else None
        return Success(data={
            'items': data,
            'current_page': page,
            'next_page': next_page,
            'prev_page': prev_page,
            'total_page': (total + size - 1)//size,
            'total_count': total
        })
    except Exception as e:
        current_app.logger.warning(f"mind list fallback: {e}")
        # DB异常或表不存在时回退静态数据
        return Success(data=_paginate(_KNOWLEDGE, page, size))


@api.route('/knowledge/<kid>', methods=['GET'])
def knowledge_detail(kid):
    try:
        it = MindKnowledge.get_one(id=kid)
        if it:
            it.update(read_count=(it.read_count or 0) + 1)
            # 当前用户是否已收藏
            starred = False
            try:
                if g.user:
                    starred = MindStar.get_one(user_id=g.user.id, knowledge_id=it.id, delete_time=None) is not None
            except Exception:
                pass
            # 创建字典副本，避免直接修改 ORM 对象
            data = dict(it)
            # 处理 tags 字段：从 JSON 字符串转换为列表
            if isinstance(it.tags, str) and it.tags:
                try:
                    data['tags'] = json.loads(it.tags)
                except Exception:
                    data['tags'] = [t.strip() for t in it.tags.split(',') if t.strip()]
            else:
                data['tags'] = it.tags if it.tags else []
            # 由于 MindKnowledge 模型的 _set_fields 排除了 content 字段，必须显式添加
            data['content'] = it.content  # 显式添加 content 字段
            # 记录原始来源并构建 summary；在返回中把原始来源保存到 `origin`，但不在 content 中显示该行
            orig_source = data.get('source')
            summary = data.get('summary') or data.get('category') or (data.get('title') and str(data.get('title'))[:12]) or '心理指南'
            data['summary'] = summary
            data['source'] = summary
            if data.get('content'):
                c = str(data.get('content'))
                m = re.search(r"来源[:：]\s*([^；;\n\r]+)", c)
                origin = m.group(1).strip() if m else None
                c = re.sub(r"来源[:：].*?(；|;|$).*", "", c)
                c = re.sub(r"原文链接[:：].*", "", c)
                data['content'] = c.strip()
                data['origin'] = origin or orig_source
            else:
                data['origin'] = orig_source
            data['starred'] = starred
            return Success(data=data)
    except Exception as e:
        current_app.logger.warning(f"mind detail fallback: {e}")

    for x in _KNOWLEDGE:
        if x['id'] == kid:
            x['read_count'] = x.get('read_count', 0) + 1
            x['starred'] = False
            return Success(data=x)
    raise NotFound(msg='内容不存在')


@api.route('/nearby', methods=['GET'])
def nearby():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    radius = int(request.args.get('radius', 3000))
    keyword = request.args.get('keyword', '心理咨询,心理咨询中心')

    try:
        source, data = search_nearby(float(lat) if lat else None, float(lng) if lng else None, radius, keyword)
        return Success(data={'source': source, **data})
    except Exception as e:
        current_app.logger.error(f"LBS查询异常: {e}")
        return Success(data={'source': 'mock', 'items': []})


@api.route('/star', methods=['POST'])
def star_toggle():
    if not g.user:
        raise Forbidden(msg='请先登录')
    data = request.get_json(silent=True) or {}
    kid = data.get('knowledge_id')
    if not kid:
        raise NotFound(msg='参数错误')
    try:
        exist = MindStar.get_one(user_id=g.user.id, knowledge_id=kid)
        if exist:
            exist.delete()
            return Success(code=0, msg='取消收藏')
        MindStar.create(user_id=g.user.id, knowledge_id=kid)
        return Success(code=0, msg='收藏成功')
    except Exception as e:
        current_app.logger.error(f"star toggle error: {e}")
        return Success(code=0, msg='已处理')


@api.route('/knowledge', methods=['POST'])
@auth.login_required
def create_knowledge():
    if not g.user or not getattr(g.user, 'is_admin', False):
        raise Forbidden(msg='仅限管理员')
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    tags = data.get('tags')  # list 或 逗号分隔字符串
    category = (data.get('category') or '').strip() or None
    source = (data.get('source') or '').strip() or None
    if not title or not content:
        raise NotFound(msg='标题/内容必填')
    if isinstance(tags, list):
        tags_str = json.dumps(tags, ensure_ascii=False)
    elif isinstance(tags, str) and tags:
        # 兼容逗号分隔
        arr = [t.strip() for t in tags.split(',') if t.strip()]
        tags_str = json.dumps(arr, ensure_ascii=False)
    else:
        tags_str = json.dumps([], ensure_ascii=False)
    obj = MindKnowledge.create(title=title, content=content, tags=tags_str, category=category, source=source)
    return Created(data={'id': obj.id})


@api.route('/knowledge/<kid>', methods=['PUT'])
@auth.login_required
def update_knowledge(kid):
    if not g.user or not getattr(g.user, 'is_admin', False):
        raise Forbidden(msg='仅限管理员')
    obj = MindKnowledge.get_one(id=kid)
    if not obj:
        raise NotFound(msg='内容不存在')
    data = request.get_json(silent=True) or {}
    update = {}
    for field in ('title', 'content', 'category', 'source'):
        if field in data and isinstance(data[field], str):
            update[field] = data[field].strip()
    if 'tags' in data:
        tags = data['tags']
        if isinstance(tags, list):
            update['tags'] = json.dumps(tags, ensure_ascii=False)
        elif isinstance(tags, str):
            arr = [t.strip() for t in tags.split(',') if t.strip()]
            update['tags'] = json.dumps(arr, ensure_ascii=False)
    obj.update(**update)
    return Success(data={'id': obj.id})


@api.route('/knowledge/<kid>', methods=['DELETE'])
@auth.login_required
def delete_knowledge(kid):
    if not g.user or not getattr(g.user, 'is_admin', False):
        raise Forbidden(msg='仅限管理员')
    obj = MindKnowledge.get_one(id=kid)
    if not obj:
        raise NotFound(msg='内容不存在')
    obj.delete()
    return Deleted()


@api.route('/meta', methods=['GET'])
def meta():
    """返回可用分类与热门标签（便于前端筛选）"""
    try:
        # 分类
        cats = [
            x[0] for x in db.session.query(MindKnowledge.category)
            .filter_by(delete_time=None)
            .filter(MindKnowledge.category.isnot(None))
            .distinct().all()
            if x[0]
        ]
        # 标签统计（简单聚合）
        rows = db.session.query(MindKnowledge.tags).filter_by(delete_time=None).all()
        counter = {}
        for (t,) in rows:
            if not t:
                continue
            arr = []
            try:
                arr = json.loads(t) if isinstance(t, str) else []
            except Exception:
                arr = [x.strip() for x in t.split(',') if x.strip()]
            for tag in arr:
                counter[tag] = counter.get(tag, 0) + 1
        hot_tags = sorted(counter.keys(), key=lambda k: counter[k], reverse=True)[:30]
        return Success(data={'categories': cats, 'tags': hot_tags})
    except Exception as e:
        current_app.logger.error(f"mind meta error: {e}")
        # 回退为静态数据中的简单汇总
        cats = list({x.get('category') for x in _KNOWLEDGE if x.get('category')})
        tags = []
        for x in _KNOWLEDGE:
            tags.extend(x.get('tags', []))
        tags = list(dict.fromkeys(tags))[:30]
        return Success(data={'categories': cats, 'tags': tags})


@api.route('/star/mine', methods=['GET'])
@auth.login_required
def my_stars():
    """当前用户的收藏列表（分页返回 Knowledge 列表）"""
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 16))
    uid = g.user.id
    # 连接查询
    q = db.session.query(MindKnowledge).join(
        MindStar, and_(MindStar.knowledge_id == MindKnowledge.id, MindStar.delete_time.is_(None))
    ).filter(
        MindStar.user_id == uid,
        MindKnowledge.delete_time.is_(None)
    ).order_by(MindStar.create_time.desc())

    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    # tags 转换
    data = []
    for it in items:
        obj = it
        if isinstance(it.tags, str) and it.tags:
            try:
                obj.tags = json.loads(it.tags)
            except Exception:
                obj.tags = [t.strip() for t in it.tags.split(',') if t.strip()]
        data.append(obj)
    next_page = page + 1 if page * size < total else None
    prev_page = page - 1 if page > 1 else None
    return Success(data={
        'items': data,
        'current_page': page,
        'next_page': next_page,
        'prev_page': prev_page,
        'total_page': (total + size - 1) // size,
        'total_count': total
    })
