#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复日记的user_id：将测试用户ID更新为真实微信用户ID
"""
import sys
import os

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app_2 import create_app
from app_2.model.base import db
from app_2.model.diary import Diary
from app_2.model.user import User


def fix_diary_user_ids(from_user_id='test_user_diary_dev', to_user_id=None):
    """
    修复日记的user_id
    
    Args:
        from_user_id: 需要更新的源用户ID（默认：test_user_diary_dev）
        to_user_id: 目标用户ID（如果为None，需要交互式输入）
    """
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("🔧 修复日记的user_id")
        print("=" * 80)
        
        # 查找需要修复的日记
        diaries_to_fix = Diary.query.filter_by(
            user_id=from_user_id,
            delete_time=None
        ).all()
        
        if not diaries_to_fix:
            print(f"✅ 没有找到需要修复的日记（user_id='{from_user_id}'）")
            return
        
        print(f"\n找到 {len(diaries_to_fix)} 条需要修复的日记:\n")
        for idx, diary in enumerate(diaries_to_fix, 1):
            print(f"{idx}. 日期: {diary.diary_date}, 内容: {diary.content[:50]}...")
        
        # 如果没有指定目标用户ID，列出所有用户供选择
        if not to_user_id:
            print("\n📋 可用的微信用户列表:")
            users = User.query.filter_by(delete_time=None).all()
            for idx, user in enumerate(users, 1):
                print(f"  {idx}. ID: {user.id}")
                print(f"     昵称: {user.nickname or '无'}")
                print(f"     OpenID: {user.openid if hasattr(user, 'openid') else 'N/A'}")
            
            print(f"\n❓ 请选择目标用户ID（将把'{from_user_id}'的日记更新为该用户）:")
            print("   输入 'skip' 跳过更新")
            choice = input("   请输入用户ID或序号: ").strip()
            
            if choice.lower() == 'skip':
                print("❌ 已取消更新")
                return
            
            # 尝试作为序号查找
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(users):
                    to_user_id = users[idx].id
                else:
                    print("❌ 序号超出范围")
                    return
            except ValueError:
                # 不是序号，直接作为用户ID
                to_user_id = choice
        
        # 验证目标用户是否存在
        target_user = User.query.filter_by(id=to_user_id, delete_time=None).first()
        if not target_user:
            print(f"❌ 目标用户ID '{to_user_id}' 不存在！")
            return
        
        print(f"\n✅ 目标用户: {target_user.nickname or '无昵称'} (ID: {to_user_id})")
        
        # 确认更新
        print(f"\n⚠️  将要更新 {len(diaries_to_fix)} 条日记的user_id:")
        print(f"   从: {from_user_id}")
        print(f"   到: {to_user_id}")
        confirm = input("\n确认更新？(yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("❌ 已取消更新")
            return
        
        # 执行更新
        try:
            updated_count = 0
            for diary in diaries_to_fix:
                diary.user_id = to_user_id
                updated_count += 1
            
            db.session.commit()
            print(f"\n✅ 更新成功！已更新 {updated_count} 条日记的user_id")
            
            # 验证更新结果
            remaining = Diary.query.filter_by(
                user_id=from_user_id,
                delete_time=None
            ).count()
            print(f"   剩余的 '{from_user_id}' 日记数: {remaining}")
            
            # 显示更新后的日记
            new_diaries = Diary.query.filter_by(
                user_id=to_user_id,
                delete_time=None
            ).order_by(Diary.diary_date.desc()).limit(5).all()
            
            print(f"\n📝 用户 '{target_user.nickname}' 的最新日记（前5条）:")
            for diary in new_diaries:
                print(f"   - {diary.diary_date}: {diary.content[:50]}...")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 更新失败: {str(e)}")
            raise


if __name__ == '__main__':
    if len(sys.argv) > 1:
        to_user_id = sys.argv[1]
        fix_diary_user_ids(to_user_id=to_user_id)
    else:
        fix_diary_user_ids()

