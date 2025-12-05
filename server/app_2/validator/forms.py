# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from wtforms import IntegerField, StringField, BooleanField, FieldList
from wtforms.validators import NumberRange

from app_2.lib.enums import GenderType
from app_2.patch.validator import Form, DataRequired, SelectField


class PaginateValidator(Form):
    page = IntegerField('页数', default=1, validators=[NumberRange(min=1, message='页数不合法')])
    size = IntegerField('条数', default=20, validators=[NumberRange(min=1, max=100, message='条数不合法')])

    def validate_page(self, value):
        self.page.data = int(value.data)

    def validate_size(self, value):
        self.size.data = int(value.data)


class PassiveAuthValidator(Form):
    code = StringField('code', validators=[DataRequired(message='code不能为空')])


class InitiativeAuthValidator(PassiveAuthValidator):
    encrypted_data = StringField('encrypted_data', validators=[DataRequired(message='encrypted_data不能为空')])
    iv = StringField('iv', validators=[DataRequired(message='iv不能为空')])


class UpdateUserValidator(Form):
    nickname = StringField('昵称', validators=[DataRequired(message='昵称不能为空')])
    avatar = StringField('头像', validators=[DataRequired(message='头像不能为空')])
    gender = SelectField('性别', choices=GenderType.choices(), validators=[DataRequired(message='性别不能为空')])
    signature = StringField('个性签名')
    poster = StringField('封面')


class GetLabelListValidator(Form):
    topic_id = StringField('话题标识')


class GetTopicListValidator(PaginateValidator):
    label_id = StringField('标签标识')
    user_id = StringField('用户标识')


class CreateTopicValidator(Form):
    content = StringField('内容', validators=[DataRequired(message='内容不能为空')])
    title = StringField('标题')
    is_anon = BooleanField('是否匿名')
    images = FieldList(StringField(), '图片')
    labels = FieldList(StringField(), '标签')
    video_id = StringField('视频标识')
    emotion_label_id = StringField('情绪标签标识')  # Week 2新增


class CreateVideoValidator(Form):
    src = StringField('地址', validators=[DataRequired(message='地址不能为空')])
    cover = StringField('封面')
    width = IntegerField('宽度')
    height = IntegerField('高度')
    duration = IntegerField('时长')
    size = IntegerField('大小')


class GetCommentListValidator(PaginateValidator):
    topic_id = StringField('话题标识')
    user_id = StringField('用户标识')


class CreateCommentValidator(Form):
    content = StringField('内容', validators=[DataRequired(message='内容不能为空')])
    topic_id = StringField('话题标识', validators=[DataRequired(message='话题标识不能为空')])
    comment_id = StringField('父评论标识')
    is_anon = BooleanField('是否匿名')


class GetStarListValidator(PaginateValidator):
    topic_id = StringField('话题标识')
    user_id = StringField('用户标识')


class FollowOrCancelValidator(Form):
    follow_user_id = StringField('关注用户标识', validators=[DataRequired(message='关注用户标识不能为空')])


class GetFollowingListValidator(PaginateValidator):
    user_id = StringField('用户标识')
    follow_user_id = StringField('关注用户标识')


class StarOrCancelValidator(Form):
    topic_id = StringField('话题标识', validators=[DataRequired(message='话题标识不能为空')])


