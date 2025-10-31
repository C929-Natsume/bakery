#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看日记脚本
提供多种查看日记的方式
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.model.base import db
from app.model.diary import Diary
from app.model.user import User
from app.model.emotion_label import EmotionLabel


def view_all_diaries(limit=20):
    """查看所有日记"""
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("📝 所有日记列表")
        print("=" * 80)
        
        diaries = Diary.query.filter_by(
            delete_time=None
        ).order_by(Diary.diary_date.desc()).limit(limit).all()
        
        if not diaries:
            print("❌ 没有找到任何日记")
            return
        
        print(f"\n共找到 {len(diaries)} 条日记（显示最近 {limit} 条）:\n")
        
        for idx, diary in enumerate(diaries, 1):
            user = User.query.filter_by(id=diary.user_id).first()
            emotion = diary.emotion_label
            
            print(f"{idx}. 日期: {diary.diary_date}")
            print(f"   用户: {user.nickname if user else diary.user_id}")
            print(f"   用户ID: {diary.user_id}")
            print(f"   内容: {diary.content[:100]}{'...' if len(diary.content) > 100 else ''}")
            print(f"   情绪: {emotion.name if emotion else '无'}")
            print(f"   公开: {'是' if diary.is_public else '否'}")
            print(f"   创建时间: {diary.create_time}")
            print()


def view_user_diaries(user_id, limit=50):
    """查看指定用户的日记"""
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print(f"📝 用户 {user_id} 的日记")
        print("=" * 80)
        
        user = User.query.filter_by(id=user_id, delete_time=None).first()
        if not user:
            print(f"❌ 用户 {user_id} 不存在")
            return
        
        print(f"用户昵称: {user.nickname or '无'}")
        print(f"用户ID: {user.id}\n")
        
        diaries = Diary.query.filter_by(
            user_id=user_id,
            delete_time=None
        ).order_by(Diary.diary_date.desc()).limit(limit).all()
        
        if not diaries:
            print("❌ 该用户没有日记")
            return
        
        print(f"共找到 {len(diaries)} 条日记:\n")
        
        for idx, diary in enumerate(diaries, 1):
            emotion = diary.emotion_label
            print(f"{idx}. 日期: {diary.diary_date}")
            print(f"   内容: {diary.content}")
            print(f"   情绪: {emotion.name if emotion else '无'}")
            print(f"   公开: {'是' if diary.is_public else '否'}")
            if diary.weather:
                print(f"   天气: {diary.weather}")
            if diary.location:
                print(f"   地点: {diary.location}")
            print(f"   创建时间: {diary.create_time}")
            print()


def view_recent_diaries(days=7, limit=50):
    """查看最近N天的日记"""
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print(f"📝 最近 {days} 天的日记")
        print("=" * 80)
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        print(f"时间范围: {start_date} 至 {end_date}\n")
        
        diaries = Diary.query.filter(
            Diary.diary_date >= start_date,
            Diary.diary_date <= end_date,
            Diary.delete_time == None
        ).order_by(Diary.diary_date.desc()).limit(limit).all()
        
        if not diaries:
            print(f"❌ 最近 {days} 天内没有日记")
            return
        
        print(f"共找到 {len(diaries)} 条日记:\n")
        
        # 按日期分组
        by_date = {}
        for diary in diaries:
            date_str = str(diary.diary_date)
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(diary)
        
        for date_str in sorted(by_date.keys(), reverse=True):
            date_diaries = by_date[date_str]
            print(f"\n📅 {date_str} ({len(date_diaries)} 条):")
            for diary in date_diaries:
                user = User.query.filter_by(id=diary.user_id).first()
                emotion = diary.emotion_label
                print(f"   - [{user.nickname if user else diary.user_id}] "
                      f"{diary.content[:60]}{'...' if len(diary.content) > 60 else ''}")
                if emotion:
                    print(f"     情绪: {emotion.name}")


