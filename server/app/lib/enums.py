# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from enum import Enum as _Enum


class Enum(_Enum):
    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]


class GenderType(Enum):
    """
    性别
    """
    MAN = '男'
    WOMAN = '女'
    UN_KNOW = '未知'


class MessageCategory(Enum):
    """
    消息分类
    """
    COMMENT = '评论'
    FOLLOWING = '关注'
    STAR = '收藏'


class VideoStatus(Enum):
    """
    视频状态
    """
    REVIEWING = '审核中'
    NORMAL = '正常'
    VIOLATION = '违规'
