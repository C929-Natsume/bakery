# -*- coding: utf-8 -*-
"""
    LLM服务 - 智能推送生成
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
import os
import json
import requests
from flask import current_app


class LLMService:
    """LLM服务类"""
    
    # 提示词模板
    PROMPT_TEMPLATE = """你是一位温暖的心理陪伴者，请根据用户的情绪和内容，生成一句温暖、治愈的话。

用户情绪：{emotion}
用户内容：{content}

要求：
1. 语言温暖、真诚、不说教
2. 50字以内
3. 贴合用户的情绪状态
4. 给予鼓励和支持
5. 可以使用emoji表情

请只返回一句话，不要有其他内容："""

    # 预设温暖句子（降级方案）
    FALLBACK_MESSAGES = {
        '开心': [
            "愿你的笑容永远灿烂如阳光 ☀️",
            "快乐的时光值得被记录，继续保持这份美好吧 ✨",
            "看到你开心，我也跟着开心起来了 😊"
        ],
        '难过': [
            "难过的时候，给自己一个温暖的拥抱 🤗",
            "每一次难过都会过去，而你会变得更强大 💪",
            "允许自己难过，这也是爱自己的一种方式 💙"
        ],
        '焦虑': [
            "深呼吸，一切都会好起来的 🌈",
            "焦虑只是暂时的，你有能力面对一切 🌟",
            "给自己一些时间，慢慢来，不着急 🕊️"
        ],
        '平静': [
            "平静是一种难得的幸福，好好享受这份宁静 🍃",
            "在平静中，我们能听见内心的声音 🎵",
            "平静的心，是最好的礼物 🎁"
        ],
        '疲惫': [
            "累了就休息，你已经很努力了 😴",
            "给自己放个假，好好休息一下吧 🛌",
            "疲惫是身体在提醒你：该好好爱自己了 💕"
        ],
        'default': [
            "无论此刻如何，你都值得被温柔以待 🌸",
            "每一天都是新的开始，加油 💪",
            "你比自己想象的更勇敢、更强大 ⭐"
        ]
    }

    @classmethod
    def generate_soul_message(cls, emotion_name, content, user_context=None):
        """
        生成心灵鸡汤
        
        Args:
            emotion_name: 情绪标签名称
            content: 用户内容（日记或帖子）
            user_context: 用户上下文信息（可选）
        
        Returns:
            dict: {
                'content': '生成的句子',
                'model': '使用的模型',
                'success': True/False
            }
        """
        # 尝试使用LLM生成
        try:
            result = cls._call_llm_api(emotion_name, content)
            if result['success']:
                return result
        except Exception as e:
            current_app.logger.error(f"LLM调用失败: {str(e)}")
        
        # 降级：使用预设句子
        return cls._get_fallback_message(emotion_name)

    @classmethod
    def _call_llm_api(cls, emotion_name, content):
        """
        调用LLM API
        支持多种LLM服务
        """
        llm_type = os.getenv('LLM_TYPE', 'fallback')  # openai, qianwen, wenxin, fallback
        
        if llm_type == 'openai':
            return cls._call_openai(emotion_name, content)
        elif llm_type == 'qianwen':
            return cls._call_qianwen(emotion_name, content)
        elif llm_type == 'wenxin':
            return cls._call_wenxin(emotion_name, content)
        else:
            return {'success': False}

    @classmethod
    def _call_openai(cls, emotion_name, content):
        """调用OpenAI API"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {'success': False}
        
        try:
            prompt = cls.PROMPT_TEMPLATE.format(
                emotion=emotion_name,
                content=content[:200]  # 限制长度
            )
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {'role': 'system', 'content': '你是一位温暖的心理陪伴者。'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 100,
                    'temperature': 0.8
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content'].strip()
                return {
                    'content': message,
                    'model': 'gpt-3.5-turbo',
                    'success': True
                }
        except Exception as e:
            current_app.logger.error(f"OpenAI调用失败: {str(e)}")
        
        return {'success': False}

    @classmethod
    def _call_qianwen(cls, emotion_name, content):
        """调用通义千问API"""
        api_key = os.getenv('QIANWEN_API_KEY')
        if not api_key:
            return {'success': False}
        
        try:
            prompt = cls.PROMPT_TEMPLATE.format(
                emotion=emotion_name,
                content=content[:200]
            )
            
            response = requests.post(
                'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'qwen-turbo',
                    'input': {
                        'messages': [
                            {'role': 'system', 'content': '你是一位温暖的心理陪伴者。'},
                            {'role': 'user', 'content': prompt}
                        ]
                    },
                    'parameters': {
                        'max_tokens': 100
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data['output']['text'].strip()
                return {
                    'content': message,
                    'model': 'qwen-turbo',
                    'success': True
                }
        except Exception as e:
            current_app.logger.error(f"通义千问调用失败: {str(e)}")
        
        return {'success': False}

    @classmethod
    def _call_wenxin(cls, emotion_name, content):
        """调用文心一言API"""
        api_key = os.getenv('WENXIN_API_KEY')
        secret_key = os.getenv('WENXIN_SECRET_KEY')
        if not api_key or not secret_key:
            return {'success': False}
        
        # 文心一言需要先获取access_token
        # 这里简化处理，实际使用时需要实现token管理
        try:
            # 获取access_token
            token_response = requests.post(
                f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}',
                timeout=5
            )
            
            if token_response.status_code == 200:
                access_token = token_response.json()['access_token']
                
                prompt = cls.PROMPT_TEMPLATE.format(
                    emotion=emotion_name,
                    content=content[:200]
                )
                
                response = requests.post(
                    f'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}',
                    json={
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ]
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message = data['result'].strip()
                    return {
                        'content': message,
                        'model': 'wenxin',
                        'success': True
                    }
        except Exception as e:
            current_app.logger.error(f"文心一言调用失败: {str(e)}")
        
        return {'success': False}

    @classmethod
    def _get_fallback_message(cls, emotion_name):
        """获取预设句子（降级方案）"""
        import random
        
        messages = cls.FALLBACK_MESSAGES.get(emotion_name, cls.FALLBACK_MESSAGES['default'])
        message = random.choice(messages)
        
        return {
            'content': message,
            'model': 'fallback',
            'success': True
        }

    @classmethod
    def extract_keywords(cls, text, max_keywords=5):
        """
        提取关键词（简单实现）
        实际项目中可以使用jieba等分词工具
        """
        # 简单的关键词提取
        # 实际使用时建议使用更专业的NLP工具
        import re
        
        # 移除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        
        # 简单分词（按空格和长度）
        words = text.split()
        
        # 过滤短词
        keywords = [w for w in words if len(w) >= 2]
        
        return keywords[:max_keywords]

