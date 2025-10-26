# -*- coding: utf-8 -*-
"""
Mind domain models: Knowledge and Star
"""
from sqlalchemy import Column, String, Integer, Text, Index, UniqueConstraint
from app.model.base import BaseModel


class MindKnowledge(BaseModel):
    __tablename__ = 'mind_knowledge'

    title = Column(String(128), nullable=False, index=True, comment='标题')
    tags = Column(Text, nullable=True, comment='标签(JSON字符串)')
    source = Column(String(64), nullable=True, comment='来源')
    category = Column(String(32), nullable=True, index=True, comment='分类')
    content = Column(Text, nullable=False, comment='内容')
    read_count = Column(Integer, default=0, comment='阅读数')

    __table_args__ = (
        Index('idx_mind_title', 'title'),
    )

    def _set_fields(self):
        self._exclude.extend(['content'])


class MindStar(BaseModel):
    __tablename__ = 'mind_star'

    user_id = Column(String(32), nullable=False, index=True, comment='用户ID')
    knowledge_id = Column(String(32), nullable=False, index=True, comment='知识ID')

    __table_args__ = (
        UniqueConstraint('user_id', 'knowledge_id', name='uq_mind_star_user_knowledge'),
    )
