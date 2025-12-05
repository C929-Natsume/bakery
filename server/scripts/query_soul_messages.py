# -*- coding: utf-8 -*-
"""
查询数据库中的心灵鸡汤句子
使用方式：
  python scripts/query_soul_messages.py
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
from app_2.model.soul_push import SoulPush
from app_2.model.user import User


def query_all_custom():
    """查询所有用户自定义句子"""
    print("\n=== 所有用户自定义句子 ===\n")
    
    custom_pushes = db.session.execute(
        db.text("""
            SELECT sp.id, sp.user_id, sp.content, sp.create_time, sp.is_collected, u.nickname
            FROM soul_push sp
            LEFT JOIN user u ON sp.user_id = u.id
            WHERE sp.source_type = 'CUSTOM'
            AND sp.delete_time IS NULL
            ORDER BY sp.create_time DESC
        """)
    ).fetchall()
    
    if not custom_pushes:
        print("暂无自定义句子")
        return
    
    for i, push in enumerate(custom_pushes, 1):
        print(f"{i}. 【{push.nickname or '未知用户'}】")
        print(f"   ID: {push.id}")
        print(f"   内容: {push.content}")
        print(f"   创建时间: {push.create_time}")
        print(f"   已收藏: {'是' if push.is_collected else '否'}")
        print()


def query_public():
    """查询公共句子库（系统用户的句子）"""
    print("\n=== 公共句子库 ===\n")
    
    system_user = User.get_one(openid='system_soul_bot')
    if not system_user:
        print("系统用户不存在，公共句子库为空")
        return
    
    public_pushes = db.session.execute(
        db.text("""
            SELECT id, content, source_type, create_time
            FROM soul_push
            WHERE user_id = :user_id
            AND delete_time IS NULL
            ORDER BY create_time DESC
        """),
        {'user_id': system_user.id}
    ).fetchall()
    
    if not public_pushes:
        print("公共句子库为空")
        return
    
    print(f"共 {len(public_pushes)} 条句子：\n")
    for i, push in enumerate(public_pushes, 1):
        print(f"{i}. {push.content}")
        print(f"   类型: {push.source_type}, 创建时间: {push.create_time}")
        print()


def query_by_user(user_id):
    """查询特定用户的所有句子"""
    print(f"\n=== 用户 {user_id} 的句子 ===\n")
    
    user = User.get_one(id=user_id)
    if not user:
        print(f"用户不存在: {user_id}")
        return
    
    pushes = SoulPush.query.filter_by(
        user_id=user_id,
        delete_time=None
    ).order_by(SoulPush.create_time.desc()).all()
    
    if not pushes:
        print("该用户暂无句子")
        return
    
    custom_count = sum(1 for p in pushes if p.source_type == 'CUSTOM')
    other_count = len(pushes) - custom_count
    
    print(f"用户: {user.nickname}")
    print(f"总句子数: {len(pushes)} (自定义: {custom_count}, 其他: {other_count})\n")
    
    for i, push in enumerate(pushes, 1):
        print(f"{i}. 【{push.source_type}】")
        print(f"   {push.content}")
        print(f"   创建时间: {push.create_time}")
        if push.source_type == 'CUSTOM':
            print(f"   已收藏: {'是' if push.is_collected else '否'}")
        print()


def statistics():
    """统计信息"""
    print("\n=== 统计信息 ===\n")
    
    stats = db.session.execute(
        db.text("""
            SELECT 
                source_type,
                COUNT(*) as count
            FROM soul_push
            WHERE delete_time IS NULL
            GROUP BY source_type
            ORDER BY count DESC
        """)
    ).fetchall()
    
    total = sum(s.count for s in stats)
    print(f"总句子数: {total}\n")
    
    for stat in stats:
        print(f"{stat.source_type}: {stat.count} 条")
    
    # 统计用户自定义句子数
    custom_by_user = db.session.execute(
        db.text("""
            SELECT 
                u.nickname,
                COUNT(sp.id) as count
            FROM soul_push sp
            JOIN user u ON sp.user_id = u.id
            WHERE sp.source_type = 'CUSTOM'
            AND sp.delete_time IS NULL
            GROUP BY sp.user_id, u.nickname
            ORDER BY count DESC
        """)
    ).fetchall()
    
    if custom_by_user:
        print(f"\n用户自定义句子统计：")
        for item in custom_by_user:
            print(f"  {item.nickname}: {item.count} 条")


def query_all():
    """查询所有句子（详细内容）"""
    print("\n=== 所有句子详细内容 ===\n")
    
    # 查询所有未删除的句子，包含情绪标签信息
    all_pushes = db.session.execute(
        db.text("""
            SELECT 
                sp.id,
                sp.content,
                sp.source_type,
                sp.emotion_label_id,
                sp.user_id,
                sp.create_time,
                sp.is_collected,
                sp.llm_model,
                el.name AS emotion_name,
                el.icon AS emotion_icon,
                el.color AS emotion_color,
                u.nickname AS user_nickname
            FROM soul_push sp
            LEFT JOIN emotion_label el ON sp.emotion_label_id = el.id
            LEFT JOIN user u ON sp.user_id = u.id
            WHERE sp.delete_time IS NULL
            ORDER BY sp.create_time DESC
        """)
    ).fetchall()
    
    if not all_pushes:
        print("暂无句子")
        return
    
    print(f"共 {len(all_pushes)} 条句子：\n")
    print("=" * 80)
    
    for i, push in enumerate(all_pushes, 1):
        print(f"\n【句子 {i}/{len(all_pushes)}】")
        print(f"ID: {push.id}")
        print(f"内容: {push.content}")
        print(f"类型: {push.source_type}")
        print(f"用户: {push.user_nickname or '系统'}")
        
        if push.emotion_label_id:
            emotion_info = f"{push.emotion_name} ({push.emotion_icon})"
            if push.emotion_color:
                emotion_info += f" #{push.emotion_color}"
            print(f"情绪标签: {emotion_info}")
        else:
            print(f"情绪标签: 未分类")
        
        print(f"创建时间: {push.create_time}")
        print(f"已收藏: {'是' if push.is_collected else '否'}")
        
        if push.llm_model:
            print(f"LLM模型: {push.llm_model}")
        
        print("-" * 80)
    
    print(f"\n总计: {len(all_pushes)} 条句子")


def query_by_emotion():
    """按情绪标签分组显示句子"""
    print("\n=== 按情绪标签分组显示 ===\n")
    
    # 获取所有情绪标签及其句子
    emotion_pushes = db.session.execute(
        db.text("""
            SELECT 
                el.id AS emotion_id,
                el.name AS emotion_name,
                el.icon AS emotion_icon,
                el.color AS emotion_color,
                sp.id AS push_id,
                sp.content,
                sp.source_type,
                sp.create_time
            FROM emotion_label el
            LEFT JOIN soul_push sp ON el.id = sp.emotion_label_id 
                AND sp.delete_time IS NULL
            WHERE el.delete_time IS NULL
            ORDER BY el.name, sp.create_time DESC
        """)
    ).fetchall()
    
    if not emotion_pushes:
        print("暂无情绪标签")
        return
    
    # 按情绪标签分组
    emotion_groups = {}
    for row in emotion_pushes:
        emotion_key = (row.emotion_id, row.emotion_name, row.emotion_icon, row.emotion_color)
        if emotion_key not in emotion_groups:
            emotion_groups[emotion_key] = []
        
        if row.push_id:  # 有句子
            emotion_groups[emotion_key].append({
                'id': row.push_id,
                'content': row.content,
                'source_type': row.source_type,
                'create_time': row.create_time
            })
    
    # 显示分组结果
    for (emotion_id, emotion_name, emotion_icon, emotion_color), pushes in emotion_groups.items():
        emotion_info = f"{emotion_name} ({emotion_icon})"
        if emotion_color:
            emotion_info += f" #{emotion_color}"
        
        print(f"\n{'='*80}")
        print(f"【{emotion_info}】- {len(pushes)} 条句子")
        print(f"{'='*80}")
        
        if not pushes:
            print("  （暂无句子）")
        else:
            for i, push in enumerate(pushes, 1):
                print(f"\n  {i}. {push['content']}")
                print(f"     类型: {push['source_type']}, 时间: {push['create_time']}")
        
        print()


def main():
    """主函数"""
    app = create_app()
    with app.app_context():
        import sys
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == 'custom':
                query_all_custom()
            elif command == 'public':
                query_public()
            elif command == 'user' and len(sys.argv) > 2:
                query_by_user(sys.argv[2])
            elif command == 'stats':
                statistics()
            elif command == 'all':
                query_all()
            elif command == 'by_emotion' or command == 'emotion':
                query_by_emotion()
            else:
                print("用法:")
                print("  python scripts/query_soul_messages.py all         # 查看所有句子详细内容")
                print("  python scripts/query_soul_messages.py by_emotion  # 按情绪标签分组显示")
                print("  python scripts/query_soul_messages.py custom      # 查看所有自定义句子")
                print("  python scripts/query_soul_messages.py public     # 查看公共句子库")
                print("  python scripts/query_soul_messages.py stats     # 查看统计信息")
                print("  python scripts/query_soul_messages.py user <user_id>  # 查看特定用户的句子")
        else:
            # 默认显示所有句子详细内容
            statistics()
            query_all()


if __name__ == '__main__':
    main()

