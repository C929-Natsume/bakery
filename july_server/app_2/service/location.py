# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2023 by Jeffrey.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import request, g

from app_2.manger.weixin.lbs import ip2region


def update_ip_belong():
    """
    更新 IP 归属地: 发布话题、评论时触发
    开发模式：完全禁用LBS，避免API配额问题
    """
    # 开发模式：直接返回None，不调用LBS API
    from flask import current_app
    current_app.logger.info("开发模式：跳过IP归属地获取")
    return None
    
    # 生产环境可以启用以下代码：
    # try:
    #     if request.remote_addr is not None:
    #         region = ip2region(request.remote_addr)
    #         if region is not None:
    #             g.user.update(ip_belong=region)
    #             return region
    # except Exception as e:
    #     current_app.logger.warning(f"IP归属地获取失败: {e}")
    # return None
