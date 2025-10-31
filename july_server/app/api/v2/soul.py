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
from app.model.user import User
from app.service.llm_service import LLMService

api = RedPrint('soul')

# 等待分析时显示的随机鼓励句子
WAITING_MESSAGES = [
    "Life is like a box of chocolates, you never know what you're gonna get."
]


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

#cocobegin
@api.route('/custom', methods=['POST'])
@auth.login_required
def save_custom_push():
    """
    保存用户自定义句子
    1. 调用情绪标签识别功能识别句子情绪
    2. 如果识别为"待定"，为所有10个情绪标签创建记录
    3. 否则，为识别出的情绪标签创建记录
    """
    from app.service.llm_service import LLMService
    from datetime import datetime
    import uuid
    
    data = request.get_json()
    
    content = data.get('content', '').strip()
    
    # 验证内容
    if not content:
        raise ParameterError(msg='句子内容不能为空')
    
    if len(content) > 500:
        raise ParameterError(msg='句子内容不能超过500字')
    
    try:
        # 1. 识别情绪标签
        current_app.logger.info(f"开始识别自定义句子的情绪标签, 用户ID: {g.user.id}")
        
        emotion_name = LLMService.analyze_emotion_from_text(content)
        
        current_app.logger.info(
            f"情绪标签识别结果: {emotion_name}, "
            f"用户ID: {g.user.id}, 句子: {content[:50]}..."
        )
        
        # 2. 获取所有系统情绪标签
        system_labels = EmotionLabel.get_system_labels()
        label_dict = {label.name: label for label in system_labels}
        
        # 3. 确定要创建记录的情绪标签
        target_labels = []
        
        if emotion_name == '待定' or emotion_name is None:
            # 如果识别为"待定"或识别失败，为所有10个情绪标签创建记录
            target_labels = list(system_labels)
            current_app.logger.info(
                f"识别结果为'待定'或识别失败, 将为所有 {len(target_labels)} 个情绪标签创建记录"
            )
        elif emotion_name in ['开心', '平静', '兴奋']:
            # 如果识别为"开心"、"平静"、"兴奋"，除了该情绪外，还要为"愤怒"、"难过"、"焦虑"、"疲惫"、"孤独"创建记录
            target_labels = [label_dict[emotion_name]]  # 先添加识别出的情绪
            
            # 添加额外需要创建的情绪标签
            additional_emotions = ['愤怒', '难过', '焦虑', '疲惫', '孤独']
            for add_emotion in additional_emotions:
                if add_emotion in label_dict:
                    target_labels.append(label_dict[add_emotion])
            
            current_app.logger.info(
                f"识别出情绪: {emotion_name}, 将创建记录: {[label.name for label in target_labels]}"
            )
        elif emotion_name in label_dict:
            # 如果识别出其他情绪，只为该情绪标签创建记录
            target_labels = [label_dict[emotion_name]]
            current_app.logger.info(
                f"识别出情绪: {emotion_name}, 为该情绪标签创建记录"
            )
        else:
            # 如果识别出的情绪不在系统中，默认为所有情绪标签创建记录
            current_app.logger.warning(
                f"识别出的情绪 '{emotion_name}' 不在系统中, 将为所有情绪标签创建记录"
            )
            target_labels = list(system_labels)
        
        # 4. 为每个情绪标签创建记录
        created_pushes = []
        from app.model.base import db
        
        for emotion_label in target_labels:
            try:
                push_id = str(uuid.uuid4()).replace('-', '')
                
                # 检查是否已存在相同内容和情绪标签的记录（避免重复）
                existing = db.session.execute(
                    db.text("""
                        SELECT id FROM soul_push 
                        WHERE content = :content 
                        AND emotion_label_id = :emotion_label_id
                        AND user_id = :user_id
                        AND delete_time IS NULL 
                        LIMIT 1
                    """),
                    {
                        'content': content,
                        'emotion_label_id': emotion_label.id,
                        'user_id': g.user.id
                    }
                ).fetchone()
                
                if existing:
                    current_app.logger.debug(
                        f"跳过重复记录: 情绪={emotion_name}, "
                        f"用户ID={g.user.id}"
                    )
                    continue
                
                # 创建新记录（使用原始SQL插入，确保正确）
                db.session.execute(
                    db.text("""
                        INSERT INTO soul_push 
                        (id, user_id, content, source_type, emotion_label_id, llm_model, create_time, delete_time)
                        VALUES 
                        (:id, :user_id, :content, 'RANDOM', :emotion_label_id, 'user_custom', :create_time, NULL)
                    """),
                    {
                        'id': push_id,
                        'user_id': g.user.id,
                        'content': content,
                        'emotion_label_id': emotion_label.id,
                        'create_time': datetime.now()
                    }
                )
                
                created_pushes.append({
                    'id': push_id,
                    'emotion_label_id': emotion_label.id,
                    'emotion_name': emotion_label.name
                })
                
            except Exception as e:
                current_app.logger.error(
                    f"创建句子记录失败: 情绪={emotion_label.name}, "
                    f"错误={str(e)}"
                )
                continue
        
        db.session.commit()
        
        # 5. 返回第一条创建的记录（用于前端显示）
        first_push_id = created_pushes[0]['id'] if created_pushes else None
        first_emotion_label_id = created_pushes[0]['emotion_label_id'] if created_pushes else None
        
        # 获取情绪标签信息
        emotion_label_info = None
        if first_emotion_label_id:
            emotion_label = EmotionLabel.get_one(id=first_emotion_label_id, delete_time=None)
            if emotion_label:
                emotion_label_info = {
                    'id': emotion_label.id,
                    'name': emotion_label.name,
                    'icon': emotion_label.icon,
                    'color': emotion_label.color
                }
        
        current_app.logger.info(
            f"保存自定义句子成功, 用户ID: {g.user.id}, "
            f"识别情绪: {emotion_name}, 创建记录数: {len(created_pushes)}"
        )
        
        return Success(data={
            'push_id': first_push_id,
            'content': content,
            'source_type': 'RANDOM',
            'emotion_label': emotion_label_info,
            'emotion_name': emotion_name,
            'created_count': len(created_pushes)
        }, msg=f'保存成功，已创建{len(created_pushes)}条记录')
        
    except Exception as e:
        current_app.logger.error(
            f"保存自定义句子失败, 用户ID: {g.user.id}, 错误: {str(e)}"
        )
        
        # 降级：识别失败时，为所有情绪标签创建记录（等同于"待定"处理）
        try:
            system_labels = EmotionLabel.get_system_labels()
            from app.model.base import db
            from datetime import datetime
            import uuid
            
            created_pushes = []
            
            for emotion_label in system_labels:
                try:
                    push_id = str(uuid.uuid4()).replace('-', '')
                    
                    db.session.execute(
                        db.text("""
                            INSERT INTO soul_push 
                            (id, user_id, content, source_type, emotion_label_id, llm_model, create_time, delete_time)
                            VALUES 
                            (:id, :user_id, :content, 'RANDOM', :emotion_label_id, 'user_custom_fallback', :create_time, NULL)
                        """),
                        {
                            'id': push_id,
                            'user_id': g.user.id,
                            'content': content,
                            'emotion_label_id': emotion_label.id,
                            'create_time': datetime.now()
                        }
                    )
                    
                    created_pushes.append({
                        'id': push_id,
                        'emotion_label_id': emotion_label.id,
                        'emotion_name': emotion_label.name
                    })
                except Exception as inner_e:
                    current_app.logger.error(f"创建降级记录失败: {str(inner_e)}")
                    continue
            
            db.session.commit()
            
            # 返回第一条记录
            first_push_id = created_pushes[0]['id'] if created_pushes else None
            first_emotion_label_id = created_pushes[0]['emotion_label_id'] if created_pushes else None
            
            emotion_label_info = None
            if first_emotion_label_id:
                emotion_label = EmotionLabel.get_one(id=first_emotion_label_id, delete_time=None)
                if emotion_label:
                    emotion_label_info = {
                        'id': emotion_label.id,
                        'name': emotion_label.name,
                        'icon': emotion_label.icon,
                        'color': emotion_label.color
                    }
            
            return Success(data={
                'push_id': first_push_id,
                'content': content,
                'source_type': 'RANDOM',
                'emotion_label': emotion_label_info,
                'emotion_name': '待定',
                'created_count': len(created_pushes)
            }, msg=f'保存成功（情绪识别失败，已创建{len(created_pushes)}条记录）')
            
        except Exception as fallback_e:
            current_app.logger.error(f"降级处理也失败: {str(fallback_e)}")
            
            # 最后的降级：只保存一条记录
            push = SoulPush.create(
                user_id=g.user.id,
                content=content,
                source_type='CUSTOM',
                llm_model='user_custom_fallback'
            )
            
            return Success(data={
                'push_id': push.id,
                'content': push.content,
                'source_type': push.source_type,
                'emotion_label': None
            }, msg='保存成功（系统错误，已保存但未分类）')