def view_by_date(date_str):
    """查看指定日期的日记"""
    app = create_app()
    with app.app_context():
        try:
            diary_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ 日期格式错误，应为 YYYY-MM-DD，例如: 2025-10-31")
            return
        
        print("=" * 80)
        print(f"📝 {date_str} 的日记")
        print("=" * 80)
        
        diaries = Diary.query.filter_by(
            diary_date=diary_date,
            delete_time=None
        ).order_by(Diary.create_time.desc()).all()
        
        if not diaries:
            print(f"❌ {date_str} 没有日记")
            return
        
        print(f"共找到 {len(diaries)} 条日记:\n")
        
        for idx, diary in enumerate(diaries, 1):
            user = User.query.filter_by(id=diary.user_id).first()
            emotion = diary.emotion_label
            
            print(f"{idx}. 用户: {user.nickname if user else diary.user_id}")
            print(f"   内容: {diary.content}")
            print(f"   情绪: {emotion.name if emotion else '无'}")
            print(f"   公开: {'是' if diary.is_public else '否'}")
            if diary.weather:
                print(f"   天气: {diary.weather}")
            if diary.location:
                print(f"   地点: {diary.location}")
            print(f"   创建时间: {diary.create_time}")
            print()


def view_statistics():
    """查看日记统计信息"""
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("📊 日记统计信息")
        print("=" * 80)
        
        # 总日记数
        total = Diary.query.filter_by(delete_time=None).count()
        print(f"总日记数: {total}")
        
        # 总用户数（有日记的用户）
        users_with_diaries = db.session.query(Diary.user_id).filter_by(
            delete_time=None
        ).distinct().count()
        print(f"有日记的用户数: {users_with_diaries}")
        
        # 最近7天的日记数
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        recent = Diary.query.filter(
            Diary.diary_date >= start_date,
            Diary.diary_date <= end_date,
            Diary.delete_time == None
        ).count()
        print(f"最近7天日记数: {recent}")
        
        # 按用户统计
        print("\n📈 用户日记排行（前10名）:")
        user_stats = db.session.query(
            Diary.user_id,
            db.func.count(Diary.id).label('count')
        ).filter_by(
            delete_time=None
        ).group_by(Diary.user_id).order_by(
            db.func.count(Diary.id).desc()
        ).limit(10).all()
        
        for idx, (user_id, count) in enumerate(user_stats, 1):
            user = User.query.filter_by(id=user_id).first()
            print(f"  {idx}. {user.nickname if user else user_id}: {count} 条")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/view_diaries.py all [限制数量]     # 查看所有日记")
        print("  python scripts/view_diaries.py user <user_id>     # 查看指定用户的日记")
        print("  python scripts/view_diaries.py recent [天数]     # 查看最近N天的日记")
        print("  python scripts/view_diaries.py date <YYYY-MM-DD> # 查看指定日期的日记")
        print("  python scripts/view_diaries.py stats              # 查看统计信息")
        print("\n示例:")
        print("  python scripts/view_diaries.py all 20")
        print("  python scripts/view_diaries.py user 1a32903d304142129a30a06970dfe43d")
        print("  python scripts/view_diaries.py recent 7")
        print("  python scripts/view_diaries.py date 2025-10-31")
        print("  python scripts/view_diaries.py stats")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'all':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        view_all_diaries(limit)
    
    elif command == 'user':
        if len(sys.argv) < 3:
            print("❌ 请提供用户ID")
            sys.exit(1)
        user_id = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        view_user_diaries(user_id, limit)
    
    elif command == 'recent':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        view_recent_diaries(days)
    
    elif command == 'date':
        if len(sys.argv) < 3:
            print("❌ 请提供日期 (YYYY-MM-DD)")
            sys.exit(1)
        date_str = sys.argv[2]
        view_by_date(date_str)
    
    elif command == 'stats':
        view_statistics()
    
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)

