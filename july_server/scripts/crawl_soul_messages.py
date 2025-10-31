# -*- coding: utf-8 -*-
"""
爬取网上心灵鸡汤句子（可选）
注意：请遵守网站robots.txt和版权声明
使用方式：
  方式1（从项目根目录运行）：
    cd D:\SE
    python july_server/scripts/crawl_soul_messages.py
  
  方式2（从july_server目录运行）：
    cd D:\SE\july_server
    python scripts/crawl_soul_messages.py
"""
import sys
import os
import requests
import time
import random
import re
import uuid

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # july_server目录
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bs4 import BeautifulSoup
from app import create_app
from app.model.base import db
from app.model.soul_push import SoulPush
from app.model.user import User

class SoulMessageCrawler:
    """心灵鸡汤爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.sentences = []
    
    def crawl_from_custom_source(self):
        """
        从自定义来源获取（示例：使用静态文本）
        可以替换为实际的心灵鸡汤API
        """
        # 示例：使用静态的心灵鸡汤句子库
        custom_sentences = [
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
        ]
        
        self.sentences.extend(custom_sentences)
    
    def crawl_from_api(self):
        """
        从心灵鸡汤API获取（示例）
        可以使用第三方API如：一言API
        """
        try:
            # 示例API调用（需要替换为实际可用的API）
            # api_url = 'https://api.ixiaowai.cn/ylapi/index.php'
            # for _ in range(50):  # 获取50条
            #     response = requests.get(api_url, timeout=10)
            #     if response.status_code == 200:
            #         data = response.json()
            #         text = data.get('data', {}).get('text', '')
            #         if text and len(text) > 10 and len(text) < 300:
            #             if text not in self.sentences:
            #                 self.sentences.append(text)
            #     time.sleep(0.5)  # 避免请求过快
            print("API爬取功能需要配置实际的API地址")
        except Exception as e:
            print(f"从API获取句子失败: {e}")
    
    def clean_sentences(self):
        """清理和去重句子"""
        # 去重
        self.sentences = list(set(self.sentences))
        
        # 过滤太短或太长的句子
        self.sentences = [
            s.strip() for s in self.sentences 
            if 10 <= len(s.strip()) <= 300 and not re.match(r'^[0-9\s]+$', s.strip())
        ]
        
        print(f"清理后共有 {len(self.sentences)} 条句子")
    
    def get_sentences(self):
        """获取所有句子"""
        return self.sentences


def import_to_database(sentences, system_user_id=None):
    """
    将句子导入数据库
    使用系统用户ID或创建一个公共用户
    """
    app = create_app()
    with app.app_context():
        # 如果没有提供系统用户ID，创建一个公共系统用户
        if not system_user_id:
            system_user = User.get_one(openid='system_soul_bot')
            if not system_user:
                system_user = User.create(
                    id=str(uuid.uuid4()).replace('-', ''),
                    openid='system_soul_bot',
                    nickname='心灵鸡汤库',
                    is_admin=False
                )
            system_user_id = system_user.id
        
        inserted = 0
        skipped = 0
        
        for sentence in sentences:
            # 检查是否已存在（避免重复）
            existing = SoulPush.query.filter_by(
                content=sentence,
                source_type='RANDOM',
                user_id=system_user_id,
                delete_time=None
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # 创建新记录
            try:
                SoulPush.create(
                    user_id=system_user_id,
                    content=sentence,
                    source_type='RANDOM',
                    llm_model='crawled'
                )
                inserted += 1
            except Exception as e:
                print(f"插入句子失败: {sentence[:50]}... 错误: {e}")
                continue
        
        db.session.commit()
        print(f"\n导入完成！")
        print(f"成功插入: {inserted} 条")
        print(f"跳过重复: {skipped} 条")
        print(f"总计: {len(sentences)} 条")


def main():
    """主函数"""
    print("开始爬取心灵鸡汤句子...")
    
    crawler = SoulMessageCrawler()
    
    # 方法1：从自定义源获取（推荐，避免版权问题）
    print("从自定义源获取句子...")
    crawler.crawl_from_custom_source()
    
    # 方法2：从API获取（可选，需要配置）
    # print("从API获取句子...")
    # crawler.crawl_from_api()
    
    # 清理句子
    print("清理句子...")
    crawler.clean_sentences()
    
    # 导入数据库
    print("\n开始导入数据库...")
    sentences = crawler.get_sentences()
    import_to_database(sentences)
    
    print("\n完成！")


if __name__ == '__main__':
    main()

