# -*- coding: utf-8 -*-
"""
    情绪标签API
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
from flask import current_app, g, request

from app.lib.exception import Success, ParameterError, NotFound
from app.lib.red_print import RedPrint
from app.lib.token import auth
from app.model.emotion_label import EmotionLabel, EmotionLabelType
from app.model.emotion_stat import EmotionStat

api = RedPrint('emotion')


@api.route('/label', methods=['GET'])
def get_labels():
    """
    获取情绪标签列表
    包含系统标签和用户自定义标签
    """
    # 获取系统标签
    system_labels = EmotionLabel.get_system_labels()
    
    # 如果用户已登录，获取自定义标签
    custom_labels = []
    if g.user:
        custom_labels = EmotionLabel.get_user_labels(g.user.id)
    
    # 获取热门标签
    popular_labels = EmotionLabel.get_popular_labels(limit=10)
    
    current_app.logger.info(f"获取情绪标签列表成功")
    
    return Success(data={
        'system_labels': system_labels,
        'custom_labels': custom_labels,
        'popular_labels': popular_labels
    })


@api.route('/label', methods=['POST'])
@auth.login_required
def create_label():
    """
    创建自定义情绪标签
    """
    data = request.get_json()
    
    name = data.get('name')
    color = data.get('color', '#337559')
    icon = data.get('icon', '')
    
    if not name or len(name) > 20:
        raise ParameterError(msg='标签名称不能为空且不超过20个字符')
    
    # 检查是否已存在相同名称的标签
    existing = EmotionLabel.query.filter_by(
        name=name,
        user_id=g.user.id,
        delete_time=None
    ).first()
    
    if existing:
        raise ParameterError(msg='该标签已存在')
    
    # 创建标签
    label = EmotionLabel.create(
        name=name,
        color=color,
        icon=icon,
        type=EmotionLabelType.CUSTOM,
        user_id=g.user.id
    )
    
    current_app.logger.info(f"用户创建自定义标签成功, 用户ID: {g.user.id}, 标签: {name}")
    
    return Success(data=label, msg='创建成功')


@api.route('/label/<label_id>', methods=['DELETE'])
@auth.login_required
def delete_label(label_id):
    """
    删除自定义情绪标签
    """
    label = EmotionLabel.get_or_404(id=label_id, delete_time=None)
    
    # 只能删除自己的自定义标签
    if label.type != EmotionLabelType.CUSTOM or label.user_id != g.user.id:
        raise ParameterError(msg='无法删除该标签')
    
    label.delete()
    
    current_app.logger.info(f"用户删除自定义标签, 用户ID: {g.user.id}, 标签ID: {label_id}")
    
    return Success(msg='删除成功')


@api.route('/stat', methods=['GET'])
@auth.login_required
def get_emotion_stats():
    """
    获取用户情绪统计
    支持按时间范围查询
    """
    from datetime import datetime, timedelta
    
    # 获取查询参数
    days = request.args.get('days', 30, type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # 解析日期
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ParameterError(msg='日期格式错误，应为YYYY-MM-DD')
    else:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
    
    # 获取统计数据
    stats = EmotionStat.get_user_stats(g.user.id, start_date, end_date)
    
    # 获取情绪分布
    distribution = EmotionStat.get_emotion_distribution(g.user.id, days)
    
    # 获取情绪趋势
    trend = EmotionStat.get_emotion_trend(g.user.id, days)
    
    # 生成情绪洞察
    insights = _generate_emotion_insights(distribution, trend)
    
    current_app.logger.info(f"获取用户情绪统计, 用户ID: {g.user.id}, 天数: {days}")
    
    return Success(data={
        'stats': stats,
        'distribution': distribution,
        'trend': trend,
        'insights': insights,
        'date_range': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
    })


@api.route('/wave', methods=['GET'])
@auth.login_required
def get_emotion_wave():
    """
    获取情绪波动图数据
    """
    days = request.args.get('days', 30, type=int)
    
    # 获取情绪趋势
    trend = EmotionStat.get_emotion_trend(g.user.id, days)
    
    # 转换为图表数据格式
    wave_data = _convert_to_wave_data(trend)
    
    current_app.logger.info(f"获取情绪波动图, 用户ID: {g.user.id}, 天数: {days}")
    
    return Success(data=wave_data)


def _generate_emotion_insights(distribution, trend):
    """
    生成情绪洞察
    基于统计数据生成有意义的洞察
    """
    insights = []
    
    if not distribution:
        return ['暂无足够数据生成洞察']
    
    # 最常见的情绪
    top_emotion = distribution[0]
    insights.append(f"最近你最常感受到的是\"{top_emotion['emotion_label'].name}\"，共{top_emotion['count']}次")
    
    # 情绪多样性
    emotion_count = len(distribution)
    if emotion_count >= 5:
        insights.append(f"你的情绪很丰富，记录了{emotion_count}种不同的情绪状态")
    elif emotion_count <= 2:
        insights.append("试着记录更多不同的情绪，这有助于更好地了解自己")
    
    # 积极情绪占比
    positive_emotions = ['开心', '兴奋', '平静', '期待', '感动']
    positive_count = sum(d['count'] for d in distribution if d['emotion_label'].name in positive_emotions)
    total_count = sum(d['count'] for d in distribution)
    
    if total_count > 0:
        positive_ratio = positive_count / total_count
        if positive_ratio >= 0.6:
            insights.append(f"你的积极情绪占比{int(positive_ratio*100)}%，保持这份美好！✨")
        elif positive_ratio <= 0.3:
            insights.append("最近可能有些不顺，但请相信一切都会好起来的 💪")
    
    return insights


def _convert_to_wave_data(trend):
    """
    将趋势数据转换为图表格式
    """
    wave_data = {
        'dates': [],
        'series': {}
    }
    
    # 获取所有日期
    dates = sorted(trend.keys())
    wave_data['dates'] = dates
    
    # 按情绪标签组织数据
    for date in dates:
        emotions = trend[date]
        for emotion_data in emotions:
            label_name = emotion_data['emotion_label'].name
            if label_name not in wave_data['series']:
                wave_data['series'][label_name] = {
                    'name': label_name,
                    'color': emotion_data['emotion_label'].color,
                    'data': []
                }
            wave_data['series'][label_name]['data'].append(emotion_data['count'])
    
    # 填充缺失数据
    for label_name in wave_data['series']:
        while len(wave_data['series'][label_name]['data']) < len(dates):
            wave_data['series'][label_name]['data'].append(0)
    
    return wave_data

