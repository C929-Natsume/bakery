# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2023 by Jeffrey.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import g

from app_2 import db
from app_2.lib.enums import MessageCategory
from app_2.lib.exception import NotFound, Success, Deleted, Created
from app_2.lib.red_print import RedPrint
from app_2.lib.schema import paginator_schema
from app_2.lib.token import auth
from app_2.model.comment import Comment
from app_2.model.message import Message
from app_2.model.topic import Topic
from app_2.service.comment import create_comment_verify, get_comment_list
from app_2.validator.forms import CreateCommentValidator, GetCommentListValidator

api = RedPrint('comment')


@api.route('/', methods=['GET'])
def get_comments():
    """
    获取评论列表
    """
    form = GetCommentListValidator()
    topic_id = form.get_data('topic_id')
    user_id = form.get_data('user_id')

    comments = get_comment_list(topic_id=topic_id, user_id=user_id)
    return Success(data=paginator_schema(comments))


@api.route('/', methods=['POST'])
@auth.login_required
def create_comment():
    """
    发布评论
    """
    form = CreateCommentValidator()
    create_comment_verify(form=form)
    return Created()


@api.route('/<comment_id>', methods=['DELETE'])
@auth.login_required
def delete_comment(comment_id):
    """
    删除评论
    """
    comment = Comment.get_one(id=comment_id)
    if comment is None:
        raise NotFound(msg='评论不存在')

    topic = Topic.get_one(id=comment.topic_id)
    exist_msg = Message.get_one(category=MessageCategory.COMMENT, user_id=topic.user_id, action_user_id=g.user.id,
                                topic_id=topic.id, is_read=False)

    with db.auto_commit():
        comment.delete(commit=False)
        if exist_msg is not None:
            exist_msg.delete(comment=False)

    # 更新话题评论数
    topic.update(comment_count=Comment.get_comment_count(topic_id=topic.id))
    return Deleted()
