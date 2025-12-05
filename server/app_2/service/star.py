# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import g
from sqlalchemy.orm import aliased

from app_2 import db
from app_2.lib.enums import MessageCategory
from app_2.lib.exception import NotFound, Success
from app_2.model.message import Message
from app_2.model.star import Star
from app_2.model.topic import Topic
from app_2.model.user import User
from app_2.model.video import Video
from app_2.validator.forms import PaginateValidator


def get_star_list(topic_id=None, user_id=None, interaction_type=None):
    """
    获取收藏/互动列表
    """
    validator = PaginateValidator().dt_data
    page = validator.get('page')
    size = validator.get('size')

    topic_user = aliased(User)

    query = db.session.query(Star, Topic, User, topic_user) \
        .outerjoin(Topic, Star.topic_id == Topic.id) \
        .outerjoin(User, Star.user_id == User.id) \
        .outerjoin(topic_user, Topic.user_id == topic_user.id) \
        .filter(Star.delete_time.is_(None))

    if topic_id is not None:
        query = query.filter(Star.topic_id == topic_id)

    if user_id is not None:
        query = query.filter(Star.user_id == user_id)
    
    if interaction_type is not None:
        query = query.filter(Star.interaction_type == interaction_type)

    data = query.order_by(Star.create_time.desc()).paginate(page=page, size=size)

    items = data.items
    for index, (star, star.topic, star.user, star.topic.user) in enumerate(items):
        if star.topic.is_anon:
            star.topic.user = None
        if star.topic.video_id is not None:
            star.topic.video = Video.get_one(id=star.topic.video_id)
        else:
            star.topic.video = None

        star.append('topic', 'user')
        star.topic.append('user', 'video')
        items[index] = star

    return data


def star_or_cancel_verify(topic_id, interaction_type='STAR'):
    """
    互动或取消互动验证
    支持三种类型：STAR(收藏)、HUG(拥抱)、PAT(拍拍)
    """
    topic = Topic.get_one(id=topic_id)
    if topic is None:
        raise NotFound(msg='话题不存在')

    # 获取互动类型的中文名称
    interaction_names = {
        'STAR': '收藏',
        'HUG': '拥抱',
        'PAT': '拍拍'
    }
    action_name = interaction_names.get(interaction_type, '互动')

    exist_star = Star.get_one(user_id=g.user.id, topic_id=topic.id, interaction_type=interaction_type)
    exist_msg = Message.get_one(category=MessageCategory.STAR, user_id=topic.user_id, action_user_id=g.user.id,
                                topic_id=topic.id, is_read=False)

    # 创建互动
    if exist_star is None:
        with db.auto_commit():
            Star.create(commit=False, user_id=g.user.id, topic_id=topic.id, interaction_type=interaction_type)
            if exist_msg is None and topic.user_id != g.user.id:
                Message.create(
                    commit=False,
                    content=action_name + '了你的话题',
                    category=MessageCategory.STAR,
                    user_id=topic.user_id,
                    action_user_id=g.user.id,
                    topic_id=topic.id
                )

        # 更新话题收藏数（只统计STAR类型）
        topic.update(star_count=Star.get_star_count(topic_id=topic.id, interaction_type='STAR'))
        return Success(msg=action_name + '成功')

    # 取消互动
    with db.auto_commit():
        exist_star.delete(commit=False)
        if exist_msg is not None:
            exist_msg.delete(commit=False)

    # 更新话题收藏数（只统计STAR类型）
    topic.update(star_count=Star.get_star_count(topic_id=topic.id, interaction_type='STAR'))
    return Success(msg='取消' + action_name + '成功')
