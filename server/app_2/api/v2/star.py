# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import request, g, current_app
from app_2 import auth
from app_2.lib.exception import Success, ParameterError
from app_2.lib.red_print import RedPrint
from app_2.lib.schema import paginator_schema
from app_2.service.star import star_or_cancel_verify, get_star_list
from app_2.validator.forms import StarOrCancelValidator, GetStarListValidator
from app_2.model.star import Star

api = RedPrint('star')


@api.route('/', methods=['GET'])
def get_stars():
    """
    获取收藏/互动列表
    支持按类型筛选
    """
    form = GetStarListValidator()
    topic_id = form.get_data('topic_id')
    user_id = form.get_data('user_id')
    interaction_type = request.args.get('interaction_type')  # 新增：互动类型筛选

    # 验证interaction_type
    if interaction_type and interaction_type not in ['STAR', 'HUG', 'PAT']:
        raise ParameterError(msg='互动类型必须是STAR、HUG或PAT之一')

    stars = get_star_list(topic_id=topic_id, user_id=user_id, interaction_type=interaction_type)
    return Success(data=paginator_schema(stars))


@api.route('/', methods=['POST'])
@auth.login_required
def star_or_cancel():
    """
    互动或取消互动
    支持三种类型：STAR(收藏)、HUG(拥抱)、PAT(拍拍)
    """
    form = StarOrCancelValidator()
    topic_id = form.get_data('topic_id')
    
    # 获取互动类型，默认为STAR
    data = request.json or {}
    interaction_type = data.get('interaction_type', 'STAR')
    
    # 验证interaction_type
    if interaction_type not in ['STAR', 'HUG', 'PAT']:
        raise ParameterError(msg='互动类型必须是STAR、HUG或PAT之一')
    
    return star_or_cancel_verify(topic_id=topic_id, interaction_type=interaction_type)


@api.route('/stat/<topic_id>', methods=['GET'])
def get_topic_interaction_stat(topic_id):
    """
    获取帖子的互动统计
    返回各类型互动的数量和当前用户的互动状态
    """
    # 获取互动统计
    stats = Star.get_interaction_stats(topic_id)
    
    # 获取当前用户的互动状态
    user_interactions = []
    if hasattr(g, 'user') and g.user:
        user_stars = Star.query.filter_by(
            user_id=g.user.id,
            topic_id=topic_id,
            delete_time=None
        ).all()
        user_interactions = [s.interaction_type for s in user_stars]
    
    current_app.logger.info(f"获取帖子互动统计, 帖子ID: {topic_id}")
    
    return Success(data={
        'topic_id': topic_id,
        'stats': stats,
        'user_interactions': user_interactions
    })
