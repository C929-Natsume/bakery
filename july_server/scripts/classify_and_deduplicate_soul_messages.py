# -*- coding: utf-8 -*-
"""
去重并分类心灵鸡汤句子
功能：
1. 删除重复的句子（保留最早的）
2. 根据句子内容自动匹配情绪标签
3. 更新句子的 emotion_label_id 字段

使用方式：
  python scripts/classify_and_deduplicate_soul_messages.py
"""
import sys
import os
import re
from collections import defaultdict

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.model.base import db
from app.model.soul_push import SoulPush
from app.model.emotion_label import EmotionLabel


# 情绪标签关键词匹配规则
EMOTION_KEYWORDS = {
    '8fda3742b16d11f0846e08bfb8c2c035': {  # 开心
        'keywords': ['开心', '快乐', '高兴', '愉快', '欢乐', '喜悦', '笑容', '阳光', '美好', '幸福', '美好', '美好'],
        'positive_words': ['成功', '胜利', '成就', '满足', '祝福']
    },
    '8fda3c1eb16d11f0846e08bfb8c2c035': {  # 平静
        'keywords': ['平静', '安静', '宁静', '淡定', '从容', '沉稳', '平和', '静心', '内心', '淡然'],
        'positive_words': ['时间', '岁月', '人生', '生活', '日常', '平凡']
    },
    '8fda489db16d11f0846e08bfb8c2c035': {  # 难过
        'keywords': ['难过', '悲伤', '伤心', '痛苦', '难过', '失落', '沮丧', '眼泪', '哭泣', '遗憾', '失去'],
        'negative_words': ['放弃', '失败', '挫折', '困难', '苦']
    },
    '8fda4a8eb16d11f0846e08bfb8c2c035': {  # 焦虑
        'keywords': ['焦虑', '担心', '忧虑', '不安', '紧张', '压力', '烦恼', '困扰', '急躁'],
        'negative_words': ['担心', '害怕', '恐惧', '压力']
    },
    '8fda4b9eb16d11f0846e08bfb8c2c035': {  # 愤怒
        'keywords': ['愤怒', '生气', '怒火', '不满', '愤慨', '气愤', '暴躁'],
        'negative_words': ['失败', '挫折', '不公']
    },
    '8fda4cdeb16d11f0846e08bfb8c2c035': {  # 兴奋
        'keywords': ['兴奋', '激动', '激动', '振奋', '热情', '充满', '活力', '激昂', '热血'],
        'positive_words': ['成功', '梦想', '追求', '奋斗', '努力']
    },
    '8fda4dbeb16d11f0846e08bfb8c2c035': {  # 疲惫
        'keywords': ['疲惫', '累', '疲倦', '劳累', '疲惫不堪', '乏力', '困倦', '筋疲力尽'],
        'negative_words': ['累', '辛苦', '疲惫']
    },
    '8fda4e81b16d11f0846e08bfb8c2c035': {  # 感动
        'keywords': ['感动', '感激', '感恩', '温暖', '温暖', '暖心', '触动', '动容', '泪目', '珍贵'],
        'positive_words': ['温暖', '爱', '关怀', '陪伴', '理解']
    },
    '8fda4f60b16d11f0846e08bfb8c2c035': {  # 孤独
        'keywords': ['孤独', '寂寞', '孤单', '独自', '一个人', '孤立', '无人', '独自面对'],
        'negative_words': ['一个人', '独自', '孤单', '寂寞']
    },
    '8fda5031b16d11f0846e08bfb8c2c035': {  # 期待
        'keywords': ['期待', '期望', '盼望', '希望', '等待', '憧憬', '向往', '未来', '明天', '将来'],
        'positive_words': ['希望', '未来', '明天', '梦想', '期待']
    }
}


def match_emotion_label(content):
    """
    根据句子内容匹配情绪标签
    返回情绪标签ID
    """
    content_lower = content.lower()
    
    # 计算每个情绪标签的匹配分数
    scores = {}
    
    for emotion_id, rules in EMOTION_KEYWORDS.items():
        score = 0
        keywords = rules.get('keywords', [])
        positive_words = rules.get('positive_words', [])
        negative_words = rules.get('negative_words', [])
        
        # 关键词匹配
        for keyword in keywords:
            if keyword in content:
                score += 2
        
        # 正面词汇匹配
        for word in positive_words:
            if word in content:
                score += 1
        
        # 负面词汇匹配（如果是负面情绪标签）
        for word in negative_words:
            if word in content:
                score += 1
        
        if score > 0:
            scores[emotion_id] = score
    
    # 返回得分最高的情绪标签
    if scores:
        return max(scores, key=scores.get)
    
    # 如果无法匹配，默认返回"平静"
    return '8fda3c1eb16d11f0846e08bfb8c2c035'


