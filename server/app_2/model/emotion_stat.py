# -*- coding: utf-8 -*-
"""
    情绪统计模型
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from sqlalchemy import Column, String, Date, Integer, Enum as SQLEnum
from datetime import datetime, timedelta

from .base import BaseModel


class EmotionStatSourceType:
    """统计来源类型"""
    DIARY = 'DIARY'
    TOPIC = 'TOPIC'


class EmotionStat(BaseModel):
    """
    情绪统计模型
    """
    __tablename__ = 'emotion_stat'

    user_id = Column(String(32), nullable=False, comment='用户ID')
    stat_date = Column(Date, nullable=False, comment='统计日期')
    emotion_label_id = Column(String(32), nullable=False, comment='情绪标签ID')
    source_type = Column(SQLEnum('DIARY', 'TOPIC'), nullable=False, comment='来源类型')
    count = Column(Integer, default=1, comment='次数')

    def __str__(self):
        return f"EmotionStat-{self.stat_date}"

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
    def get_user_stats(cls, user_id, start_date=None, end_date=None):
        """获取用户情绪统计"""
        if not start_date:
            start_date = datetime.now().date() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now().date()
        
        return cls.query.filter(
            cls.user_id == user_id,
            cls.stat_date >= start_date,
            cls.stat_date <= end_date
        ).order_by(cls.stat_date.desc()).all()

    @classmethod
    def get_emotion_distribution(cls, user_id, days=30):
        """获取情绪分布统计"""
        from sqlalchemy import func
        from .emotion_label import EmotionLabel
        
        start_date = datetime.now().date() - timedelta(days=days)
        
        # 按情绪标签分组统计
        stats = cls.query.filter(
            cls.user_id == user_id,
            cls.stat_date >= start_date
        ).with_entities(
            cls.emotion_label_id,
            func.sum(cls.count).label('total_count')
        ).group_by(cls.emotion_label_id).all()
        
        result = []
        for stat in stats:
            label = EmotionLabel.get_one(id=stat.emotion_label_id)
            if label:
                result.append({
                    'emotion_label': label,
                    'count': stat.total_count
                })
        
        return sorted(result, key=lambda x: x['count'], reverse=True)

    @classmethod
    def get_emotion_trend(cls, user_id, days=30):
        """获取情绪趋势"""
        from .emotion_label import EmotionLabel
        
        start_date = datetime.now().date() - timedelta(days=days)
        
        stats = cls.query.filter(
            cls.user_id == user_id,
            cls.stat_date >= start_date
        ).order_by(cls.stat_date.asc()).all()
        
        # 按日期组织数据
        trend_data = {}
        for stat in stats:
            date_str = stat.stat_date.strftime('%Y-%m-%d')
            if date_str not in trend_data:
                trend_data[date_str] = []
            
            label = EmotionLabel.get_one(id=stat.emotion_label_id)
            if label:
                trend_data[date_str].append({
                    'emotion_label': label,
                    'count': stat.count,
                    'source_type': stat.source_type
                })
        
        return trend_data

