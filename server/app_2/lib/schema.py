# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from app_2.model.user import User
from app_2.patch.db import Pagination


def paginator_schema(pagination: Pagination):
    """
    分页响应格式
    """
    return {
        'items': pagination.items,
        'current_page': pagination.page,
        'next_page': pagination.next_num,
        'prev_page': pagination.prev_num,
        'total_page': pagination.pages,
        'total_count': pagination.total
    }


