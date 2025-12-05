# -*- coding: utf-8 -*-
"""
    心灵鸡汤API - 智能推送
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import current_app, g, request

from app.lib.exception import Success, ParameterError, NotFound, Forbidden
from app.lib.red_print import RedPrint
from app.lib.token import auth
from app.model.soul_push import SoulPush, SoulPushSourceType
from app.model.diary import Diary
from app.model.topic import Topic
from app.model.emotion_label import EmotionLabel
from app.service.llm_service import LLMService

api = RedPrint('soul')


@api.route('/push', methods=['POST'])
@auth.login_required
def generate_push():
    """
    生成智能推送
    根据来源类型（日记/话题/情绪）生成温暖句子
    """
    data = request.get_json()
    
    source_type = data.get('source_type', 'RANDOM')
    source_id = data.get('source_id')
    emotion_label_id = data.get('emotion_label_id')
    
    # 验证来源类型
    valid_types = ['DIARY', 'TOPIC', 'EMOTION', 'RANDOM']
    if source_type not in valid_types:
        raise ParameterError(msg=f'来源类型必须是{valid_types}之一')
    
    # 获取内容和情绪
    content = ''
    emotion_name = '平静'
    
    if source_type == 'DIARY' and source_id:
        # 从日记获取
        diary = Diary.get_one(id=source_id, delete_time=None)
        if diary and diary.user_id == g.user.id:
            content = diary.content
            if diary.emotion_label:
                emotion_name = diary.emotion_label.name
                emotion_label_id = diary.emotion_label_id
    
    elif source_type == 'TOPIC' and source_id:
        # 从话题获取
        topic = Topic.get_one(id=source_id, delete_time=None)
        if topic:
            content = topic.content
            if hasattr(topic, 'emotion_label') and topic.emotion_label:
                emotion_name = topic.emotion_label.name
                emotion_label_id = topic.emotion_label_id
    
    elif source_type == 'EMOTION' and emotion_label_id:
        # 只基于情绪
        label = EmotionLabel.get_one(id=emotion_label_id, delete_time=None)
        if label:
            emotion_name = label.name
    
    # 生成心灵鸡汤
    result = LLMService.generate_soul_message(emotion_name, content)
    
    # 保存推送记录
    push = SoulPush.create(
        user_id=g.user.id,
        content=result['content'],
        source_type=source_type,
        source_id=source_id,
        emotion_label_id=emotion_label_id,
        llm_model=result.get('model', 'fallback')
    )
    
    current_app.logger.info(
        f"生成心灵鸡汤推送, 用户ID: {g.user.id}, "
        f"来源: {source_type}, 模型: {result.get('model')}"
    )
    
    return Success(data={
        'push_id': push.id,
        'content': push.content,
        'emotion_label': push.emotion_label,
        'model': push.llm_model
    })


@api.route('/push/<push_id>/collect', methods=['POST'])
@auth.login_required
def collect_push(push_id):
    """
    收藏/取消收藏推送
    """
    push = SoulPush.get_or_404(id=push_id, delete_time=None)
    
    # 权限检查
    if push.user_id != g.user.id:
        raise Forbidden(msg='无权操作该推送')
    
    push.toggle_collect()
    
    action = '收藏' if push.is_collected else '取消收藏'
    current_app.logger.info(f"用户{action}推送, 用户ID: {g.user.id}, 推送ID: {push_id}")
    
    return Success(data={'is_collected': push.is_collected}, msg=f'{action}成功')


@api.route('/history', methods=['GET'])
@auth.login_required
def get_history():
    """
    获取推送历史
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    collected_only = request.args.get('collected_only', False, type=bool)
    
    if collected_only:
        # 只获取收藏的
        pushes = SoulPush.get_collected(g.user.id)
        return Success(data={'items': pushes, 'total_count': len(pushes)})
    else:
        # 获取所有历史
        pagination = SoulPush.get_user_history(g.user.id, page, size)
        return Success(data={
            'items': pagination.items,
            'total_count': pagination.total,
            'current_page': pagination.page,
            'total_page': pagination.pages
        })