def deduplicate_sentences():
    """
    去重句子：删除重复的句子，保留最早的
    """
    print("开始去重句子...")
    
    # 查询所有未删除的句子
    all_pushes = db.session.execute(
        db.text("""
            SELECT id, content, create_time
            FROM soul_push
            WHERE delete_time IS NULL
            ORDER BY create_time ASC
        """)
    ).fetchall()
    
    # 按内容分组
    content_map = defaultdict(list)
    for push in all_pushes:
        content_map[push.content].append({
            'id': push.id,
            'create_time': push.create_time
        })
    
    # 找出重复的句子
    duplicates_to_delete = []
    kept_count = 0
    
    for content, pushes in content_map.items():
        if len(pushes) > 1:
            # 保留最早的，删除其他的
            pushes_sorted = sorted(pushes, key=lambda x: x['create_time'])
            kept = pushes_sorted[0]
            to_delete = pushes_sorted[1:]
            
            kept_count += 1
            duplicates_to_delete.extend([p['id'] for p in to_delete])
            
            print(f"  发现重复: {content[:30]}... (保留最早的，删除 {len(to_delete)} 条)")
    
    # 软删除重复的句子
    if duplicates_to_delete:
        deleted_count = 0
        for push_id in duplicates_to_delete:
            try:
                db.session.execute(
                    db.text("""
                        UPDATE soul_push 
                        SET delete_time = NOW() 
                        WHERE id = :id AND delete_time IS NULL
                    """),
                    {'id': push_id}
                )
                deleted_count += 1
            except Exception as e:
                print(f"  删除失败 {push_id}: {e}")
        
        db.session.commit()
        print(f"\n去重完成！")
        print(f"  保留: {kept_count} 条（每组重复中最早的）")
        print(f"  删除: {deleted_count} 条重复句子")
    else:
        print("  未发现重复句子")


def classify_sentences():
    """
    为句子分类并添加情绪标签
    """
    print("\n开始为句子分类...")
    
    # 获取所有未删除且没有情绪标签的句子
    pushes = db.session.execute(
        db.text("""
            SELECT id, content, emotion_label_id
            FROM soul_push
            WHERE delete_time IS NULL
            AND (emotion_label_id IS NULL OR emotion_label_id = '')
        """)
    ).fetchall()
    
    if not pushes:
        print("  所有句子已分类")
        return
    
    classified = 0
    emotion_counts = defaultdict(int)
    
    for push in pushes:
        # 匹配情绪标签
        emotion_id = match_emotion_label(push.content)
        
        # 获取情绪标签名称（用于统计）
        emotion = EmotionLabel.get_one(id=emotion_id, delete_time=None)
        emotion_name = emotion.name if emotion else '未知'
        
        # 更新句子
        try:
            db.session.execute(
                db.text("""
                    UPDATE soul_push 
                    SET emotion_label_id = :emotion_id 
                    WHERE id = :id
                """),
                {
                    'id': push.id,
                    'emotion_id': emotion_id
                }
            )
            classified += 1
            emotion_counts[emotion_name] += 1
        except Exception as e:
            print(f"  更新失败 {push.id}: {e}")
    
    db.session.commit()
    
    print(f"\n分类完成！")
    print(f"  分类句子数: {classified} 条")
    print(f"\n  情绪标签分布：")
    for emotion_name, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {emotion_name}: {count} 条")


def reclassify_all():
    """
    重新分类所有句子（强制更新）
    """
    print("\n开始重新分类所有句子...")
    
    # 获取所有未删除的句子
    pushes = db.session.execute(
        db.text("""
            SELECT id, content
            FROM soul_push
            WHERE delete_time IS NULL
        """)
    ).fetchall()
    
    if not pushes:
        print("  没有句子需要分类")
        return
    
    classified = 0
    emotion_counts = defaultdict(int)
    
    for push in pushes:
        # 匹配情绪标签
        emotion_id = match_emotion_label(push.content)
        
        # 获取情绪标签名称（用于统计）
        emotion = EmotionLabel.get_one(id=emotion_id, delete_time=None)
        emotion_name = emotion.name if emotion else '未知'
        
        # 更新句子
        try:
            db.session.execute(
                db.text("""
                    UPDATE soul_push 
                    SET emotion_label_id = :emotion_id 
                    WHERE id = :id
                """),
                {
                    'id': push.id,
                    'emotion_id': emotion_id
                }
            )
            classified += 1
            emotion_counts[emotion_name] += 1
        except Exception as e:
            print(f"  更新失败 {push.id}: {e}")
    
    db.session.commit()
    
    print(f"\n重新分类完成！")
    print(f"  分类句子数: {classified} 条")
    print(f"\n  情绪标签分布：")
    for emotion_name, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {emotion_name}: {count} 条")