@api.route('/custom/<push_id>', methods=['DELETE'])
@auth.login_required
def delete_custom_push(push_id):
    """
    删除用户自定义句子
    由于一个句子可能对应多条记录（不同情绪标签），需要删除所有相同内容的记录
    """
    push = SoulPush.get_or_404(id=push_id, delete_time=None)
    
    # 权限检查：只能删除自己的自定义句子
    if push.user_id != g.user.id:
        raise Forbidden(msg='无权操作该推送')
    
    # 检查是否是用户自定义的句子（通过llm_model判断）
    if push.llm_model not in ['user_custom', 'user_custom_fallback']:
        raise ParameterError(msg='只能删除自定义句子')
    
    # 获取该句子的所有记录（相同内容、相同用户、user_custom标识）
    from app.model.base import db
    
    deleted_count = db.session.execute(
        db.text("""
            UPDATE soul_push 
            SET delete_time = NOW() 
            WHERE content = :content 
            AND user_id = :user_id
            AND llm_model IN ('user_custom', 'user_custom_fallback')
            AND delete_time IS NULL
        """),
        {
            'content': push.content,
            'user_id': g.user.id
        }
    ).rowcount
    
    db.session.commit()
    
    current_app.logger.info(
        f"删除自定义句子, 用户ID: {g.user.id}, "
        f"推送ID: {push_id}, 删除记录数: {deleted_count}"
    )
    
    return Success(msg=f'删除成功，已删除{deleted_count}条记录')