@api.route('/random', methods=['GET'])
@auth.login_required
def get_random_push():
    """
    获取随机推送
    不基于特定内容，随机生成温暖句子
    """
    # 随机选择一个情绪
    import random
    emotion_names = ['开心', '平静', '难过', '焦虑', '期待']
    emotion_name = random.choice(emotion_names)
    
    # 生成句子
    result = LLMService.generate_soul_message(emotion_name, '')
    
    # 保存推送记录
    push = SoulPush.create(
        user_id=g.user.id,
        content=result['content'],
        source_type='RANDOM',
        llm_model=result.get('model', 'fallback')
    )
    
    current_app.logger.info(f"生成随机推送, 用户ID: {g.user.id}")
    
    return Success(data={
        'push_id': push.id,
        'content': push.content
    })


@api.route('/daily', methods=['GET'])
@auth.login_required
def get_daily_push():
    """
    获取每日推送
    基于用户最近的情绪状态生成
    """
    from datetime import datetime, timedelta
    from app.model.emotion_stat import EmotionStat
    
    # 获取最近7天的情绪统计
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    stats = EmotionStat.get_user_stats(g.user.id, start_date, end_date)
    
    # 找出最常见的情绪
    emotion_counts = {}
    for stat in stats:
        if stat.emotion_label:
            name = stat.emotion_label.name
            emotion_counts[name] = emotion_counts.get(name, 0) + stat.count
    
    # 选择最常见的情绪
    if emotion_counts:
        emotion_name = max(emotion_counts, key=emotion_counts.get)
    else:
        emotion_name = '平静'
    
    # 生成句子
    result = LLMService.generate_soul_message(
        emotion_name,
        f'最近经常感到{emotion_name}'
    )
    
    # 保存推送记录
    push = SoulPush.create(
        user_id=g.user.id,
        content=result['content'],
        source_type='EMOTION',
        llm_model=result.get('model', 'fallback')
    )
    
    current_app.logger.info(f"生成每日推送, 用户ID: {g.user.id}, 情绪: {emotion_name}")
    
    return Success(data={
        'push_id': push.id,
        'content': push.content,
        'emotion': emotion_name
    })


@api.route('/batch', methods=['POST'])
@auth.login_required
def generate_batch_push():
    """
    批量生成推送
    为用户的多个日记或话题生成推送
    """
    data = request.get_json()
    
    source_type = data.get('source_type', 'DIARY')
    source_ids = data.get('source_ids', [])
    
    if not source_ids or len(source_ids) > 10:
        raise ParameterError(msg='source_ids不能为空且不超过10个')
    
    results = []
    
    for source_id in source_ids:
        try:
            # 获取内容
            if source_type == 'DIARY':
                source = Diary.get_one(id=source_id, user_id=g.user.id, delete_time=None)
            else:
                source = Topic.get_one(id=source_id, delete_time=None)
            
            if not source:
                continue
            
            # 生成推送
            emotion_name = '平静'
            emotion_label_id = None
            
            if hasattr(source, 'emotion_label') and source.emotion_label:
                emotion_name = source.emotion_label.name
                emotion_label_id = source.emotion_label_id
            
            result = LLMService.generate_soul_message(emotion_name, source.content)
            
            # 保存推送
            push = SoulPush.create(
                user_id=g.user.id,
                content=result['content'],
                source_type=source_type,
                source_id=source_id,
                emotion_label_id=emotion_label_id,
                llm_model=result.get('model', 'fallback')
            )
            
            results.append({
                'source_id': source_id,
                'push_id': push.id,
                'content': push.content
            })
        
        except Exception as e:
            current_app.logger.error(f"批量生成推送失败: {source_id}, 错误: {str(e)}")
            continue
    
    current_app.logger.info(f"批量生成推送, 用户ID: {g.user.id}, 数量: {len(results)}")
    
    return Success(data={'pushes': results, 'count': len(results)})

