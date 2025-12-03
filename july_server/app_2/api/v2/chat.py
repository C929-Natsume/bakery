# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2023 by Jeffrey.
    :license: Apache 2.0, see LICENSE for more details.
"""
from app_2 import auth
from app_2.lib.exception import Success
from app_2.lib.red_print import RedPrint
from app_2.lib.schema import paginator_schema
from app_2.service.chat import get_chat_list
from app_2.validator.forms import GetChatListValidator

api = RedPrint('chat')


@api.route('/', methods=['GET'])
@auth.login_required
def get_chats():
    """
    获取聊天记录
    """
    form = GetChatListValidator()
    room_id = form.get_data('room_id')
    chat_id = form.get_data('chat_id')

    chats = get_chat_list(room_id=room_id, chat_id=chat_id)
    return Success(data=paginator_schema(chats))
