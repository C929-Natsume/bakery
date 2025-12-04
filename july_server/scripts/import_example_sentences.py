# -*- coding: utf-8 -*-
"""
从example.txt文件导入心灵鸡汤句子
使用方式：
  方式1（从项目根目录运行）：
    cd D:/SE
    python july_server/scripts/import_example_sentences.py
  
  方式2（从july_server目录运行）：
    cd D:/SE/july_server
    python scripts/import_example_sentences.py
  
  方式3（使用pipenv）：
    cd D:/SE/july_server
    pipenv run python scripts/import_example_sentences.py
"""
import sys
import os
import uuid
import re

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # july_server目录
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app_2 import create_app
from app_2.model.base import db
from app_2.model.soul_push import SoulPush, SoulPushSourceType
from app_2.model.user import User
from app_2.model.emotion_label import EmotionLabel


def parse_example_file(file_path):
    """
    解析example.txt文件
    返回: [(句子内容, [情绪标签列表]), ...]
    """
    sentences = []
    
    if not os.path.exists(file_path):
        print(f"错误：文件不存在: {file_path}")
        return sentences
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            # 匹配格式：句子内容（情绪标签1，情绪标签2，...）
            match = re.match(r'^(.+?)（(.+?)）$', line)
            if match:
                content = match.group(1).strip()
                emotion_tags_str = match.group(2).strip()
                
                # 解析情绪标签
                if emotion_tags_str == '全部':
                    # 使用特殊标记表示所有情绪
                    emotion_tags = ['全部']
                else:
                    # 分割多个标签
                    emotion_tags = [tag.strip() for tag in emotion_tags_str.split('，') if tag.strip()]
                
                if content and emotion_tags:
                    sentences.append((content, emotion_tags))
            else:
                # 如果没有匹配到格式，可能是格式错误，记录警告
                print(f"警告：跳过无法解析的行: {line}")
    
    return sentences


def get_all_system_emotion_labels():
    """
    获取所有系统情绪标签
    返回: {标签名称: EmotionLabel对象}
    """
    labels = EmotionLabel.get_system_labels()
    label_dict = {}
    for label in labels:
        label_dict[label.name] = label
    
    return label_dict


def clear_soul_push_database(system_user_id):
    """
    清空鸡汤句子数据库（仅清空系统用户的句子）
    """
    # 删除系统用户的所有推送记录（软删除）
    deleted_count = db.session.execute(
        db.text("""
            UPDATE soul_push 
            SET delete_time = NOW() 
            WHERE user_id = :user_id 
            AND delete_time IS NULL
        """),
        {'user_id': system_user_id}
    ).rowcount
    
    db.session.commit()
    return deleted_count


def main():
    """主函数"""
    app = create_app()
    with app.app_context():
        # 1. 创建或获取系统用户
        system_user = User.get_one(openid='system_soul_bot')
        if not system_user:
            system_user = User.create(
                id=str(uuid.uuid4()).replace('-', ''),
                openid='system_soul_bot',
                nickname='心灵鸡汤库',
                is_admin=False
            )
            print(f"创建系统用户: {system_user.id}")
        else:
            print(f"找到系统用户: {system_user.id} ({system_user.nickname})")
        
        # 2. 获取所有系统情绪标签
        emotion_labels = get_all_system_emotion_labels()
        print(f"\n找到 {len(emotion_labels)} 个系统情绪标签:")
        for name, label in emotion_labels.items():
            print(f"  - {name} ({label.icon})")
        
        if not emotion_labels:
            print("错误：未找到系统情绪标签，请先导入情绪标签数据！")
            return
        
        # 3. 清空数据库
        print(f"\n开始清空系统用户的鸡汤句子数据库...")
        deleted_count = clear_soul_push_database(system_user.id)
        print(f"已清空 {deleted_count} 条记录")
        
        # 4. 解析example.txt文件
        example_file = os.path.join(project_root, 'docs', 'example.txt')
        print(f"\n开始解析文件: {example_file}")
        sentences = parse_example_file(example_file)
        
        if not sentences:
            print("错误：未从文件中解析到任何句子！")
            return
        
        print(f"解析到 {len(sentences)} 条句子")
        
        # 5. 插入句子
        print(f"\n开始插入句子到数据库...")
        inserted = 0
        skipped = 0
        errors = 0
        
        from datetime import datetime
        
        for content, emotion_tags in sentences:
            # 如果标签是"全部"，为所有10个情绪标签创建记录
            if emotion_tags == ['全部']:
                target_tags = list(emotion_labels.keys())
            else:
                target_tags = emotion_tags
            
            # 为每个情绪标签创建一条记录
            for tag_name in target_tags:
                # 检查标签是否存在
                if tag_name not in emotion_labels:
                    print(f"警告：情绪标签 '{tag_name}' 不存在，跳过")
                    skipped += 1
                    continue
                
                emotion_label = emotion_labels[tag_name]
                
                # 检查是否已存在（相同内容、相同情绪标签，包括已删除的）
                # 注意：清空后理论上不会有重复，但保留检查以防万一
                existing = db.session.execute(
                    db.text("""
                        SELECT id FROM soul_push 
                        WHERE content = :content 
                        AND emotion_label_id = :emotion_label_id
                        AND source_type = 'RANDOM' 
                        AND user_id = :user_id 
                        AND delete_time IS NULL 
                        LIMIT 1
                    """),
                    {
                        'content': content,
                        'emotion_label_id': emotion_label.id,
                        'user_id': system_user.id
                    }
                ).fetchone()
                
                if existing:
                    skipped += 1
                    continue
                
                # 创建新记录
                try:
                    push_id = str(uuid.uuid4()).replace('-', '')
                    db.session.execute(
                        db.text("""
                            INSERT INTO soul_push 
                            (id, user_id, content, source_type, emotion_label_id, llm_model, create_time, delete_time)
                            VALUES 
                            (:id, :user_id, :content, 'RANDOM', :emotion_label_id, 'example_import', :create_time, NULL)
                        """),
                        {
                            'id': push_id,
                            'user_id': system_user.id,
                            'content': content,
                            'emotion_label_id': emotion_label.id,
                            'create_time': datetime.now()
                        }
                    )
                    inserted += 1
                except Exception as e:
                    print(f"插入句子失败: {content[:50]}... (情绪: {tag_name}) 错误: {e}")
                    errors += 1
                    continue
        
        db.session.commit()
        
        # 6. 输出统计信息
        print(f"\n{'='*60}")
        print(f"导入完成！")
        print(f"{'='*60}")
        print(f"成功插入: {inserted} 条记录")
        print(f"跳过重复: {skipped} 条")
        print(f"错误记录: {errors} 条")
        print(f"原始句子: {len(sentences)} 条")
        print(f"实际记录: {inserted} 条")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()