def remove_unclassified():
    """
    删除未打标签的句子（软删除）
    """
    print("\n开始删除未分类句子...")
    
    # 查询未分类的句子
    unclassified = db.session.execute(
        db.text("""
            SELECT id, content
            FROM soul_push
            WHERE delete_time IS NULL
            AND (emotion_label_id IS NULL OR emotion_label_id = '')
        """)
    ).fetchall()
    
    if not unclassified:
        print("  没有未分类的句子")
        return
    
    print(f"  发现 {len(unclassified)} 条未分类句子")
    
    # 确认删除
    print(f"\n  准备删除以下未分类句子：")
    for i, push in enumerate(unclassified[:10], 1):  # 只显示前10条
        content = push.content[:50] + '...' if len(push.content) > 50 else push.content
        print(f"    {i}. {content}")
    
    if len(unclassified) > 10:
        print(f"    ... 还有 {len(unclassified) - 10} 条")
    
    # 软删除未分类的句子
    deleted_count = 0
    for push in unclassified:
        try:
            db.session.execute(
                db.text("""
                    UPDATE soul_push 
                    SET delete_time = NOW() 
                    WHERE id = :id AND delete_time IS NULL
                """),
                {'id': push.id}
            )
            deleted_count += 1
        except Exception as e:
            print(f"  删除失败 {push.id}: {e}")
    
    db.session.commit()
    
    print(f"\n删除完成！")
    print(f"  已删除: {deleted_count} 条未分类句子")


def show_statistics():
    """
    显示统计信息
    """
    print("\n=== 数据库统计信息 ===\n")
    
    # 总句子数
    total = db.session.execute(
        db.text("SELECT COUNT(*) as count FROM soul_push WHERE delete_time IS NULL")
    ).fetchone().count
    
    print(f"总句子数: {total}")
    
    # 按类型统计
    type_stats = db.session.execute(
        db.text("""
            SELECT source_type, COUNT(*) as count
            FROM soul_push
            WHERE delete_time IS NULL
            GROUP BY source_type
        """)
    ).fetchall()
    
    print(f"\n按来源类型统计：")
    for stat in type_stats:
        print(f"  {stat.source_type}: {stat.count} 条")
    
    # 按情绪标签统计
    emotion_stats = db.session.execute(
        db.text("""
            SELECT el.name, COUNT(sp.id) as count
            FROM soul_push sp
            LEFT JOIN emotion_label el ON sp.emotion_label_id = el.id
            WHERE sp.delete_time IS NULL
            AND sp.emotion_label_id IS NOT NULL
            GROUP BY sp.emotion_label_id, el.name
            ORDER BY count DESC
        """)
    ).fetchall()
    
    print(f"\n按情绪标签统计：")
    for stat in emotion_stats:
        print(f"  {stat.name}: {stat.count} 条")
    
    # 未分类的句子
    unclassified = db.session.execute(
        db.text("""
            SELECT COUNT(*) as count
            FROM soul_push
            WHERE delete_time IS NULL
            AND (emotion_label_id IS NULL OR emotion_label_id = '')
        """)
    ).fetchone().count
    
    if unclassified > 0:
        print(f"\n未分类句子: {unclassified} 条（将被删除）")
    else:
        print(f"\n未分类句子: 0 条")


def main():
    """主函数"""
    app = create_app()
    with app.app_context():
        import sys
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == 'deduplicate':
                deduplicate_sentences()
            elif command == 'classify':
                classify_sentences()
            elif command == 'reclassify':
                reclassify_all()
            elif command == 'stats':
                show_statistics()
            elif command == 'remove_unclassified':
                remove_unclassified()
                show_statistics()
            elif command == 'all':
                # 执行所有操作
                deduplicate_sentences()
                classify_sentences()
                remove_unclassified()  # 删除未分类的句子
                show_statistics()
            else:
                print("用法:")
                print("  python scripts/classify_and_deduplicate_soul_messages.py deduplicate  # 去重")
                print("  python scripts/classify_and_deduplicate_soul_messages.py classify     # 分类未分类的句子")
                print("  python scripts/classify_and_deduplicate_soul_messages.py reclassify  # 重新分类所有句子")
                print("  python scripts/classify_and_deduplicate_soul_messages.py remove_unclassified  # 删除未分类的句子")
                print("  python scripts/classify_and_deduplicate_soul_messages.py stats      # 显示统计信息")
                print("  python scripts/classify_and_deduplicate_soul_messages.py all         # 执行所有操作（推荐）")
        else:
            # 默认执行所有操作
            deduplicate_sentences()
            classify_sentences()
            remove_unclassified()  # 删除未分类的句子
            show_statistics()


if __name__ == '__main__':
    main()

