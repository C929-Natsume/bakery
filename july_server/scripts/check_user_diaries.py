#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断脚本：检查用户日记数据
用于排查为什么查不到用户日记的问题
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app_2 import create_app
from app_2.model.base import db
from app_2.model.diary import Diary
from app_2.model.user import User

def check_user_diaries(user_id=None):
    """检查用户日记数据"""
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("用户日记诊断工具")
        print("=" * 60)
        
        # 如果没有指定用户ID，列出所有用户
        if not user_id:
            print("\n📋 所有用户列表:")
            users = User.query.filter_by(delete_time=None).limit(10).all()
            for idx, user in enumerate(users, 1):
                diary_count = Diary.query.filter_by(
                    user_id=user.id,
                    delete_time=None
                ).count()
                print(f"  {idx}. 用户ID: {user.id}")
                print(f"     昵称: {user.nickname or '无'}")
                print(f"     日记数: {diary_count}")
            print("\n请指定用户ID进行详细检查:")
            print("  python scripts/check_user_diaries.py <user_id>")
            return
        
        print(f"\n🔍 检查用户ID: {user_id}")
        
        # 检查用户是否存在
        user = User.query.filter_by(id=user_id, delete_time=None).first()
        if not user:
            print(f"❌ 错误：用户 {user_id} 不存在或已被删除")
            return
        
        print(f"✅ 用户存在: {user.nickname or '无昵称'}")
        print(f"   用户ID: {user.id}")
        print(f"   OpenID: {user.openid if hasattr(user, 'openid') else 'N/A'}")
        
        # 检查所有日记（不限时间）
        all_diaries = Diary.query.filter_by(
            user_id=user_id,
            delete_time=None
        ).order_by(Diary.diary_date.desc()).all()
        
        print(f"\n📝 日记总数（不限时间）: {len(all_diaries)}")
        
        # 如果查不到日记，检查是否有其他用户ID的日记
        if len(all_diaries) == 0:
            print("\n⚠️  该用户没有任何日记！")
            print("\n🔍 检查数据库中是否有日记（可能是用户ID不匹配）:")
            all_diaries_sample = Diary.query.filter_by(
                delete_time=None
            ).limit(20).all()
            
            if all_diaries_sample:
                print(f"   数据库中共有日记（样本前20条）: {len(all_diaries_sample)}")
                # 统计不同用户ID
                user_id_counts = {}
                for diary in all_diaries_sample:
                    uid = diary.user_id
                    user_id_counts[uid] = user_id_counts.get(uid, 0) + 1
                
                print(f"\n   日记中的用户ID分布:")
                for uid, count in sorted(user_id_counts.items(), key=lambda x: x[1], reverse=True):
                    match = "✅" if uid == user_id else "❌"
                    user_info = User.query.filter_by(id=uid, delete_time=None).first()
                    nickname = user_info.nickname if user_info else "未知用户"
                    print(f"     {match} {uid}: {count}条日记 (昵称: {nickname})")
                
                if user_id not in user_id_counts:
                    print(f"\n   ⚠️  查询的用户ID '{user_id}' 不在日记记录中！")
                    print(f"   这可能表明用户ID不匹配问题。")
                    return
        
        # 显示最近的日记
        print("\n📅 最近的10条日记:")
        for idx, diary in enumerate(all_diaries[:10], 1):
            print(f"  {idx}. 日期: {diary.diary_date}")
            print(f"     内容: {diary.content[:50]}{'...' if len(diary.content) > 50 else ''}")
            print(f"     情绪标签: {diary.emotion_label.name if diary.emotion_label_id and diary.emotion_label else '无'}")
            print(f"     创建时间: {diary.create_time}")
            print()
        
        # 检查近7天的日记
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        print(f"\n📊 近7天日记统计（{start_date} 至 {end_date}）:")
        recent_diaries = Diary.query.filter(
            Diary.user_id == user_id,
            Diary.diary_date >= start_date,
            Diary.diary_date <= end_date,
            Diary.delete_time == None
        ).order_by(Diary.diary_date.desc()).all()
        
        print(f"  查询到的日记数: {len(recent_diaries)}")
        
        if len(recent_diaries) == 0:
            print("  ⚠️  近7天内没有日记")
            if len(all_diaries) > 0:
                latest_diary = all_diaries[0]
                days_diff = (end_date - latest_diary.diary_date).days
                print(f"  ℹ️  最近的日记是 {days_diff} 天前的（{latest_diary.diary_date}）")
        else:
            print("  ✅ 近7天有日记:")
            for diary in recent_diaries:
                print(f"    - {diary.diary_date}: {diary.content[:30]}...")
        
        # 按日期统计
        print("\n📈 日记日期分布:")
        date_counts = {}
        for diary in all_diaries:
            date_str = str(diary.diary_date)
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        # 显示日期分布（最近20个日期）
        sorted_dates = sorted(date_counts.keys(), reverse=True)[:20]
        for date_str in sorted_dates:
            count = date_counts[date_str]
            days_ago = (end_date - datetime.strptime(date_str, '%Y-%m-%d').date()).days
            print(f"  {date_str}: {count}条 (距今{days_ago}天)")

if __name__ == '__main__':
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    check_user_diaries(user_id)

