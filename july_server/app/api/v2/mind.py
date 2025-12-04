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

from app.lib.exception import Success, NotFound, Forbidden, Created, Deleted
from app.lib.red_print import RedPrint
from app.lib.schema import paginator_schema
from app.model.mind import MindKnowledge, MindStar
from app.model.base import db
from app.service.lbs_service import search_nearby
from app.lib.mind_content_generator import generate_content
from app.lib.token import auth
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
        'title': '人际界限：学会说“不”的三步法',
        'tags': ['人际', '自我保护'],
        'source': '人际沟通技巧',
        'content': '学会设置界限可保护心理资源。三步法为：首先陈述事实（描述具体情境），其次表达感受或需求，最后明确提出可接受的请求或替代方案。练习时保持语气平和、言辞具体，有助于既维护关系又保护自我界限。',
        'read_count': 65
    }
]

# 在模块加载时，使用生成器为后备条目扩写正文，保证本地回退时内容详尽一致
try:
    for x in _KNOWLEDGE:
        try:
            x['content'] = generate_content(x.get('title'), x.get('tags', []), x.get('source'))
        except Exception:
            # 保底：如果生成出错，保留现有 content
            pass
except Exception:
    pass


def _paginate(items, page: int, size: int):
    total = len(items)
    start = (page - 1) * size
    end = start + size
    slice_ = items[start:end]
    # 兼容前端 Paging 所需字段（paginator_schema）
    total_page = (total + size - 1) // size if size > 0 else 1
    next_page = page + 1 if end < total else None
    prev_page = page - 1 if page > 1 else None
    return {
        'items': slice_,
        'current_page': page,
        'next_page': next_page,
        'prev_page': prev_page,
        'total_page': total_page,
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
                obj = {
                    'id': getattr(it, 'id', None),
                    'title': getattr(it, 'title', None),
                    'tags': getattr(it, 'tags', None),
                    'source': getattr(it, 'source', None),
                    'content': getattr(it, 'content', None),
                    'read_count': getattr(it, 'read_count', 0),
                    'category': getattr(it, 'category', None)
                }
            if isinstance(obj.get('tags'), str) and obj.get('tags'):
                try:
                    obj['tags'] = json.loads(obj['tags'])
                except Exception:
                    obj['tags'] = [t.strip() for t in obj['tags'].split(',') if t.strip()]
                orig_source = obj.get('source')
                summary = obj.get('summary') or obj.get('category') or (obj.get('title') and str(obj.get('title'))[:12]) or '心理指南'
                obj['summary'] = summary
                obj['source'] = summary
                if obj.get('content'):
                    c = str(obj.get('content'))
                    m = re.search(r"来源[:：]\s*([^；;\n\r]+)", c)
                    origin = m.group(1).strip() if m else None
                    c = re.sub(r"来源[:：].*?(；|;|$).*", "", c)
                    c = re.sub(r"原文链接[:：].*", "", c)
                    obj['content'] = c.strip()
                    obj['origin'] = origin or orig_source
                else:
                    obj['origin'] = orig_source
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
            if isinstance(it.tags, str) and it.tags:
                try:
                    it.tags = json.loads(it.tags)
                except Exception:
                    it.tags = [t.strip() for t in it.tags.split(',') if t.strip()]
            # 当前用户是否已收藏
            starred = False
            try:
                if g.user:
                    starred = MindStar.get_one(user_id=g.user.id, knowledge_id=it.id) is not None
            except Exception:
                pass
            # MindKnowledge model hides 'content' by default (for list responses).
            # For detail API we must explicitly include the content field so the
            # client can render the full post body.
            data = dict(it)
            try:
                data['content'] = it.content
            except Exception:
                # 保底：如果访问失败，仍保留已有响应结构
                data['content'] = ''
            # 构建 summary 并覆盖 source
            summary = data.get('summary') or data.get('category') or (data.get('title') and str(data.get('title'))[:12]) or '心理指南'
            data['summary'] = summary
            data['source'] = summary
            # 清洗 content：去除爬取时残留的来源 / 原文链接说明
            if data.get('content'):
                c = str(data.get('content'))
                c = re.sub(r"来源[:：].*?(；|;|$).*", "", c)
                c = re.sub(r"原文链接[:：].*", "", c)
                data['content'] = c.strip()
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
