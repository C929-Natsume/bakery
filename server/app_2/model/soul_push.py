# -*- coding: utf-8 -*-
"""
    心灵鸡汤推送模型
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from sqlalchemy import Column, String, Text, Boolean, Enum as SQLEnum

from .base import BaseModel


class SoulPushSourceType:
    """推送来源类型"""
    DIARY = 'DIARY'
    TOPIC = 'TOPIC'
    EMOTION = 'EMOTION'
    RANDOM = 'RANDOM'
    CUSTOM = 'CUSTOM' # 自定义句子


class SoulPush(BaseModel):
    """
    心灵鸡汤推送记录模型
    """
    __tablename__ = 'soul_push'

    user_id = Column(String(32), nullable=False, comment='用户ID')
    content = Column(Text, nullable=False, comment='推送内容')
    source_type = Column(SQLEnum('DIARY', 'TOPIC', 'EMOTION', 'RANDOM', 'CUSTOM'), default='RANDOM', comment='来源类型')
    source_id = Column(String(32), comment='来源ID')
    emotion_label_id = Column(String(32), comment='情绪标签ID')
    is_collected = Column(Boolean, default=False, comment='是否收藏')
    llm_model = Column(String(50), comment='使用的LLM模型')

    def __str__(self):
        return f"SoulPush-{self.id}"

    def _set_fields(self):
        self._exclude.extend(['delete_time'])
        self._fields.extend(['emotion_label'])

    @property
    def emotion_label(self):
        """获取情绪标签"""
        from .emotion_label import EmotionLabel
        if self.emotion_label_id:
            return EmotionLabel.get_one(id=self.emotion_label_id, delete_time=None)
        return None

    @classmethod
    def get_user_history(cls, user_id, page=1, size=20):
        """获取用户推送历史"""
        return cls.query.filter_by(
            user_id=user_id,
            delete_time=None
        ).order_by(cls.create_time.desc()).paginate(page=page, size=size)

    @classmethod
    def get_collected(cls, user_id):
        """获取用户收藏的推送"""
        return cls.query.filter_by(
            user_id=user_id,
            is_collected=True,
            delete_time=None
        ).order_by(cls.create_time.desc()).all()

    def toggle_collect(self):
        """切换收藏状态"""
        self.is_collected = not self.is_collected
        self.save()

