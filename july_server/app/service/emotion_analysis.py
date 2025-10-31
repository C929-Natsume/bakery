# -*- coding: utf-8 -*-
"""
智能情绪分析服务
基于用户近7天的发帖、日记和浏览内容，智能确定今日情绪标签
使用 DeepSeek V3 进行智能分类
"""
from datetime import datetime, timedelta
from collections import defaultdict
import math
from flask import current_app
from sqlalchemy import and_

from app.model.diary import Diary
from app.model.topic import Topic
from app.model.star import Star
from app.model.comment import Comment
from app.model.emotion_label import EmotionLabel
from app.service.llm_service import LLMService


class EmotionAnalysisService:
    """智能情绪分析服务"""
    
    @classmethod
    def analyze_user_emotion_today(cls, user_id):
        """
        分析用户今日情绪标签
        基于近7天的发帖、日记和浏览内容
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: {
                'emotion_label_id': '情绪标签ID',
                'emotion_name': '情绪标签名称',
                'confidence': 0.85,  # 置信度 (0-1)
                'analysis': '分析说明',
                'factors': {
                    'diary_count': 3,
                    'topic_count': 5,
                    'browse_count': 10,
                    'emotion_scores': {...}
                }
            }
        """
        # 计算7天前的日期
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        current_app.logger.info(
            f"开始分析用户情绪, 用户ID: {user_id}, "
            f"时间范围: {start_date} 至 {end_date}"
        )
        
        # 1. 获取近7天的日记内容和情绪
        diary_emotions = cls._get_diary_emotions(user_id, start_date, end_date)
        
        # 2. 获取近7天的发帖内容和情绪
        topic_emotions = cls._get_topic_emotions(user_id, start_date, end_date)
        
        # 3. 获取近7天的评论内容和情绪
        comment_emotions = cls._get_comment_emotions(user_id, start_date, end_date)
        
        # 4. 获取近7天的浏览内容情绪（通过收藏、评论等行为推断）
        browse_emotions = cls._get_browse_emotions(user_id, start_date, end_date)
        
        # 5. 综合分析，计算情绪得分
        emotion_scores = cls._calculate_emotion_scores(
            diary_emotions, topic_emotions, comment_emotions, browse_emotions
        )
        
        # 5. 选择得分最高的情绪标签
        best_emotion = cls._select_best_emotion(emotion_scores)
        
        # 6. 生成分析报告
        analysis = cls._generate_analysis(
            best_emotion, diary_emotions, topic_emotions, comment_emotions, browse_emotions
        )
        
        # 统计实际的日记、话题和评论数量（去重，因为每个可能产生标签+DeepSeek两条记录）
        unique_diary_dates = set(emotion['date'] for emotion in diary_emotions)
        unique_topic_dates = set(emotion['date'] for emotion in topic_emotions)
        unique_comment_dates = set(emotion['date'] for emotion in comment_emotions)
        
        # 统计来源类型
        label_count = sum(1 for e in diary_emotions + topic_emotions if e.get('source') == 'label')
        deepseek_count = sum(1 for e in diary_emotions + topic_emotions + comment_emotions if e.get('source') == 'deepseek')
        
        return {
            'emotion_label_id': best_emotion['id'],
            'emotion_name': best_emotion['name'],
            'confidence': best_emotion['confidence'],
            'analysis': analysis,
            'factors': {
                'diary_count': len(unique_diary_dates),  # 实际日记数量
                'topic_count': len(unique_topic_dates),  # 实际话题数量
                'comment_count': len(unique_comment_dates),  # 实际评论数量
                'browse_count': browse_emotions.get('total', 0),
                'label_count': label_count,  # 标签来源的记录数
                'deepseek_count': deepseek_count,  # DeepSeek分析的记录数
                'emotion_scores': emotion_scores
            }
        }
    
    @classmethod
    def _get_diary_emotions(cls, user_id, start_date, end_date):
        """
        获取用户近7天的日记情绪
        返回: [{'emotion_id': 'xxx', 'emotion_name': '开心', 'weight': 1.0}, ...]
        """
        current_app.logger.info(
            f"查询日记情绪, 用户ID: {user_id}, "
            f"时间范围: {start_date} 至 {end_date}"
        )
        
        # 首先检查该用户是否存在任何日记（用于调试）
        all_user_diaries = Diary.query.filter_by(
            user_id=user_id,
            delete_time=None
        ).all()
        
        current_app.logger.info(
            f"用户 {user_id} 总共有 {len(all_user_diaries)} 条日记（不限时间）"
        )
        
        # 检查是否有其他用户ID的日记（用于诊断user_id不匹配问题）
        all_diaries_sample = Diary.query.filter_by(
            delete_time=None
        ).limit(10).all()
        
        if all_diaries_sample:
            user_ids_in_db = set(d.user_id for d in all_diaries_sample)
            current_app.logger.info(
                f"数据库中的用户ID示例（前10条日记）: {list(user_ids_in_db)}"
            )
            if user_id not in user_ids_in_db:
                current_app.logger.warning(
                    f"⚠️ 警告：查询的用户ID '{user_id}' 不在示例日记的用户ID列表中！"
                    f"可能的原因：用户ID不匹配或该用户确实没有日记。"
                )
        
        # 查询日记
        diaries = Diary.query.filter(
            and_(
                Diary.user_id == user_id,
                Diary.diary_date >= start_date,
                Diary.diary_date <= end_date,
                Diary.delete_time == None
            )
        ).order_by(Diary.diary_date.desc()).all()
        
        current_app.logger.info(
            f"查询到日记数量: {len(diaries)}, 用户ID: {user_id}"
        )
        
        # 如果没有查询到日记，记录详细信息用于调试
        if len(diaries) == 0:
            # 检查是否有任何日记（不限制时间）
            current_app.logger.warning(
                f"⚠️ 用户 {user_id} 在时间范围 {start_date} 至 {end_date} 内没有日记。"
                f"该用户共有 {len(all_user_diaries)} 条日记（不限时间）。"
            )
            
            # 如果有日记但不在此时间范围内，显示最近几条日记的日期
            if all_user_diaries:
                recent_dates = [d.diary_date for d in all_user_diaries[:5]]
                current_app.logger.info(
                    f"用户最近的日记日期: {recent_dates}"
                )
                # 显示最近日记的user_id（验证是否匹配）
                if all_user_diaries:
                    latest_diary = all_user_diaries[0]
                    current_app.logger.info(
                        f"最近日记的user_id: '{latest_diary.user_id}' "
                        f"(查询的user_id: '{user_id}', 是否匹配: {latest_diary.user_id == user_id})"
                    )
            else:
                current_app.logger.error(
                    f"❌ 用户 {user_id} 没有任何日记！"
                )
        
        emotions = []
        for diary in diaries:
            base_weight = 2.0  # 日记基础权重较高
            
            # 如果已有情绪标签，使用标签（权重70%）
            if diary.emotion_label_id:
                # 获取完整的日期时间信息用于精确的时间权重计算
                diary_datetime = datetime.combine(diary.diary_date, datetime.min.time())
                if hasattr(diary, 'create_time') and diary.create_time:
                    diary_datetime = diary.create_time
                
                label_emotion = {
                    'emotion_id': diary.emotion_label_id,
                    'emotion_name': diary.emotion_label.name if diary.emotion_label else '未知',
                    'weight': base_weight * 0.7,  # 标签权重70%
                    'content': diary.content[:100],
                    'date': diary.diary_date,
                    'datetime': diary_datetime,  # 添加完整时间信息
                    'source': 'label'  # 标记来源为标签
                }
                emotions.append(label_emotion)
            
            # 同时使用 DeepSeek 分析内容（权重30%）
            inferred_name = LLMService.analyze_emotion_from_text(diary.content)
            if inferred_name:
                emotion_label = EmotionLabel.query.filter_by(
                    name=inferred_name, delete_time=None
                ).first()
                if emotion_label:
                    # 获取完整的日期时间信息
                    diary_datetime = datetime.combine(diary.diary_date, datetime.min.time())
                    if hasattr(diary, 'create_time') and diary.create_time:
                        diary_datetime = diary.create_time
                    
                    inferred_emotion = {
                        'emotion_id': emotion_label.id,
                        'emotion_name': emotion_label.name,
                        'weight': base_weight * 0.3,  # DeepSeek分析权重30%
                        'content': diary.content[:100],
                        'date': diary.diary_date,
                        'datetime': diary_datetime,  # 添加完整时间信息
                        'source': 'deepseek'  # 标记来源为DeepSeek
                    }
                    emotions.append(inferred_emotion)
                    
                    label_name = diary.emotion_label.name if diary.emotion_label_id and diary.emotion_label else '无'
                    current_app.logger.info(
                        f"日记DeepSeek分析: 内容={diary.content[:50]}..., "
                        f"原标签={label_name}, "
                        f"DeepSeek分析={inferred_name}"
                    )
            else:
                current_app.logger.warning(f"日记DeepSeek分析失败或无结果: {diary.content[:50]}...")
        
        return emotions
    
    @classmethod
    def _get_topic_emotions(cls, user_id, start_date, end_date):
        """
        获取用户近7天的发帖情绪
        返回: [{'emotion_id': 'xxx', 'emotion_name': '开心', 'weight': 1.5}, ...]
        """
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        topics = Topic.query.filter(
            and_(
                Topic.user_id == user_id,
                Topic.create_time >= start_datetime,
                Topic.create_time <= end_datetime,
                Topic.delete_time == None
            )
        ).order_by(Topic.create_time.desc()).all()
        
        emotions = []
        for topic in topics:
            base_weight = 1.5  # 发帖基础权重中等
            
            # 如果已有情绪标签，使用标签（权重70%）
            if topic.emotion_label_id:
                topic_datetime = topic.create_time if topic.create_time else datetime.combine(datetime.now().date(), datetime.min.time())
                
                label_emotion = {
                    'emotion_id': topic.emotion_label_id,
                    'emotion_name': topic.emotion_label.name if topic.emotion_label else '未知',
                    'weight': base_weight * 0.7,  # 标签权重70%
                    'content': topic.content[:100],
                    'date': topic.create_time.date(),
                    'datetime': topic_datetime,  # 添加完整时间信息
                    'source': 'label'  # 标记来源为标签
                }
                emotions.append(label_emotion)
            
            # 同时使用 DeepSeek 分析内容（权重30%）
            inferred_name = LLMService.analyze_emotion_from_text(topic.content)
            if inferred_name:
                emotion_label = EmotionLabel.query.filter_by(
                    name=inferred_name, delete_time=None
                ).first()
                if emotion_label:
                    topic_datetime = topic.create_time if topic.create_time else datetime.combine(datetime.now().date(), datetime.min.time())
                    
                    inferred_emotion = {
                        'emotion_id': emotion_label.id,
                        'emotion_name': emotion_label.name,
                        'weight': base_weight * 0.3,  # DeepSeek分析权重30%
                        'content': topic.content[:100],
                        'date': topic.create_time.date(),
                        'datetime': topic_datetime,  # 添加完整时间信息
                        'source': 'deepseek'  # 标记来源为DeepSeek
                    }
                    emotions.append(inferred_emotion)
                    
                    label_name = topic.emotion_label.name if topic.emotion_label_id and topic.emotion_label else '无'
                    current_app.logger.info(
                        f"话题DeepSeek分析: 内容={topic.content[:50]}..., "
                        f"原标签={label_name}, "
                        f"DeepSeek分析={inferred_name}"
                    )
            else:
                current_app.logger.warning(f"话题DeepSeek分析失败或无结果: {topic.content[:50]}...")
        
        return emotions
    
    @classmethod
    def _get_browse_emotions(cls, user_id, start_date, end_date):
        """
        获取用户近7天的浏览内容情绪
        通过收藏、评论等行为推断用户浏览偏好
        
        返回: {
            'total': 10,
            'emotions': [{'emotion_id': 'xxx', 'weight': 0.8}, ...]
        }
        """
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # 通过收藏的帖子推断
        stars = Star.query.filter(
            and_(
                Star.user_id == user_id,
                Star.create_time >= start_datetime,
                Star.create_time <= end_datetime,
                Star.delete_time == None
            )
        ).all()
        
        browse_emotions = []
        
        for star in stars:
            topic = Topic.get_one(id=star.topic_id, delete_time=None)
            if topic:
                # 使用收藏时间作为浏览时间
                browse_date = star.create_time.date() if star.create_time else datetime.now().date()
                
                if topic.emotion_label_id:
                    browse_emotions.append({
                        'emotion_id': topic.emotion_label_id,
                        'emotion_name': topic.emotion_label.name if topic.emotion_label else '未知',
                        'weight': 0.8,  # 浏览权重较低
                        'type': 'star',  # 通过收藏推断
                        'date': browse_date  # 添加日期信息用于时间权重计算
                    })
                else:
                    # 如果没有情绪标签，使用 DeepSeek 分析收藏的内容
                    inferred_name = LLMService.analyze_emotion_from_text(topic.content)
                    if inferred_name:
                        emotion_label = EmotionLabel.query.filter_by(
                            name=inferred_name, delete_time=None
                        ).first()
                        if emotion_label:
                            browse_emotions.append({
                                'emotion_id': emotion_label.id,
                                'emotion_name': emotion_label.name,
                                'weight': 0.6,  # 推断的浏览情绪权重更低
                                'type': 'star_inferred',
                                'date': browse_date  # 添加日期信息用于时间权重计算
                            })
        
        return {
            'total': len(browse_emotions),
            'emotions': browse_emotions
        }
    
    @classmethod
    def _get_comment_emotions(cls, user_id, start_date, end_date):
        """
        获取用户近7天的评论情绪
        返回: [{'emotion_id': 'xxx', 'emotion_name': '开心', 'weight': 0.3}, ...]
        评论权重为30%（基础权重1.0 * 30% = 0.3）
        """
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        current_app.logger.info(
            f"查询评论情绪, 用户ID: {user_id}, "
            f"时间范围: {start_date} 至 {end_date}"
        )
        
        # 查询评论
        comments = Comment.query.filter(
            and_(
                Comment.user_id == user_id,
                Comment.create_time >= start_datetime,
                Comment.create_time <= end_datetime,
                Comment.delete_time == None
            )
        ).order_by(Comment.create_time.desc()).all()
        
        current_app.logger.info(
            f"查询到评论数量: {len(comments)}, 用户ID: {user_id}"
        )
        
        emotions = []
        base_weight = 1.0  # 评论基础权重
        
        for comment in comments:
            # 评论没有情绪标签，完全依赖 DeepSeek 分析（权重30%）
            inferred_name = LLMService.analyze_emotion_from_text(comment.content)
            if inferred_name:
                emotion_label = EmotionLabel.query.filter_by(
                    name=inferred_name, delete_time=None
                ).first()
                if emotion_label:
                    comment_datetime = comment.create_time if comment.create_time else datetime.combine(
                        datetime.now().date(), datetime.min.time()
                    )
                    
                    inferred_emotion = {
                        'emotion_id': emotion_label.id,
                        'emotion_name': emotion_label.name,
                        'weight': base_weight * 0.3,  # 评论权重30%
                        'content': comment.content[:100],
                        'date': comment.create_time.date(),
                        'datetime': comment_datetime,  # 添加完整时间信息
                        'source': 'deepseek'  # 标记来源为DeepSeek
                    }
                    emotions.append(inferred_emotion)
                    
                    current_app.logger.info(
                        f"评论DeepSeek分析: 内容={comment.content[:50]}..., "
                        f"DeepSeek分析={inferred_name}"
                    )
            else:
                current_app.logger.warning(f"评论DeepSeek分析失败或无结果: {comment.content[:50]}...")
        
        return emotions
    
    @classmethod
    def _calculate_emotion_scores(cls, diary_emotions, topic_emotions, comment_emotions, browse_emotions):
        """
        计算各情绪标签的加权得分
        
        权重说明：
        - 日记：2.0（最重要）
        - 发帖：1.5（中等）
        - 评论：1.0 * 30% = 0.3（基础权重1.0，整体权重30%）
        - 浏览：0.8（较低）
        - 时间权重：按时间顺序，越新权重越高
          * 今天：权重 100%
          * 1天前：权重 85%
          * 2天前：权重 70%
          * 3天前：权重 55%
          * 4天前：权重 45%
          * 5天前：权重 35%
          * 6天前：权重 28%
          * 7天前：权重 22%
        - 顺序权重：同一时间内的内容，按顺序给予额外权重（最近的最重要）
        """
        emotion_scores = defaultdict(float)
        today = datetime.now().date()
        
        # 时间衰减函数：使用改进的衰减算法，时间越早权重越低
        def get_time_weight(days_ago, hour_ago=None):
            """
            根据距离今天的天数和小时数计算时间权重
            days_ago: 距离今天的天数
            hour_ago: 距离今天的小时数（可选，用于同一天内的细化）
            """
            # 基础时间衰减：使用更明显的衰减曲线
            if days_ago == 0:
                # 今天的内容，进一步按小时衰减
                if hour_ago is not None:
                    # 今天的内容，按小时衰减：最近1小时=100%, 24小时前=80%
                    hour_weight = 1.0 / (1 + hour_ago * 0.02)
                    return max(hour_weight, 0.8)
                else:
                    return 1.0
            else:
                # 使用分段衰减，前3天衰减较快，后4天衰减较慢
                if days_ago <= 3:
                    # 前3天：快速衰减
                    decay_rate = 0.15
                else:
                    # 后4天：慢速衰减
                    decay_rate = 0.08
                
                time_weight = 1.0 / (1 + days_ago * decay_rate)
                # 确保最小权重不低于0.15（即使7天前也有一定影响）
                return max(time_weight, 0.15)
        
        # 按时间顺序对情绪进行排序（最新的在前）
        # 优先使用datetime精确排序，如果没有则使用date
        def get_sort_key(emotion):
            if 'datetime' in emotion and emotion['datetime']:
                return emotion['datetime']
            elif 'date' in emotion:
                return datetime.combine(emotion['date'], datetime.max.time())
            else:
                return datetime.min
        
        diary_emotions_sorted = sorted(diary_emotions, key=get_sort_key, reverse=True)
        topic_emotions_sorted = sorted(topic_emotions, key=get_sort_key, reverse=True)
        comment_emotions_sorted = sorted(comment_emotions, key=get_sort_key, reverse=True)
        
        # 计算日记情绪得分（按时间顺序）
        for idx, emotion in enumerate(diary_emotions_sorted):
            days_ago = (today - emotion['date']).days
            
            # 如果是今天的内容，尝试获取小时数
            hour_ago = None
            if days_ago == 0 and 'datetime' in emotion:
                # 如果有完整的时间信息
                now = datetime.now()
                if isinstance(emotion['datetime'], datetime):
                    hour_ago = (now - emotion['datetime']).total_seconds() / 3600
            
            time_factor = get_time_weight(days_ago, hour_ago)
            
            # 顺序权重：同一时间内的内容，按顺序给予额外权重
            # 最近的内容有微小的额外权重加成（+5%）
            order_factor = 1.0 + (1.0 / (1 + idx)) * 0.05  # 第一个+5%, 第二个+2.5%, 依此类推
            
            score = emotion['weight'] * time_factor * order_factor
            emotion_scores[emotion['emotion_id']] += score
            
            # 记录详细信息（用于调试）
            emotion['time_weight'] = time_factor
            emotion['order_factor'] = order_factor
            emotion['days_ago'] = days_ago
            emotion['final_score'] = score
        
        # 计算发帖情绪得分（按时间顺序）
        for idx, emotion in enumerate(topic_emotions_sorted):
            days_ago = (today - emotion['date']).days
            
            # 如果是今天的内容，尝试获取小时数
            hour_ago = None
            if days_ago == 0 and 'datetime' in emotion:
                # 如果有完整的时间信息
                now = datetime.now()
                if isinstance(emotion['datetime'], datetime):
                    hour_ago = (now - emotion['datetime']).total_seconds() / 3600
            
            time_factor = get_time_weight(days_ago, hour_ago)
            
            # 顺序权重：最近的发帖有额外权重
            order_factor = 1.0 + (1.0 / (1 + idx)) * 0.05
            
            score = emotion['weight'] * time_factor * order_factor
            emotion_scores[emotion['emotion_id']] += score
            
            # 记录详细信息（用于调试）
            emotion['time_weight'] = time_factor
            emotion['order_factor'] = order_factor
            emotion['days_ago'] = days_ago
            emotion['final_score'] = score
        
        # 计算评论情绪得分（按时间顺序）
        for idx, emotion in enumerate(comment_emotions_sorted):
            days_ago = (today - emotion['date']).days
            
            # 如果是今天的内容，尝试获取小时数
            hour_ago = None
            if days_ago == 0 and 'datetime' in emotion:
                # 如果有完整的时间信息
                now = datetime.now()
                if isinstance(emotion['datetime'], datetime):
                    hour_ago = (now - emotion['datetime']).total_seconds() / 3600
            
            time_factor = get_time_weight(days_ago, hour_ago)
            
            # 顺序权重：最近的评论有额外权重
            order_factor = 1.0 + (1.0 / (1 + idx)) * 0.05
            
            score = emotion['weight'] * time_factor * order_factor
            emotion_scores[emotion['emotion_id']] += score
            
            # 记录详细信息（用于调试）
            emotion['time_weight'] = time_factor
            emotion['order_factor'] = order_factor
            emotion['days_ago'] = days_ago
            emotion['final_score'] = score
        
        # 计算浏览情绪得分（浏览内容也加入时间权重）
        # 浏览内容通常通过收藏时间来确定，如果没有时间信息则使用固定权重
        for emotion in browse_emotions['emotions']:
            # 如果有日期信息，使用时间权重
            if 'date' in emotion:
                days_ago = (today - emotion['date']).days
                time_factor = get_time_weight(days_ago)
                score = emotion['weight'] * time_factor
            else:
                # 没有日期信息，使用默认时间权重（假设是最近3天）
                time_factor = get_time_weight(2)  # 假设是2天前
                score = emotion['weight'] * time_factor
            emotion_scores[emotion['emotion_id']] += score
        
        # 如果没有足够数据，返回默认情绪（平静）
        if not emotion_scores or sum(emotion_scores.values()) < 1.0:
            # 获取"平静"情绪标签
            calm_emotion = EmotionLabel.query.filter_by(
                name='平静', delete_time=None
            ).first()
            if calm_emotion:
                emotion_scores[calm_emotion.id] = 0.5
        
        return dict(emotion_scores)
    
    @classmethod
    def _select_best_emotion(cls, emotion_scores):
        """
        选择得分最高的情绪标签（改进版置信度计算）
        
        改进点：
        1. 考虑得分比例（最高得分/总得分）
        2. 考虑得分差距（第一名与第二名的差距）
        3. 考虑数据量（数据越多，置信度越高）
        4. 考虑数据质量（总得分越高，置信度越高）
        5. 平滑处理（避免极端情况）
        
        规则：
        - 如果置信度 < 0.5，返回"待定"标签
        - 如果置信度 >= 0.5，返回得分最高的情绪标签
        """
        if not emotion_scores:
            # 默认返回"待定"
            pending = EmotionLabel.query.filter_by(name='待定', delete_time=None).first()
            if pending:
                return {
                    'id': pending.id,
                    'name': pending.name,
                    'confidence': 0.3
                }
            # 如果没有"待定"标签，返回"平静"
            calm = EmotionLabel.query.filter_by(name='平静', delete_time=None).first()
            return {
                'id': calm.id if calm else None,
                'name': calm.name if calm else '平静',
                'confidence': 0.3
            }
        
        # 1. 找到得分最高的情绪和得分
        sorted_scores = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        best_emotion_id, best_score = sorted_scores[0]
        
        # 计算总得分
        total_score = sum(emotion_scores.values())
        
        if total_score <= 0:
            # 如果没有有效得分，返回"待定"
            pending = EmotionLabel.query.filter_by(name='待定', delete_time=None).first()
            if pending:
                return {
                    'id': pending.id,
                    'name': pending.name,
                    'confidence': 0.3
                }
        
        # 2. 计算得分比例（基础置信度）
        score_ratio = best_score / max(total_score, 1.0)
        
        # 3. 计算得分差距（第一名与第二名的差距）
        if len(sorted_scores) >= 2:
            second_score = sorted_scores[1][1]
            score_gap = (best_score - second_score) / max(best_score, 1.0)
            # 得分差距越大，置信度越高（0-1之间）
            gap_factor = min(score_gap, 1.0)
        else:
            # 只有一个情绪，得分差距为1.0（完全一致）
            gap_factor = 1.0
        
        # 4. 计算数据量因子（数据越多，置信度越高）
        data_count = len(emotion_scores)
        # 数据量因子：1个数据=0.5, 2个=0.65, 3个=0.75, 4个=0.82, 5个=0.87, >=6个=0.9
        if data_count == 1:
            data_factor = 0.5
        elif data_count == 2:
            data_factor = 0.65
        elif data_count == 3:
            data_factor = 0.75
        elif data_count == 4:
            data_factor = 0.82
        elif data_count == 5:
            data_factor = 0.87
        else:
            data_factor = 0.9  # 6个或更多数据，置信度因子为0.9
        
        # 5. 计算总得分因子（总得分越高，说明数据质量越好）
        # 总得分 < 2: 0.6, 2-5: 0.75, 5-10: 0.85, >=10: 0.95
        if total_score < 2:
            total_score_factor = 0.6
        elif total_score < 5:
            total_score_factor = 0.75
        elif total_score < 10:
            total_score_factor = 0.85
        else:
            total_score_factor = 0.95
        
        # 6. 综合置信度计算（加权平均）
        # 基础权重：
        # - 得分比例：40%（基础）
        # - 得分差距：30%（区分度）
        # - 数据量：15%（可靠性）
        # - 总得分：15%（质量）
        
        confidence = (
            score_ratio * 0.40 +           # 得分比例权重：40%
            gap_factor * 0.30 +             # 得分差距权重：30%
            data_factor * 0.15 +            # 数据量权重：15%
            total_score_factor * 0.15       # 总得分权重：15%
        )
        
        # 7. 平滑处理（避免极端情况）
        # 使用sigmoid函数平滑，避免置信度过低或过高
        # 将置信度映射到sigmoid函数，使得0.5附近的置信度更稳定
        # sigmoid(5*(x-0.5)) * 0.9 + 0.05 将0-1映射到0.05-0.95
        confidence_smooth = 1 / (1 + math.exp(-5 * (confidence - 0.5))) * 0.9 + 0.05
        
        # 8. 如果得分差距足够大，额外提升置信度
        if len(sorted_scores) >= 2:
            second_score = sorted_scores[1][1]
            if best_score > second_score * 2:  # 第一名是第二名的2倍以上
                confidence_smooth = min(confidence_smooth + 0.1, 0.95)
        
        confidence = round(confidence_smooth, 2)
        
        # 9. 如果置信度 < 0.5，返回"待定"标签
        if confidence < 0.5:
            pending = EmotionLabel.query.filter_by(name='待定', delete_time=None).first()
            if pending:
                current_app.logger.info(
                    f"置信度 {confidence} < 0.5，返回待定标签。"
                    f"得分最高的情绪：{best_emotion_id}（得分：{best_score:.2f}，总得分：{total_score:.2f}，"
                    f"得分比例：{score_ratio:.2f}，得分差距：{gap_factor:.2f}，"
                    f"数据量：{data_count}，总得分因子：{total_score_factor:.2f}）"
                )
                return {
                    'id': pending.id,
                    'name': pending.name,
                    'confidence': confidence
                }
        
        # 10. 获取情绪标签信息
        emotion_label = EmotionLabel.get_one(id=best_emotion_id, delete_time=None)
        
        current_app.logger.debug(
            f"情绪分析结果：{emotion_label.name if emotion_label else '未知'}，"
            f"置信度：{confidence:.2f}，得分：{best_score:.2f}，总得分：{total_score:.2f}，"
            f"得分比例：{score_ratio:.2f}，得分差距：{gap_factor:.2f}，"
            f"数据量：{data_count}，总得分因子：{total_score_factor:.2f}"
        )
        
        return {
            'id': best_emotion_id,
            'name': emotion_label.name if emotion_label else '未知',
            'confidence': confidence
        }
    
    @classmethod
    def _generate_analysis(cls, best_emotion, diary_emotions, topic_emotions, comment_emotions, browse_emotions):
        """
        生成分析说明
        """
        analysis_parts = []
        
        # 统计实际的日记、话题和评论数量（去重）
        unique_diary_dates = set(emotion['date'] for emotion in diary_emotions)
        unique_topic_dates = set(emotion['date'] for emotion in topic_emotions)
        unique_comment_dates = set(emotion['date'] for emotion in comment_emotions)
        
        if unique_diary_dates:
            analysis_parts.append(f"根据您近7天写的{len(unique_diary_dates)}篇日记")
        
        if unique_topic_dates:
            analysis_parts.append(f"发布的{len(unique_topic_dates)}条动态")
        
        if unique_comment_dates:
            analysis_parts.append(f"发表的{len(unique_comment_dates)}条评论")
        
        if browse_emotions['total'] > 0:
            analysis_parts.append(f"浏览和收藏的{browse_emotions['total']}条内容")
        
        if analysis_parts:
            if best_emotion['name'] == '待定':
                analysis = f"综合{'、'.join(analysis_parts)}，由于数据不够充分，暂时无法准确判断您的情绪状态"
            else:
                analysis = f"综合{'、'.join(analysis_parts)}，您今日的情绪状态倾向于：{best_emotion['name']}"
                if best_emotion['confidence'] > 0.7:
                    analysis += "（置信度较高）"
                elif best_emotion['confidence'] >= 0.5:
                    analysis += "（置信度中等）"
        else:
            if best_emotion['name'] == '待定':
                analysis = "由于近期活动数据较少，暂时无法准确判断您的情绪状态"
            else:
                analysis = "由于近期活动数据较少，已为您推荐默认情绪标签"
        
        return analysis

