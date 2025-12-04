# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2023 by Jeffrey.
    :license: Apache 2.0, see LICENSE for more details.
"""
from sqlalchemy import Column, String, Enum, func

from .base import BaseModel, db


class Star(BaseModel):
    """
    收藏/互动模型
    支持三种类型：STAR(收藏)、HUG(拥抱)、PAT(拍拍)
    """
    __tablename__ = 'star'

    user_id = Column(String(32), nullable=False, index=True, comment='用户标识')
    topic_id = Column(String(32), nullable=False, index=True, comment='话题标识')
    interaction_type = Column(Enum('STAR', 'HUG', 'PAT'), default='STAR', comment='互动类型')

    def __str__(self):
        return self.id

    @classmethod
    def get_starred(cls, user_id, topic_id, interaction_type='STAR'):
        """
        获取该用户是否对该话题进行了指定类型的互动
        """
        return cls.get_one(user_id=user_id, topic_id=topic_id, interaction_type=interaction_type) is not None

    @classmethod
    def get_star_count(cls, topic_id, interaction_type=None):
        """
        获取该话题的互动数量
        如果指定interaction_type，则只统计该类型的数量
        """
        query = db.session.query(func.count(cls.id)).filter_by(topic_id=topic_id, delete_time=None)
        if interaction_type:
            query = query.filter_by(interaction_type=interaction_type)
        return query.scalar()
    
    @classmethod
    def get_interaction_stats(cls, topic_id):
        """
        获取话题的所有互动统计
        返回: {'STAR': 10, 'HUG': 5, 'PAT': 3}
        """
        results = db.session.query(
            cls.interaction_type,
            func.count(cls.id).label('count')
        ).filter_by(
            topic_id=topic_id,
            delete_time=None
        ).group_by(cls.interaction_type).all()
        
        stats = {'STAR': 0, 'HUG': 0, 'PAT': 0}
        for interaction_type, count in results:
            stats[interaction_type] = count
        
        return stats
