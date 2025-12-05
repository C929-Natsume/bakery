# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import Blueprint as BluePrint

from . import auth, comment, following, label, message, oss, star, topic, user, video
from . import emotion, diary, soul  # 新增：心情烘焙坊功能
from . import mind  # 新增：心灵配方


def create_v2():
    bp = BluePrint('v2', __name__)

    # 原有API
    auth.api.register(bp)
    comment.api.register(bp)
    following.api.register(bp)
    label.api.register(bp)
    message.api.register(bp)
    oss.api.register(bp)
    star.api.register(bp)
    topic.api.register(bp)
    user.api.register(bp)
    video.api.register(bp)
    
    # 新增API - 心情烘焙坊
    emotion.api.register(bp)  # 情绪标签API
    diary.api.register(bp)    # 日记API
    soul.api.register(bp)      # 心灵鸡汤API

    # 新增API - 心灵配方
    mind.api.register(bp)

    return bp
