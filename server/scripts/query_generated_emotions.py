# -*- coding: utf-8 -*-
"""
查询生成的情绪标签
查看数据库中已生成的情绪标签，包括日记、话题等
"""
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app_2 import create_app
from app_2.model.base import db
from app_2.model.diary import Diary
from app_2.model.topic import Topic
from app_2.model.comment import Comment
from app_2.model.emotion_label import EmotionLabel
from app_2.service.emotion_analysis import EmotionAnalysisService


def query_user_emotions(user_id, days=7):
    """查询用户近N天的情绪标签"""
    print(f"\n=== 用户 {user_id} 近{days}天的情绪标签 ===\n")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # 查询日记
    diaries = db.session.execute(
        db.text("""
            SELECT d.id, d.content, d.diary_date, el.name AS emotion_name, el.icon AS emotion_icon
            FROM diary d
            LEFT JOIN emotion_label el ON d.emotion_label_id = el.id
            WHERE d.user_id = :user_id
            AND d.delete_time IS NULL
            AND d.diary_date >= :start_date
            ORDER BY d.diary_date DESC
        """),
        {'user_id': user_id, 'start_date': start_date}
    ).fetchall()
    
    print(f"📔 日记情绪标签 ({len(diaries)} 条):")
    print("-" * 80)
    
    if not diaries:
        print("  暂无日记")
    else:
        for i, diary in enumerate(diaries, 1):
            emotion_info = f"{diary.emotion_name} {diary.emotion_icon or ''}" if diary.emotion_name else "未分类"
            content_preview = diary.content[:50] + '...' if len(diary.content) > 50 else diary.content
            print(f"  {i}. [{diary.diary_date}] {emotion_info}")
            print(f"     内容: {content_preview}")
            print()
    
    # 查询话题
    topics = db.session.execute(
        db.text("""
            SELECT t.id, t.content, t.create_time, el.name AS emotion_name, el.icon AS emotion_icon
            FROM topic t
            LEFT JOIN emotion_label el ON t.emotion_label_id = el.id
            WHERE t.user_id = :user_id
            AND t.delete_time IS NULL
            AND t.create_time >= :start_datetime
            ORDER BY t.create_time DESC
        """),
        {
            'user_id': user_id, 
            'start_datetime': datetime.combine(start_date, datetime.min.time())
        }
    ).fetchall()
    
    print(f"\n📝 话题情绪标签 ({len(topics)} 条):")
    print("-" * 80)
    
    if not topics:
        print("  暂无话题")
    else:
        for i, topic in enumerate(topics, 1):
            date_str = topic.create_time.date() if topic.create_time else '未知'
            emotion_info = f"{topic.emotion_name} {topic.emotion_icon or ''}" if topic.emotion_name else "未分类"
            content_preview = topic.content[:50] + '...' if len(topic.content) > 50 else topic.content
            print(f"  {i}. [{date_str}] {emotion_info}")
            print(f"     内容: {content_preview}")
            print()
    
    # 查询评论（评论没有情绪标签，需要通过DeepSeek分析）
    comments = db.session.execute(
        db.text("""
            SELECT c.id, c.content, c.create_time
            FROM comment c
            WHERE c.user_id = :user_id
            AND c.delete_time IS NULL
            AND c.create_time >= :start_datetime
            ORDER BY c.create_time DESC
        """),
        {
            'user_id': user_id,
            'start_datetime': datetime.combine(start_date, datetime.min.time())
        }
    ).fetchall()
    
    print(f"\n💬 评论内容 ({len(comments)} 条):")
    print("-" * 80)
    
    if not comments:
        print("  暂无评论")
    else:
        for i, comment in enumerate(comments, 1):
            date_str = comment.create_time.date() if comment.create_time else '未知'
            content_preview = comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
            print(f"  {i}. [{date_str}] {content_preview}")
            print()
    
    # 统计情绪分布
    emotion_stats = defaultdict(int)
    for diary in diaries:
        if diary.emotion_name:
            emotion_stats[diary.emotion_name] += 1
    for topic in topics:
        if topic.emotion_name:
            emotion_stats[topic.emotion_name] += 1
    
    if emotion_stats:
        print(f"\n📊 情绪分布统计:")
        print("-" * 40)
        for emotion, count in sorted(emotion_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {emotion}: {count} 次")
    
    # 调用智能分析查看今日推荐
    print(f"\n🤖 智能分析今日推荐情绪:")
    print("-" * 80)
    try:
        result = EmotionAnalysisService.analyze_user_emotion_today(user_id)
        print(f"  推荐情绪: {result['emotion_name']} (置信度: {result['confidence']:.2%})")
        print(f"  分析说明: {result['analysis']}")
        print(f"  数据来源: 日记 {result['factors']['diary_count']} 条, "
              f"话题 {result['factors']['topic_count']} 条, "
              f"评论 {result['factors'].get('comment_count', 0)} 条, "
              f"浏览 {result['factors']['browse_count']} 条")
        print(f"  分析统计: 标签来源 {result['factors'].get('label_count', 0)} 条, "
              f"DeepSeek分析 {result['factors'].get('deepseek_count', 0)} 条")
        
        # 显示情绪得分详情（包含标签和DeepSeek的权重，以及时间权重）
        if result['factors']['emotion_scores']:
            print(f"\n  情绪得分详情:")
            # 获取所有情绪标签名称
            from app_2.model.emotion_label import EmotionLabel
            emotion_id_to_name = {}
            for emotion_id in result['factors']['emotion_scores'].keys():
                emotion = EmotionLabel.get_one(id=emotion_id, delete_time=None)
                if emotion:
                    emotion_id_to_name[emotion_id] = emotion.name
            
            print(f"    {'情绪':<10} {'得分':<10} {'说明'}")
            print(f"    {'-'*10} {'-'*10} {'-'*30}")
            for emotion_id, score in sorted(result['factors']['emotion_scores'].items(), 
                                           key=lambda x: x[1], reverse=True):
                emotion_name = emotion_id_to_name.get(emotion_id, '未知')
                # 得分越高说明该情绪在近期内容中占比越大（已包含时间权重）
                print(f"    {emotion_name:<10} {score:.2f}    {'（时间越近权重越高）' if score > 0 else ''}")
        
    except Exception as e:
        print(f"  分析失败: {e}")
        import traceback
        traceback.print_exc()


def query_all_emotions(days=7):
    """查询所有用户近N天的情绪标签统计"""
    print(f"\n=== 所有用户近{days}天的情绪标签统计 ===\n")
    
    start_date = datetime.now().date() - timedelta(days=days)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    stats = db.session.execute(
        db.text("""
            SELECT 
                el.id AS emotion_id,
                el.name AS emotion_name,
                el.icon AS emotion_icon,
                COUNT(DISTINCT d.id) AS diary_count,
                COUNT(DISTINCT t.id) AS topic_count
            FROM emotion_label el
            LEFT JOIN diary d ON el.id = d.emotion_label_id 
                AND d.delete_time IS NULL
                AND d.diary_date >= :start_date
            LEFT JOIN topic t ON el.id = t.emotion_label_id 
                AND t.delete_time IS NULL
                AND t.create_time >= :start_datetime
            WHERE el.delete_time IS NULL
            GROUP BY el.id, el.name, el.icon
            HAVING diary_count > 0 OR topic_count > 0
            ORDER BY (diary_count + topic_count) DESC
        """),
        {
            'start_date': start_date,
            'start_datetime': start_datetime
        }
    ).fetchall()
    
    if not stats:
        print("  近{days}天暂无情绪标签数据")
        return
    
    print(f"{'情绪标签':<15} {'图标':<8} {'日记数':<10} {'话题数':<10} {'总计':<10}")
    print("-" * 60)
    
    total_diaries = 0
    total_topics = 0
    
    for stat in stats:
        total = stat.diary_count + stat.topic_count
        icon = stat.emotion_icon or ''
        print(f"{stat.emotion_name:<15} {icon:<8} {stat.diary_count:<10} {stat.topic_count:<10} {total:<10}")
        total_diaries += stat.diary_count
        total_topics += stat.topic_count
    
    print("-" * 60)
    print(f"{'总计':<15} {'':<8} {total_diaries:<10} {total_topics:<10} {total_diaries + total_topics:<10}")


def query_unclassified(days=7):
    """查询未分类的内容"""
    print(f"\n=== 近{days}天未分类的内容 ===\n")
    
    start_date = datetime.now().date() - timedelta(days=days)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    # 查询未分类的日记
    unclassified_diaries = db.session.execute(
        db.text("""
            SELECT d.id, d.content, d.diary_date, u.nickname
            FROM diary d
            LEFT JOIN user u ON d.user_id = u.id
            WHERE d.delete_time IS NULL
            AND d.emotion_label_id IS NULL
            AND d.diary_date >= :start_date
            ORDER BY d.diary_date DESC
            LIMIT 20
        """),
        {'start_date': start_date}
    ).fetchall()
    
    print(f"📔 未分类的日记 ({len(unclassified_diaries)} 条，显示前20条):")
    print("-" * 80)
    
    if unclassified_diaries:
        for i, diary in enumerate(unclassified_diaries, 1):
            content_preview = diary.content[:50] + '...' if len(diary.content) > 50 else diary.content
            print(f"  {i}. [{diary.diary_date}] {diary.nickname or '未知用户'}")
            print(f"     {content_preview}")
            print()
    else:
        print("  暂无未分类的日记")
    
    # 查询未分类的话题
    unclassified_topics = db.session.execute(
        db.text("""
            SELECT t.id, t.content, t.create_time, u.nickname
            FROM topic t
            LEFT JOIN user u ON t.user_id = u.id
            WHERE t.delete_time IS NULL
            AND t.emotion_label_id IS NULL
            AND t.create_time >= :start_datetime
            ORDER BY t.create_time DESC
            LIMIT 20
        """),
        {'start_datetime': start_datetime}
    ).fetchall()
    
    print(f"\n📝 未分类的话题 ({len(unclassified_topics)} 条，显示前20条):")
    print("-" * 80)
    
    if unclassified_topics:
        for i, topic in enumerate(unclassified_topics, 1):
            date_str = topic.create_time.date() if topic.create_time else '未知'
            content_preview = topic.content[:50] + '...' if len(topic.content) > 50 else topic.content
            print(f"  {i}. [{date_str}] {topic.nickname or '未知用户'}")
            print(f"     {content_preview}")
            print()
    else:
        print("  暂无未分类的话题")


def query_emotion_details(emotion_name, days=7):
    """查询特定情绪标签的详细信息"""
    print(f"\n=== 情绪标签「{emotion_name}」的详细信息（近{days}天） ===\n")
    
    emotion = EmotionLabel.query.filter_by(name=emotion_name, delete_time=None).first()
    if not emotion:
        print(f"错误: 未找到情绪标签「{emotion_name}」")
        return
    
    start_date = datetime.now().date() - timedelta(days=days)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    print(f"标签信息: {emotion.name} {emotion.icon or ''} #{emotion.color}")
    print("-" * 80)
    
    # 查询日记
    diaries = db.session.execute(
        db.text("""
            SELECT d.content, d.diary_date, u.nickname
            FROM diary d
            LEFT JOIN user u ON d.user_id = u.id
            WHERE d.emotion_label_id = :emotion_id
            AND d.delete_time IS NULL
            AND d.diary_date >= :start_date
            ORDER BY d.diary_date DESC
            LIMIT 10
        """),
        {'emotion_id': emotion.id, 'start_date': start_date}
    ).fetchall()
    
    print(f"\n📔 相关日记 ({len(diaries)} 条，显示前10条):")
    for i, diary in enumerate(diaries, 1):
        content_preview = diary.content[:60] + '...' if len(diary.content) > 60 else diary.content
        print(f"  {i}. [{diary.diary_date}] {diary.nickname or '未知用户'}")
        print(f"     {content_preview}")
        print()
    
    # 查询话题
    topics = db.session.execute(
        db.text("""
            SELECT t.content, t.create_time, u.nickname
            FROM topic t
            LEFT JOIN user u ON t.user_id = u.id
            WHERE t.emotion_label_id = :emotion_id
            AND t.delete_time IS NULL
            AND t.create_time >= :start_datetime
            ORDER BY t.create_time DESC
            LIMIT 10
        """),
        {'emotion_id': emotion.id, 'start_datetime': start_datetime}
    ).fetchall()
    
    print(f"\n📝 相关话题 ({len(topics)} 条，显示前10条):")
    for i, topic in enumerate(topics, 1):
        date_str = topic.create_time.date() if topic.create_time else '未知'
        content_preview = topic.content[:60] + '...' if len(topic.content) > 60 else topic.content
        print(f"  {i}. [{date_str}] {topic.nickname or '未知用户'}")
        print(f"     {content_preview}")
        print()


def main():
    """主函数"""
    app = create_app()
    with app.app_context():
        import sys
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == 'user' and len(sys.argv) > 2:
                # 查询特定用户的情绪标签
                user_id = sys.argv[2]
                days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
                query_user_emotions(user_id, days)
                
            elif command == 'all':
                # 查询所有用户的情绪标签统计
                days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
                query_all_emotions(days)
                
            elif command == 'unclassified':
                # 查询未分类的内容
                days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
                query_unclassified(days)
                
            elif command == 'emotion' and len(sys.argv) > 2:
                # 查询特定情绪标签的详细信息
                emotion_name = sys.argv[2]
                days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
                query_emotion_details(emotion_name, days)
                
            else:
                print("用法:")
                print("  python scripts/query_generated_emotions.py user <用户ID> [天数]     # 查询特定用户的情绪标签")
                print("  python scripts/query_generated_emotions.py all [天数]              # 查询所有用户的情绪标签统计")
                print("  python scripts/query_generated_emotions.py unclassified [天数]     # 查询未分类的内容")
                print("  python scripts/query_generated_emotions.py emotion <情绪名称> [天数]  # 查询特定情绪标签的详细信息")
                print("\n示例:")
                print("  python scripts/query_generated_emotions.py user d8e5ae1bc666459e856e0e05d6bbdcbf 7")
                print("  python scripts/query_generated_emotions.py all 7")
                print("  python scripts/query_generated_emotions.py unclassified 7")
                print("  python scripts/query_generated_emotions.py emotion 开心 7")
        else:
            # 默认查询所有用户的统计
            query_all_emotions(7)


if __name__ == '__main__':
    main()

