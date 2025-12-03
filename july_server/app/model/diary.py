# -*- coding: utf-8 -*-
"""
    日记模型
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from sqlalchemy import Column, String, Text, Date, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class Diary(BaseModel):
    """
    日记模型
    """
    __tablename__ = 'diary'

    user_id = Column(String(32), nullable=False, comment='用户ID')
    content = Column(Text, nullable=False, comment='日记内容')
    emotion_label_id = Column(String(32), comment='情绪标签ID')
    diary_date = Column(Date, nullable=False, comment='日记日期')
    is_public = Column(Boolean, default=False, comment='是否公开')
    weather = Column(String(20), comment='天气')
    location = Column(String(100), comment='地点')
    images = Column(JSON, comment='图片列表')

    def __str__(self):
        return f"Diary-{self.diary_date}"

    def _set_fields(self):
        self._exclude.extend(['delete_time'])
        self._fields.extend(['emotion_label', 'user'])

    @property
    def emotion_label(self):
        """获取情绪标签"""
        from .emotion_label import EmotionLabel
        if self.emotion_label_id:
            return EmotionLabel.get_one(id=self.emotion_label_id, delete_time=None)
        return None

    @property
    def user(self):
        """获取用户信息"""
        from .user import User
        return User.get_one(id=self.user_id, delete_time=None)

    @classmethod
    def get_by_date(cls, user_id, diary_date):
        """根据日期获取日记"""
        return cls.query.filter_by(
            user_id=user_id,
            diary_date=diary_date,
            delete_time=None
        ).first()

    @classmethod
    def get_month_diaries(cls, user_id, year, month):
        """获取某月的所有日记"""
        from datetime import date
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        return cls.query.filter(
            cls.user_id == user_id,
            cls.diary_date >= start_date,
            cls.diary_date < end_date,
            cls.delete_time == None
        ).order_by(cls.diary_date.desc()).all()

    @classmethod
    def get_public_diaries(cls, page=1, size=20):
        """获取公开日记"""
        return cls.query.filter_by(
            is_public=True,
            delete_time=None
        ).order_by(cls.create_time.desc()).paginate(page=page, size=size)

