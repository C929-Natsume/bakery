# -*- coding: utf-8 -*-
"""
    日记API
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import current_app, g, request
from datetime import datetime

from app_2.lib.exception import Success, ParameterError, NotFound, Forbidden
from app_2.lib.red_print import RedPrint
from app_2.lib.token import auth
from app_2.model.diary import Diary
from app_2.model.emotion_label import EmotionLabel

api = RedPrint('diary')


@api.route('', methods=['POST'])
def create_diary():
    """
    创建日记
    开发模式：未登录时使用测试用户ID
    """
    data = request.get_json()
    
    content = data.get('content')
    emotion_label_id = data.get('emotion_label_id')
    diary_date_str = data.get('diary_date')
    is_public = data.get('is_public', True)  # 开发模式默认公开
    weather = data.get('weather')
    location = data.get('location')
    images = data.get('images', [])
    
    # 获取用户ID（必须登录）
    try:
        auth.login_required()
        user_id = g.user.id
        current_app.logger.info(f"创建日记, 已登录用户ID: {user_id}")
    except Exception as e:
        # 未登录时记录警告并返回错误
        current_app.logger.warning(f"创建日记失败: 用户未登录或token无效, 错误: {str(e)}")
        raise Forbidden(msg='请先登录后再创建日记')
    
    # 参数验证
    if not content:
        raise ParameterError(msg='日记内容不能为空')
    
    if len(content) > 10000:
        raise ParameterError(msg='日记内容不能超过10000字')
    
    # 解析日期
    try:
        if diary_date_str:
            diary_date = datetime.strptime(diary_date_str, '%Y-%m-%d').date()
        else:
            diary_date = datetime.now().date()
    except ValueError:
        raise ParameterError(msg='日期格式错误，应为YYYY-MM-DD')
    
    # 检查该日期是否已有日记
    existing = Diary.get_by_date(user_id, diary_date)
    if existing:
        raise ParameterError(msg='该日期已有日记，请修改或删除后再创建')
    
    # 验证情绪标签
    if emotion_label_id:
        label = EmotionLabel.get_one(id=emotion_label_id, delete_time=None)
        if not label:
            raise NotFound(msg='情绪标签不存在')
    
    # 创建日记
    diary = Diary.create(
        user_id=user_id,
        content=content,
        emotion_label_id=emotion_label_id,
        diary_date=diary_date,
        is_public=is_public,
        weather=weather,
        location=location,
        images=images
    )
    
    current_app.logger.info(f"创建日记, 用户ID: {user_id}, 日期: {diary_date}")
    
    return Success(data=diary, msg='创建成功')


@api.route('/<diary_id>', methods=['GET'])
def get_diary(diary_id):
    """
    获取日记详情
    开发模式：可查看所有日记
    """
    diary = Diary.get_or_404(id=diary_id, delete_time=None)
    
    # 权限检查（开发模式放宽）
    try:
        auth.login_required()
        if not diary.is_public and diary.user_id != g.user.id:
            raise Forbidden(msg='无权查看该日记')
    except:
        # 开发模式：可以查看所有日记
        pass
    
    return Success(data=diary)


@api.route('/<diary_id>', methods=['PUT'])
def update_diary(diary_id):
    """
    更新日记
    开发模式：可修改所有日记
    """
    diary = Diary.get_or_404(id=diary_id, delete_time=None)
    
    # 权限检查（开发模式放宽）
    try:
        auth.login_required()
        if diary.user_id != g.user.id:
            raise Forbidden(msg='无权修改该日记')
    except:
        # 开发模式：可以修改所有日记
        pass
    
    data = request.get_json()
    
    # 可更新的字段
    if 'content' in data:
        if not data['content']:
            raise ParameterError(msg='日记内容不能为空')
        diary.content = data['content']
    
    if 'emotion_label_id' in data:
        if data['emotion_label_id']:
            label = EmotionLabel.get_one(id=data['emotion_label_id'], delete_time=None)
            if not label:
                raise NotFound(msg='情绪标签不存在')
        diary.emotion_label_id = data['emotion_label_id']
    
    if 'is_public' in data:
        diary.is_public = data['is_public']
    
    if 'weather' in data:
        diary.weather = data['weather']
    
    if 'location' in data:
        diary.location = data['location']
    
    if 'images' in data:
        diary.images = data['images']
    
    diary.save()
    
    current_app.logger.info(f"用户更新日记, 日记ID: {diary_id}")
    
    return Success(data=diary, msg='更新成功')


@api.route('/<diary_id>', methods=['DELETE'])
def delete_diary(diary_id):
    """
    删除日记
    开发模式：可删除所有日记
    """
    diary = Diary.get_or_404(id=diary_id, delete_time=None)
    
    # 权限检查（开发模式放宽）
    try:
        auth.login_required()
        if diary.user_id != g.user.id:
            raise Forbidden(msg='无权删除该日记')
        user_id = g.user.id
    except:
        # 开发模式：可以删除所有日记
        user_id = 'test_user_diary_dev'
    
    diary.delete()
    
    current_app.logger.info(f"删除日记, 用户ID: {user_id}, 日记ID: {diary_id}")
    
    return Success(msg='删除成功')


@api.route('/calendar', methods=['GET'])
@auth.login_required
def get_calendar():
    """
    获取日历视图数据
    返回指定月份的所有日记
    """
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # 参数验证
    if not (1 <= month <= 12):
        raise ParameterError(msg='月份必须在1-12之间')
    
    if not (2000 <= year <= 2100):
        raise ParameterError(msg='年份范围错误')
    
    # 获取该月的所有日记
    diaries = Diary.get_month_diaries(g.user.id, year, month)
    
    # 转换为日历格式
    calendar_data = {}
    for diary in diaries:
        date_str = diary.diary_date.strftime('%Y-%m-%d')
        calendar_data[date_str] = {
            'id': diary.id,
            'has_content': True,
            'emotion_label': diary.emotion_label,
            'is_public': diary.is_public,
            'weather': diary.weather
        }
    
    current_app.logger.info(f"获取日历数据, 用户ID: {g.user.id}, 年月: {year}-{month}")
    
    return Success(data={
        'year': year,
        'month': month,
        'diaries': calendar_data
    })


@api.route('/list', methods=['GET'])
def get_diary_list():
    """
    获取日记列表（分页）
    开发模式：未登录时返回所有日记（包括私密日记）
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    
    # 检查是否登录
    try:
        auth.login_required()
        # 已登录：返回用户的日记
        pagination = Diary.query.filter_by(
            user_id=g.user.id,
            delete_time=None
        ).order_by(Diary.diary_date.desc()).paginate(page=page, size=size)
    except:
        # 未登录：返回所有日记（开发模式，包括私密日记）
        pagination = Diary.query.filter_by(
            delete_time=None
        ).order_by(Diary.diary_date.desc()).paginate(page=page, size=size)
    
    return Success(data={
        'items': pagination.items,
        'total_count': pagination.total,
        'current_page': pagination.page,
        'total_page': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@api.route('/public', methods=['GET'])
def get_public_diaries():
    """
    获取公开日记列表
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    
    pagination = Diary.get_public_diaries(page, size)
    
    return Success(data={
        'items': pagination.items,
        'total_count': pagination.total,
        'current_page': pagination.page,
        'total_page': pagination.pages
    })


@api.route('/date/<date_str>', methods=['GET'])
@auth.login_required
def get_diary_by_date(date_str):
    """
    根据日期获取日记
    """
    try:
        diary_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ParameterError(msg='日期格式错误，应为YYYY-MM-DD')
    
    diary = Diary.get_by_date(g.user.id, diary_date)
    
    if not diary:
        raise NotFound(msg='该日期没有日记')
    
    return Success(data=diary)