@api.route('/custom/list', methods=['GET'])
@auth.login_required
def get_custom_list():
    """
    获取用户所有自定义句子
    由于一个句子可能对应多条记录（不同情绪标签），需要去重显示
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)
    
    # 获取用户自定义句子（通过llm_model判断，去重内容）
    from app.model.base import db
    
    # 使用SQL去重，获取每个唯一内容的第一条记录
    all_custom = db.session.execute(
        db.text("""
            SELECT 
                sp1.id,
                sp1.content,
                sp1.emotion_label_id,
                sp1.create_time,
                sp1.llm_model
            FROM soul_push sp1
            INNER JOIN (
                SELECT content, MIN(create_time) as min_time
                FROM soul_push
                WHERE user_id = :user_id
                  AND llm_model IN ('user_custom', 'user_custom_fallback')
                  AND delete_time IS NULL
                GROUP BY content
            ) sp2 ON sp1.content = sp2.content 
                 AND sp1.create_time = sp2.min_time
            WHERE sp1.user_id = :user_id
              AND sp1.llm_model IN ('user_custom', 'user_custom_fallback')
              AND sp1.delete_time IS NULL
            ORDER BY sp1.create_time DESC
        """),
        {'user_id': g.user.id}
    ).fetchall()
    
    # 手动分页
    total_count = len(all_custom)
    total_pages = (total_count + size - 1) // size
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_items = all_custom[start_idx:end_idx]
    
    # 转换为字典格式，包含情绪标签信息
    items = []
    for row in paginated_items:
        emotion_label_info = None
        if row.emotion_label_id:
            emotion_label = EmotionLabel.get_one(id=row.emotion_label_id, delete_time=None)
            if emotion_label:
                emotion_label_info = {
                    'id': emotion_label.id,
                    'name': emotion_label.name,
                    'icon': emotion_label.icon,
                    'color': emotion_label.color
                }
        
        items.append({
            'id': row.id,
            'content': row.content,
            'emotion_label': emotion_label_info,
            'create_time': row.create_time.isoformat() if row.create_time else None,
            'source_type': 'RANDOM',
            'llm_model': row.llm_model
        })
    
    return Success(data={
        'items': items,
        'total_count': total_count,
        'current_page': page,
        'total_page': total_pages
    })


@api.route('/public/random', methods=['GET'])
@auth.login_required
def get_public_random():
    """
    从公共句子库获取随机句子
    可选参数：emotion_label_id - 指定情绪标签
    """
    # 查找系统用户
    system_user = User.get_one(openid='system_soul_bot')
    if not system_user:
        # 如果没有系统用户，返回随机推送
        return get_random_push()
    
    # 获取情绪标签ID（可选）
    emotion_label_id = request.args.get('emotion_label_id', type=str)
    
    # 从系统用户的句子库随机选择
    import random
    query = SoulPush.query.filter_by(
        user_id=system_user.id,
        source_type='RANDOM',
        delete_time=None
    )
    
    # 如果指定了情绪标签，按情绪标签过滤
    if emotion_label_id:
        query = query.filter_by(emotion_label_id=emotion_label_id)
    
    pushes = query.all()
    
    if not pushes:
        # 如果没有匹配的句子，尝试不按情绪标签查找
        if emotion_label_id:
            pushes = SoulPush.query.filter_by(
                user_id=system_user.id,
                source_type='RANDOM',
                delete_time=None
            ).all()
        
        if not pushes:
            # 如果没有公共句子，生成随机推送
            return get_random_push()
    
    # 随机选择一条
    selected = random.choice(pushes)
    
    current_app.logger.info(f"获取公共句子库随机句子, 用户ID: {g.user.id}, 情绪标签: {emotion_label_id or '无'}")
    
    return Success(data={
        'push_id': selected.id,
        'content': selected.content,
        'source_type': 'PUBLIC',
        'emotion_label_id': selected.emotion_label_id
    })


@api.route('/public/emotion/<emotion_label_id>', methods=['GET'])
@auth.login_required
def get_public_by_emotion(emotion_label_id):
    """
    根据情绪标签获取公共句子
    """
    # 查找系统用户
    system_user = User.get_one(openid='system_soul_bot')
    if not system_user:
        raise NotFound(msg='公共句子库不存在')
    
    # 验证情绪标签是否存在
    from app.model.emotion_label import EmotionLabel
    emotion = EmotionLabel.get_one(id=emotion_label_id, delete_time=None)
    if not emotion:
        raise NotFound(msg='情绪标签不存在')
    
    # 获取该情绪标签下的句子
    pushes = SoulPush.query.filter_by(
        user_id=system_user.id,
        source_type='RANDOM',
        emotion_label_id=emotion_label_id,
        delete_time=None
    ).all()
    
    if not pushes:
        # 如果没有匹配的句子，返回空列表
        return Success(data={'items': [], 'count': 0})
    
    # 随机返回一条
    import random
    selected = random.choice(pushes)
    
    current_app.logger.info(f"根据情绪标签获取句子, 情绪: {emotion.name}, 用户ID: {g.user.id}")
    
    return Success(data={
        'push_id': selected.id,
        'content': selected.content,
        'emotion_label': {
            'id': emotion.id,
            'name': emotion.name,
            'icon': emotion.icon,
            'color': emotion.color
        }
    })


@api.route('/smart', methods=['GET'])
@auth.login_required
def get_smart_push():
    """
    智能推送 - 根据识别出的情绪标签随机匹配数据库中的句子
    1. 自动识别用户最近的情绪标签（基于近7天的日记、发帖、评论等）
    2. 根据识别出的情绪标签，从数据库随机匹配一条句子
    3. 不再使用LLM生成句子
    """
    from app.service.emotion_analysis import EmotionAnalysisService
    import random
    
    try:
        # 1. 识别用户最近的情绪标签
        current_app.logger.info(f"开始智能推送分析, 用户ID: {g.user.id}")
        
        emotion_analysis = EmotionAnalysisService.analyze_user_emotion_today(g.user.id)
        emotion_label_id = emotion_analysis.get('emotion_label_id')
        emotion_name = emotion_analysis.get('emotion_name', '平静')
        confidence = emotion_analysis.get('confidence', 0.0)
        
        current_app.logger.info(
            f"识别到用户情绪: {emotion_name} (ID: {emotion_label_id}, "
            f"置信度: {confidence:.2f})"
        )
        
        # 2. 从公共句子库随机匹配情绪标签一致的句子
        system_user = User.get_one(openid='system_soul_bot')
        
        # 2.1 如果识别情绪为"待定"，随机显示一条标签为"开心"或"兴奋"的句子
        if emotion_name == '待定':
            current_app.logger.info(
                f"识别情绪为'待定', 将随机选择'开心'或'兴奋'标签的句子"
            )
            
            if system_user:
                # 获取"开心"和"兴奋"的情绪标签
                happy_label = EmotionLabel.query.filter_by(
                    name='开心', 
                    type='SYSTEM', 
                    delete_time=None
                ).first()
                
                excited_label = EmotionLabel.query.filter_by(
                    name='兴奋', 
                    type='SYSTEM', 
                    delete_time=None
                ).first()
                
                # 查找"开心"或"兴奋"标签的句子
                target_label_ids = []
                if happy_label:
                    target_label_ids.append(happy_label.id)
                if excited_label:
                    target_label_ids.append(excited_label.id)
                
                if target_label_ids:
                    pushes = SoulPush.query.filter(
                        SoulPush.user_id == system_user.id,
                        SoulPush.source_type == 'RANDOM',
                        SoulPush.emotion_label_id.in_(target_label_ids),
                        SoulPush.delete_time.is_(None)
                    ).all()
                    
                    if pushes:
                        selected = random.choice(pushes)
                        
                        # 获取选中句子的情绪标签信息
                        selected_emotion_label = EmotionLabel.get_one(
                            id=selected.emotion_label_id, 
                            delete_time=None
                        ) if selected.emotion_label_id else None
                        
                        current_app.logger.info(
                            f"识别为'待定', 随机选择'开心'或'兴奋'标签句子, "
                            f"用户ID: {g.user.id}, 匹配到 {len(pushes)} 条句子, "
                            f"选择情绪: {selected_emotion_label.name if selected_emotion_label else '未知'}"
                        )
                        
                        return Success(data={
                            'push_id': selected.id,
                            'content': selected.content,
                            'emotion_label': {
                                'id': selected_emotion_label.id if selected_emotion_label else None,
                                'name': selected_emotion_label.name if selected_emotion_label else '待定',
                                'icon': selected_emotion_label.icon if selected_emotion_label else None,
                                'color': selected_emotion_label.color if selected_emotion_label else None
                            },
                            'confidence': confidence,
                            'source': 'database_pending'  # 标识这是"待定"情况的特殊处理
                        })
        
        # 2.2 如果不是"待定"，正常匹配识别的情绪标签
        if system_user and emotion_label_id and emotion_name != '待定':
            pushes = SoulPush.query.filter_by(
                user_id=system_user.id,
                source_type='RANDOM',
                emotion_label_id=emotion_label_id,
                delete_time=None
            ).all()
            
            if pushes:
                # 随机选择一条
                selected = random.choice(pushes)
                
                current_app.logger.info(
                    f"从公共句子库获取推送, 情绪: {emotion_name}, "
                    f"用户ID: {g.user.id}, 匹配到 {len(pushes)} 条句子"
                )
                
                emotion_label = EmotionLabel.get_one(id=emotion_label_id, delete_time=None)
                
                return Success(data={
                    'push_id': selected.id,
                    'content': selected.content,
                    'emotion_label': {
                        'id': emotion_label.id if emotion_label else emotion_label_id,
                        'name': emotion_name,
                        'icon': emotion_label.icon if emotion_label else None,
                        'color': emotion_label.color if emotion_label else None
                    },
                    'confidence': confidence,
                    'source': 'database'
                })
        
        # 3. 如果没有匹配的句子，返回等待时的随机鼓励句子
        current_app.logger.info(
            f"公共句子库无匹配句子, 情绪: {emotion_name}, "
            f"返回等待时的鼓励句子"
        )
        
        waiting_message = random.choice(WAITING_MESSAGES)
        
        # 如果识别到了情绪标签，尝试获取情绪标签信息
        emotion_label = None
        if emotion_label_id:
            emotion_label = EmotionLabel.get_one(id=emotion_label_id, delete_time=None)
        
        return Success(data={
            'push_id': None,  # 等待句子不保存到数据库
            'content': waiting_message,
            'emotion_label': {
                'id': emotion_label.id if emotion_label else emotion_label_id,
                'name': emotion_name,
                'icon': emotion_label.icon if emotion_label else None,
                'color': emotion_label.color if emotion_label else None
            } if emotion_label_id else None,
            'confidence': confidence,
            'source': 'waiting_message'
        })
        
    except Exception as e:
        current_app.logger.error(f"智能推送失败, 用户ID: {g.user.id}, 错误: {str(e)}")
        
        # 降级：返回等待时的随机鼓励句子
        waiting_message = random.choice(WAITING_MESSAGES)
        
        current_app.logger.info("智能推送失败，返回等待时的鼓励句子")
        
        return Success(data={
            'push_id': None,
            'content': waiting_message,
            'emotion_label': None,
            'confidence': 0.0,
            'source': 'waiting_message_fallback'
        })


@api.route('/smart/another', methods=['GET'])
@auth.login_required
def get_another_smart_push():
    """
    根据已识别的情绪标签，获取数据库中的另一条句子（换一条）
    不重新分析情绪标签，使用已有的情绪标签ID
    
    Query参数:
        emotion_label_id: 情绪标签ID（必需）
        exclude_push_id: 要排除的句子ID（可选，避免重复显示）
    """
    import random
    
    emotion_label_id = request.args.get('emotion_label_id', type=str)
    exclude_push_id = request.args.get('exclude_push_id', type=str)
    
    if not emotion_label_id:
        raise ParameterError(msg='emotion_label_id参数不能为空')
    
    try:
        # 1. 验证情绪标签是否存在
        emotion_label = EmotionLabel.get_one(id=emotion_label_id, delete_time=None)
        if not emotion_label:
            raise NotFound(msg='情绪标签不存在')
        
        # 2. 从公共句子库获取该情绪标签下的所有句子
        system_user = User.get_one(openid='system_soul_bot')
        if not system_user:
            # 如果没有系统用户，返回等待句子
            waiting_message = random.choice(WAITING_MESSAGES)
            return Success(data={
                'push_id': None,
                'content': waiting_message,
                'emotion_label': {
                    'id': emotion_label.id,
                    'name': emotion_label.name,
                    'icon': emotion_label.icon,
                    'color': emotion_label.color
                },
                'source': 'waiting_message'
            })
        
        # 3. 查询该情绪标签下的所有句子
        query = SoulPush.query.filter_by(
            user_id=system_user.id,
            source_type='RANDOM',
            emotion_label_id=emotion_label_id,
            delete_time=None
        )
        
        # 4. 如果有要排除的句子ID，排除它
        if exclude_push_id:
            query = query.filter(SoulPush.id != exclude_push_id)
        
        pushes = query.all()
        
        if pushes:
            # 随机选择一条
            selected = random.choice(pushes)
            
            current_app.logger.info(
                f"根据情绪标签获取另一条句子, 情绪: {emotion_label.name}, "
                f"用户ID: {g.user.id}, 匹配到 {len(pushes)} 条句子, 排除: {exclude_push_id or '无'}"
            )
            
            return Success(data={
                'push_id': selected.id,
                'content': selected.content,
                'emotion_label': {
                    'id': emotion_label.id,
                    'name': emotion_label.name,
                    'icon': emotion_label.icon,
                    'color': emotion_label.color
                },
                'source': 'database'
            })
        else:
            # 如果没有其他句子了，返回等待句子
            waiting_message = random.choice(WAITING_MESSAGES)
            
            current_app.logger.info(
                f"该情绪标签下没有其他句子, 情绪: {emotion_label.name}, "
                f"返回等待时的鼓励句子"
            )
            
            return Success(data={
                'push_id': None,
                'content': waiting_message,
                'emotion_label': {
                    'id': emotion_label.id,
                    'name': emotion_label.name,
                    'icon': emotion_label.icon,
                    'color': emotion_label.color
                },
                'source': 'waiting_message'
            })
            
    except Exception as e:
        current_app.logger.error(f"获取另一条句子失败, 用户ID: {g.user.id}, 错误: {str(e)}")
        
        # 降级：返回等待时的随机鼓励句子
        waiting_message = random.choice(WAITING_MESSAGES)
        
        return Success(data={
            'push_id': None,
            'content': waiting_message,
            'emotion_label': None,
            'source': 'waiting_message_fallback'
        })

#cocoend