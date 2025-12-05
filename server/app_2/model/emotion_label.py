# -*- coding: utf-8 -*-
"""
    情绪标签模型
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from sqlalchemy import Column, String, Integer, Enum as SQLEnum

from .base import BaseModel


class EmotionLabelType:
    """情绪标签类型枚举"""
    SYSTEM = 'SYSTEM'
    CUSTOM = 'CUSTOM'


class EmotionLabel(BaseModel):
    """
    情绪标签模型
    """
    __tablename__ = 'emotion_label'

    name = Column(String(20), nullable=False, comment='标签名称')
    icon = Column(String(256), comment='标签图标URL')
    color = Column(String(7), default='#337559', comment='标签颜色')
    type = Column(SQLEnum('SYSTEM', 'CUSTOM'), default='SYSTEM', comment='标签类型')
    user_id = Column(String(32), comment='创建用户ID（自定义标签）')
    use_count = Column(Integer, default=0, comment='使用次数')

    def __str__(self):
        return self.name

    def _set_fields(self):
        self._exclude.extend(['delete_time', 'update_time'])

    @classmethod
    def get_system_labels(cls):
        """获取系统标签"""
        return cls.query.filter_by(type='SYSTEM', delete_time=None).order_by(cls.use_count.desc()).all()

    @classmethod
    def get_user_labels(cls, user_id):
        """获取用户自定义标签"""
        return cls.query.filter_by(type='CUSTOM', user_id=user_id, delete_time=None).order_by(cls.create_time.desc()).all()

    @classmethod
    def get_popular_labels(cls, limit=10):
        """获取热门标签"""
        return cls.query.filter_by(delete_time=None).order_by(cls.use_count.desc()).limit(limit).all()

    def increment_use_count(self):
        """增加使用次数"""
        self.use_count += 1
        self.save()

