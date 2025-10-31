# -*- coding: utf-8 -*-
"""
导入心灵鸡汤句子种子数据
使用方式：
  方式1（从项目根目录运行）：
    cd D:\SE
    python july_server/scripts/seed_soul_messages.py
  
  方式2（从july_server目录运行）：
    cd D:\SE\july_server
    python scripts/seed_soul_messages.py
"""
import sys
import os
import uuid

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # july_server目录
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.model.base import db
from app.model.soul_push import SoulPush
from app.model.user import User

# 心灵鸡汤句子库（手动维护，避免版权问题）
SOUL_MESSAGES = [
    "生活就像一杯茶，不会苦一辈子，但总会苦一阵子。",
    "每一个不曾起舞的日子，都是对生命的辜负。",
    "明天会更好，前提是你今天没有放弃。",
    "真正的强者，不是流泪的人，而是含泪奔跑的人。",
    "相信自己，你能作茧自缚，就能破茧成蝶。",
    "没有人能够左右你的情绪，除了你自己。",
    "只有经历过地狱般的折磨，才有征服天堂的力量。",
    "成功不是将来才有的，而是从决定去做的那一刻起，持续累积而成。",
    "生活不是等待暴风雨过去，而是学会在雨中翩翩起舞。",
    "梦想不会逃跑，会逃跑的永远是自己。",
    "你今天的努力，是幸运的伏笔。",
    "不要因为一次失败就放弃，失败是成功之母。",
    "路漫漫其修远兮，吾将上下而求索。",
    "阳光总在风雨后，请相信有彩虹。",
    "给自己一个微笑，告诉自己今天会更美好。",
    "不要害怕你的生活将要结束，应该担心你的生活永远不会真正开始。",
    "人生没有彩排，每天都是现场直播。",
    "愿你在被打击时，记起你的珍贵，抵抗恶意。",
    "成长就是渐渐温柔、克制、朴素、不怨不问不记。",
    "所有的光芒，都需要时间才能被看到。",
    "今天很残酷，明天更残酷，后天很美好。",
    "不要等待机会，而要创造机会。",
    "世上没有绝望的处境，只有对处境绝望的人。",
    "只要路是对的，就不怕路远。",
    "心若向阳，无畏悲伤。",
    "每一天都是一个新的开始，每一刻都是一个新的机会。",
    "生活不会因为你放弃而变得容易，但你可以选择变得更强大。",
    "不管昨天发生了什么，今天都是崭新的一天。",
    "努力不一定成功，但放弃一定失败。",
    "相信自己，你比想象中更强大。",
    "时间是最好的老师，但它会把所有的学生都淘汰。",
    "不要为失败找借口，要为成功找方法。",
    "只有拼出来的美丽，没有等出来的辉煌。",
    "如果你想飞，就要放弃那些会拖累你的东西。",
    "每一个成功者都有一个开始。勇于开始，才能找到成功的路。",
    "山重水复疑无路，柳暗花明又一村。",
    "宝剑锋从磨砺出，梅花香自苦寒来。",
    "天将降大任于斯人也，必先苦其心志，劳其筋骨。",
    "长风破浪会有时，直挂云帆济沧海。",
    "不积跬步，无以至千里；不积小流，无以成江海。",
    "沉舟侧畔千帆过，病树前头万木春。",
    "海阔凭鱼跃，天高任鸟飞。",
    "会当凌绝顶，一览众山小。",
    "天生我材必有用，千金散尽还复来。",
    "有志者事竟成，破釜沉舟，百二秦关终属楚。",
    "苦心人天不负，卧薪尝胆，三千越甲可吞吴。",
    "千淘万漉虽辛苦，吹尽狂沙始到金。",
    "不是一番寒彻骨，怎得梅花扑鼻香。",
    "看似寻常最奇崛，成如容易却艰辛。",
    "山不辞土，故能成其高；海不辞水，故能成其深。",
]


def main():
    """主函数"""
    app = create_app()
    with app.app_context():
        # 创建或获取系统用户
        system_user = User.get_one(openid='system_soul_bot')
        if not system_user:
            system_user = User.create(
                id=str(uuid.uuid4()).replace('-', ''),
                openid='system_soul_bot',
                nickname='心灵鸡汤库',
                is_admin=False
            )
            print(f"创建系统用户: {system_user.id}")
        
        inserted = 0
        skipped = 0
        
        for message in SOUL_MESSAGES:
            # 检查是否已存在（使用原始SQL查询，避免update_time字段问题）
            existing = db.session.execute(
                db.text("""
                    SELECT id FROM soul_push 
                    WHERE content = :content 
                    AND source_type = 'RANDOM' 
                    AND user_id = :user_id 
                    AND delete_time IS NULL 
                    LIMIT 1
                """),
                {'content': message, 'user_id': system_user.id}
            ).fetchone()
            
            if existing:
                skipped += 1
                continue
            
            # 创建新记录（使用原始SQL插入，避免update_time字段问题）
            try:
                from datetime import datetime
                
                push_id = str(uuid.uuid4()).replace('-', '')
                db.session.execute(
                    db.text("""
                        INSERT INTO soul_push 
                        (id, user_id, content, source_type, llm_model, create_time, delete_time)
                        VALUES 
                        (:id, :user_id, :content, 'RANDOM', 'seed', :create_time, NULL)
                    """),
                    {
                        'id': push_id,
                        'user_id': system_user.id,
                        'content': message,
                        'create_time': datetime.now()
                    }
                )
                inserted += 1
            except Exception as e:
                print(f"插入句子失败: {message[:50]}... 错误: {e}")
                continue
        
        db.session.commit()
        
        print(f"\n种子数据导入完成！")
        print(f"成功插入: {inserted} 条")
        print(f"跳过重复: {skipped} 条")
        print(f"总计: {len(SOUL_MESSAGES)} 条")


if __name__ == '__main__':
    main()

