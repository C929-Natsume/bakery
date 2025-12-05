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
from .sentiment_lexicon import SentimentLexicon


class LLMService:
    """LLM服务类"""
    
    # 情绪任务模板（参考cntext的设计）
    EMOTION_TASK_TEMPLATES = {
        'emotion_simple': {
            'prompt': '分析文本的情绪状态，返回情绪标签名称（如：开心、难过、焦虑等）。',
            'output_format': {'label': str}
        },
        'emotion_enhanced': {
            'prompt': '分析文本的情绪状态，返回情绪标签、分值、置信度和强度。',
            'output_format': {
                'label': str,
                'score': float,      # -1.0 ~ 1.0，负数为负面，正数为正面
                'confidence': float, # 0.0 ~ 1.0，置信度
                'intensity': float   # 0.0 ~ 1.0，强度
            }
        },
        'emotion_multi_dimension': {
            'prompt': '从多个维度分析文本情绪：主要情绪、次要情绪、情绪倾向、强度、置信度。',
            'output_format': {
                'primary_emotion': str,
                'secondary_emotion': str,
                'valence': str,      # 'positive'/'negative'/'neutral'
                'intensity': float,
                'confidence': float
            }
        }
    }
    
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
        llm_type = os.getenv('LLM_TYPE', 'fallback')  # openai, qianwen, wenxin, deepseek, fallback
        
        if llm_type == 'openai':
            return cls._call_openai(emotion_name, content)
        elif llm_type == 'qianwen':
            return cls._call_qianwen(emotion_name, content)
        elif llm_type == 'wenxin':
            return cls._call_wenxin(emotion_name, content)
        elif llm_type == 'deepseek':
            return cls._call_deepseek(emotion_name, content)
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
    def _call_deepseek(cls, emotion_name, content):
        """调用DeepSeek V3 API"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            return {'success': False}
        
        try:
            prompt = cls.PROMPT_TEMPLATE.format(
                emotion=emotion_name,
                content=content[:200]
            )
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': '你是一位温暖的心理陪伴者。'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 100,
                    'temperature': 0.8
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']['content'].strip()
                return {
                    'content': message,
                    'model': 'deepseek-chat',
                    'success': True
                }
        except Exception as e:
            current_app.logger.error(f"DeepSeek调用失败: {str(e)}")
        
        return {'success': False}

    @classmethod
    def analyze_emotion_from_text(cls, text):
        """
        使用DeepSeek V3分析文本情绪（结合专业sentiment词典优化版）
        返回情绪标签名称
        
        Args:
            text: 待分析的文本内容
            
        Returns:
            str: 情绪标签名称，如 '开心', '难过', '平静' 等
        """
        if not text or len(text.strip()) < 3:
            return None
        
        # 第一步：使用专业sentiment词典进行快速预判断
        try:
            lexicon_result = SentimentLexicon.analyze_with_lexicon(text)
            # 如果专业词典置信度很高（>=0.8），直接返回
            if lexicon_result and lexicon_result.get('confidence', 0) >= 0.8:
                top_emotion = max(
                    lexicon_result['emotion_scores'], 
                    key=lexicon_result['emotion_scores'].get
                ) if lexicon_result['emotion_scores'] else None
                
                if top_emotion:
                    current_app.logger.debug(
                        f"专业词典快速识别: {top_emotion}, "
                        f"置信度: {lexicon_result['confidence']:.2f}"
                    )
                    return top_emotion
        except Exception as e:
            current_app.logger.warning(f"专业词典预判断失败: {str(e)}")
        
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            # 如果没有配置API Key，使用专业词典或关键词匹配
            if lexicon_result and lexicon_result['emotion_scores']:
                top_emotion = max(
                    lexicon_result['emotion_scores'], 
                    key=lexicon_result['emotion_scores'].get
                )
                return top_emotion
            return cls._match_emotion_by_keywords(text)
        
        try:
            # 获取系统情绪标签列表
            from app_2.model.emotion_label import EmotionLabel
            system_labels = EmotionLabel.get_system_labels()
            emotion_names = [label.name for label in system_labels]
            emotion_list = '、'.join(emotion_names)
            
            # 检测特殊情况
            has_turnaround = cls._detect_turnaround_keywords(text)
            has_mixed_emotion = cls._detect_mixed_emotion_keywords(text)
            modal_info = cls._detect_modal_particles(text)
            
            # 将专业词典分析结果融入提示词
            lexicon_context = ""
            if lexicon_result and lexicon_result['emotion_scores']:
                sorted_emotions = sorted(
                    lexicon_result['emotion_scores'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                if sorted_emotions:
                    emotion_str = '、'.join([f"{name}" for name, _ in sorted_emotions])
                    lexicon_context = f"💡 专业词典分析提示：候选情绪可能是 {emotion_str}（按匹配强度排序），但需结合文本上下文综合分析。"
            
            # 构建优化的提示词
            prompt = cls._build_emotion_analysis_prompt(
                text, emotion_list, emotion_names, 
                has_turnaround, has_mixed_emotion, modal_info,
                lexicon_context=lexicon_context
            )
            
            # 记录检测结果
            if has_turnaround:
                current_app.logger.debug(
                    f"检测到转折句式: {text[:50]}..., "
                    f"将使用转折句式处理提示"
                )
            if has_mixed_emotion:
                current_app.logger.debug(
                    f"检测到混合情绪: {text[:50]}..., "
                    f"将识别为'待定'"
                )
            if modal_info['has_particles']:
                current_app.logger.debug(
                    f"检测到语气词: {text[:50]}..., "
                    f"语气词: {modal_info['particles']}, "
                    f"强度词: {modal_info['intensity_words']}"
                )
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': cls._build_system_message()},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 20,  # 增加token数，允许更详细的输出
                    'temperature': 0.1,  # 进一步降低温度以提高准确性和一致性
                    'top_p': 0.9,  # 使用top_p采样，提高确定性
                    'frequency_penalty': 0.3,  # 减少重复
                    'presence_penalty': 0.0  # 鼓励多样化输出
                },
                timeout=20  # 增加超时时间
            )
            
            if response.status_code == 200:
                data = response.json()
                emotion_result = data['choices'][0]['message']['content'].strip()
                
                # 使用改进的解析方法
                emotion_name = cls._parse_emotion_result(emotion_result, emotion_names)
                
                if emotion_name:
                    # 如果专业词典也有结果，验证一致性
                    if lexicon_result and lexicon_result['emotion_scores']:
                        lexicon_top = max(
                            lexicon_result['emotion_scores'], 
                            key=lexicon_result['emotion_scores'].get
                        )
                        if lexicon_top == emotion_name:
                            current_app.logger.debug(
                                f"DeepSeek和专业词典结果一致: {emotion_name}, "
                                f"文本={text[:50]}..."
                            )
                        else:
                            current_app.logger.debug(
                                f"DeepSeek: {emotion_name}, 词典: {lexicon_top}, "
                                f"使用DeepSeek结果"
                            )
                    
                    current_app.logger.debug(
                        f"DeepSeek情绪分析成功: 文本={text[:50]}..., "
                        f"结果={emotion_result}, "
                        f"匹配={emotion_name}"
                    )
                    return emotion_name
                else:
                    current_app.logger.warning(
                        f"DeepSeek情绪分析结果无法匹配: 文本={text[:50]}..., "
                        f"结果={emotion_result}"
                    )
                    # 降级方案：优先使用专业词典，再使用关键词匹配
                    if lexicon_result and lexicon_result['emotion_scores']:
                        top_emotion = max(
                            lexicon_result['emotion_scores'], 
                            key=lexicon_result['emotion_scores'].get
                        )
                        current_app.logger.debug(f"降级到专业词典: {top_emotion}")
                        return top_emotion
                    # 最后降级到关键词匹配
                    return cls._match_emotion_by_keywords(text)
            else:
                current_app.logger.error(
                    f"DeepSeek API调用失败: status={response.status_code}, "
                    f"response={response.text[:200]}"
                )
                # 降级方案：优先使用专业词典
                if lexicon_result and lexicon_result['emotion_scores']:
                    top_emotion = max(
                        lexicon_result['emotion_scores'], 
                        key=lexicon_result['emotion_scores'].get
                    )
                    return top_emotion
                return cls._match_emotion_by_keywords(text)
            
        except requests.Timeout:
            current_app.logger.error(f"DeepSeek情绪分析超时: {text[:50]}...")
            # 超时降级：优先使用专业词典
            if lexicon_result and lexicon_result['emotion_scores']:
                top_emotion = max(
                    lexicon_result['emotion_scores'], 
                    key=lexicon_result['emotion_scores'].get
                )
                return top_emotion
            return cls._match_emotion_by_keywords(text)
        except Exception as e:
            current_app.logger.error(f"DeepSeek情绪分析失败: {str(e)}")
            # 异常降级：优先使用专业词典
            if lexicon_result and lexicon_result['emotion_scores']:
                top_emotion = max(
                    lexicon_result['emotion_scores'], 
                    key=lexicon_result['emotion_scores'].get
                )
                return top_emotion
            return cls._match_emotion_by_keywords(text)
        
        return None
    
    @classmethod
    def _build_system_message(cls):
        """构建系统消息，提供更专业的角色定义"""
        return """你是一个专业的情绪分析专家，擅长从中文文本中准确识别作者的情绪状态。

你的任务：
1. 仔细分析文本的语言风格、用词、语气
2. 识别作者的真实情绪状态
3. 从给定的情绪标签中选择最匹配的一个
4. 只返回情绪标签名称，不要有其他解释

情绪标签定义：
- 开心：喜悦、愉快、兴奋、满足
- 难过：悲伤、失落、沮丧、痛苦
- 焦虑：担心、不安、紧张、压力
- 愤怒：生气、不满、暴躁、恼火
- 平静：宁静、淡定、从容、平和
- 疲惫：累、疲倦、劳累、乏力
- 感动：感激、温暖、触动、动容
- 兴奋：激动、振奋、热情、充满活力
- 期待：期望、盼望、希望、等待
- 孤独：寂寞、孤单、独自、孤立

分析原则：
- 优先考虑文本的主要情绪
- 注意语境和隐含的情绪
- **注意语气词（啊、呀、呢、吧等）和强度词（真的、太、特别等），它们可以帮助判断情绪强度**
- **特别注意转折句式（如"虽然...但是..."、"虽然...还是..."）：转折后的内容表达真实情绪**
- 如果文本情绪不明显或混合，选择最接近的标签

语气词分析：
- 语气词（啊、呀、呢、吧、吗、哦等）可以表达情绪的语气和强度
- 强度词（真的、太、好、特别、非常等）表示情绪的强烈程度
- 结合语气词和强度词可以更准确地判断情绪类型和强度

转折句式处理：
- "虽然X（负面），但是Y（正面情绪）" → 识别为正面情绪（转折后的情绪）
- "虽然X（负面），但是Y（正面行为）" → 识别为负面情绪（转折前的情绪）
- "虽然表面平静，但内心还是有点不安" → 识别为"焦虑"（转折后的真实情绪）

混合情绪处理：
- "又...又..."、"既...又..." → 识别为"待定"（混合情绪）
- "不知道是什么感觉"、"心情很复杂" → 识别为"待定"（不确定状态）"""
    
    @classmethod
    def _build_emotion_analysis_prompt(cls, text, emotion_list, emotion_names, 
                                       has_turnaround=False, has_mixed_emotion=False, 
                                       modal_info=None, lexicon_context=""):
        """
        构建优化的情绪分析提示词
        
        Args:
            text: 文本内容
            emotion_list: 情绪标签列表（字符串）
            emotion_names: 情绪标签名称列表
            has_turnaround: 是否检测到转折句式
            has_mixed_emotion: 是否检测到混合情绪
            modal_info: 语气词信息
            lexicon_context: 专业词典分析上下文（可选）
        """
        if modal_info is None:
            modal_info = {'has_particles': False, 'particles': [], 'intensity_words': []}
        
        # 清理文本，移除多余空格和换行
        text_clean = ' '.join(text.split())
        
        # 限制文本长度，但保留更多上下文
        text_truncated = text_clean[:800] if len(text_clean) > 800 else text_clean
        
        # 优先处理混合情绪
        if has_mixed_emotion:
            mixed_emotion_instruction = """

⚠️ 重要提示：检测到混合情绪表达（如"又...又..."、"既...又..."、"不知道是什么感觉"等）。
请特别注意：当文本明确表达出多种矛盾情绪或不确定的感觉时，应该识别为"待定"。
例如：
- "又开心又难过，不知道是什么感觉" → 应该识别为"待定"（混合情绪，不确定）
- "今天发生了很多事情，心情很复杂" → 应该识别为"待定"（复杂情绪）
- "既兴奋又紧张，说不清是什么感觉" → 应该识别为"待定"（混合情绪）

请直接返回"待定"。

"""
            return f"""请分析以下文本内容，判断作者的情绪状态。

可选的情绪标签：{emotion_list}{mixed_emotion_instruction}
文本内容：{text_truncated}

请直接返回情绪标签名称（如果是混合情绪，请返回"待定"）："""
        
        # 添加few-shot示例（如果文本很短，提供更具体的指导）
        few_shot_examples = ""
        if len(text_clean) < 50:
            few_shot_examples = """

示例：
文本："今天天气真好，心情也不错！"
情绪：开心

文本："最近工作压力很大，总是睡不好"
情绪：焦虑

文本："一个人在家，感觉有点孤单"
情绪：孤独

文本："感谢朋友的帮助，真的很感动"
情绪：感动

"""
        
        # 语气词分析提示
        modal_instruction = ""
        if modal_info['has_particles']:
            particles_str = '、'.join(set(modal_info['particles'])) if modal_info['particles'] else ''
            intensity_str = '、'.join(set(modal_info['intensity_words'])) if modal_info['intensity_words'] else ''
            
            modal_instruction = """

💡 语气词提示：检测到语气词和强度词，这些可以帮助判断情绪强度。
"""
            if particles_str:
                modal_instruction += f"\n检测到的语气词：{particles_str}\n"
            if intensity_str:
                modal_instruction += f"\n检测到的强度词：{intensity_str}\n"
            
            modal_instruction += """
语气词的作用：
- "啊"、"呀"、"呢"、"吧"等语气词可以表达不同的情绪语气和强度
- "真的"、"太"、"特别"、"非常"等强度词表示情绪的强烈程度

例如：
- "今天真的太好啦！" → 语气词"啦"和强度词"真的"、"太"表示强烈的开心
- "我好难过啊..." → 语气词"啊"和强度词"好"表示较强的难过
- "太焦虑了..." → 强度词"太"表示很强的焦虑
- "特别感动呢！" → 强度词"特别"和语气词"呢"表示强烈的感动

请结合语气词和强度词来更准确地判断情绪类型和强度。

"""
        
        # 转折句式处理提示（需要区分情绪描述、积极行为和消极行为）
        turnaround_instruction = ""
        if has_turnaround:
            # 检测是否包含积极行为
            positive_actions = [
                '克服', '坚持', '努力', '面对', '战胜', '应对', '挑战', 
                '继续', '前进', '奋斗', '拼搏', '解决', '突破', '进取',
                '勇敢', '坚强', '坚韧', '不屈', '不挠'
            ]
            has_positive_action = any(action in text for action in positive_actions)
            
            turnaround_instruction = """

⚠️ 重要提示：检测到转折句式（如"虽然...但是..."、"虽然...还是..."等）。
请特别注意：需要区分转折后的内容是情绪描述、积极行为还是消极行为。

处理规则：
1. **如果转折后是情绪描述**：优先识别转折后的情绪
   - "虽然很累，但是感觉很充实" → 应该识别为"开心"（转折后的正面情绪：充实）
   - "虽然表面平静，但内心还是有点不安" → 应该识别为"焦虑"（转折后的真实情绪：不安）

2. **如果转折后是积极行为**：识别为积极情绪（期待或开心）
   - "虽然很累，但还是会坚持下去" → 应该识别为"期待"（转折后是积极行为：坚持，表达积极态度）
   - "虽然面临挑战，但我会努力应对" → 应该识别为"期待"（转折后是积极行为：努力应对，表达积极态度）
   
   积极行为关键词：克服、坚持、努力、面对、战胜、应对、挑战、继续、前进、奋斗、拼搏、解决、突破等
   
3. **如果转折后是消极行为**：识别转折前的情绪状态
   - "虽然有点难过，但还是要坚持下去" → 如果转折前难过很明显且转折后只是行为而非情绪转变，仍可识别为"难过"
   - "虽然很焦虑，但还是会努力面对" → 如果转折前焦虑很明显，仍可识别为"焦虑"
   - "虽然很害怕，但还是退缩了" → 应该识别为"焦虑"（转折前是情绪：害怕，转折后是消极行为：退缩）

判断标准：
- 转折后是情绪词汇（开心、难过、焦虑、平静等）→ 识别转折后的情绪
- 转折后是积极行为词汇（克服、坚持、努力、面对、战胜等）→ 识别为"期待"（表达积极态度）
- 转折后是消极行为词汇（放弃、逃避、退缩等）→ 识别转折前的情绪

请仔细分析转折前后的内容类型来确定情绪状态。

"""
        
        # 添加专业词典上下文（如果提供）
        lexicon_section = ""
        if lexicon_context:
            lexicon_section = f"\n{lexicon_context}"
        
        # 检测强烈愤怒词汇并添加提示
        anger_instruction = ""
        anger_keywords = ['恼火', '愤怒', '生气', '怒火', '气愤', '暴躁', '发火', '不满', '火大']
        has_strong_anger = any(keyword in text_truncated for keyword in anger_keywords)
        
        if has_strong_anger:
            anger_instruction = """

🔥 重要提示：检测到强烈的愤怒情绪词汇（如"恼火"、"愤怒"、"生气"等）。
请特别注意：这些词汇明确表达愤怒情绪，应该识别为"愤怒"。
例如：
- "看到不合理的现象，很恼火" → 应该识别为"愤怒"（"恼火"是强烈愤怒情绪）
- "被人误解了，真的很生气" → 应该识别为"愤怒"（"生气"是愤怒情绪）
- "看到不公平的事情，非常愤怒" → 应该识别为"愤怒"（"愤怒"是明确的愤怒情绪）

请直接识别为"愤怒"。

"""
        
        prompt = f"""请分析以下文本内容，判断作者的情绪状态。

可选的情绪标签：{emotion_list}{lexicon_section}{few_shot_examples}{modal_instruction}{turnaround_instruction}{anger_instruction}
文本内容：{text_truncated}

要求：
1. 仔细分析文本的整体情绪倾向
2. 注意语气词和强度词，它们可以帮助判断情绪强度
3. 特别注意转折句式，优先考虑转折后的情绪
4. 从可选的情绪标签中选择一个最匹配的
5. 只返回情绪标签名称，格式：情绪标签名称
6. 不要包含标点符号、解释或其他内容

请直接返回情绪标签名称："""
        
        return prompt
    
    @classmethod
    def _detect_turnaround_keywords(cls, text):
        """
        检测文本中是否包含转折关键词
        
        Returns:
            bool: 是否包含转折关键词
        """
        # 转折关键词列表
        turnaround_keywords = [
            '虽然', '尽管', '固然', '虽说',
            '但是', '但', '可是', '然而', '却', '不过', '只是',
            '还是', '依然', '仍然', '依旧',
            '即使', '即便', '纵然', '纵使',
            '即使...也', '即使...还是',
            '虽然...但是', '虽然...但', '虽然...可是', '虽然...却',
            '尽管...但是', '尽管...但', '尽管...可是',
            '固然...但是', '虽说...但是'
        ]
        
        for keyword in turnaround_keywords:
            if keyword in text:
                return True
        
        return False
    
    @classmethod
    def _detect_mixed_emotion_keywords(cls, text):
        """
        检测文本中是否包含混合情绪关键词
        
        Returns:
            bool: 是否包含混合情绪关键词
        """
        import re
        
        # 混合情绪模式列表
        mixed_emotion_patterns = [
            r'又.*又',  # 又开心又难过
            r'既.*又',  # 既兴奋又紧张
            r'也.*也',  # 也开心也难过
            r'同时.*',  # 同时感到
            r'都有.*',  # 都有
            r'不知道是什么.*感觉',  # 不知道是什么感觉
            r'说不清.*感觉',  # 说不清是什么感觉
            r'说不出来.*感觉',  # 说不出来是什么感觉
            r'不知道是.*感觉',  # 不知道是开心还是难过
            r'心情.*复杂',  # 心情很复杂
            r'感觉.*复杂',  # 感觉很复杂
            r'心情.*矛盾',  # 心情很矛盾
            r'情绪.*矛盾',  # 情绪很矛盾
            r'纠结.*感觉',  # 纠结的感觉
        ]
        
        # 简单关键词列表（不需要正则）
        simple_keywords = [
            '心情很复杂', '情绪很复杂', '感觉很复杂',
            '矛盾的心情', '矛盾的情绪', '矛盾的感觉',
            '说不清', '说不出来', '不知道是什么'
        ]
        
        # 检查简单关键词
        for keyword in simple_keywords:
            if keyword in text:
                return True
        
        # 检查正则模式
        for pattern in mixed_emotion_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    @classmethod
    def _detect_modal_particles(cls, text):
        """
        检测文本中是否包含语气词
        
        Returns:
            dict: {
                'has_particles': bool,  # 是否包含语气词
                'particles': list,      # 检测到的语气词列表
                'intensity_words': list # 强度词列表
            }
        """
        import re
        
        # 语气词列表（表达情绪的语气）
        modal_particles = [
            '啊', '呀', '呢', '吧', '吗', '哦', '喔', '嗯',
            '唉', '哎', '咦', '哇', '喔', '噢', '哼', '嘿',
            '哈', '呵', '嘻', '嘘', '呀', '嘞', '咯', '啦',
            '嘛', '喽', '呐', '哦', '喔', '噢', '呗', '咧'
        ]
        
        # 强度词列表（增强情绪强度）
        intensity_words = [
            '真的', '太', '好', '特别', '非常', '超级', '极其',
            '格外', '十分', '相当', '很', '挺', '蛮', '颇为',
            '简直', '完全', '根本', '实在', '确实', '的确',
            '超级', '超', '巨', '超超', '超超超', '无敌',
            '绝', '贼', '超', '超级无敌'
        ]
        
        detected_particles = []
        detected_intensity = []
        
        # 检测语气词
        for particle in modal_particles:
            if particle in text:
                detected_particles.append(particle)
        
        # 检测强度词
        for intensity in intensity_words:
            # 使用词边界匹配，避免误匹配
            pattern = r'\b' + re.escape(intensity) + r'\b'
            if re.search(pattern, text):
                detected_intensity.append(intensity)
        
        return {
            'has_particles': len(detected_particles) > 0 or len(detected_intensity) > 0,
            'particles': detected_particles,
            'intensity_words': detected_intensity
        }
    
    @classmethod
    def _parse_emotion_result(cls, emotion_result, emotion_names):
        """
        解析DeepSeek返回的情绪分析结果
        使用更智能的匹配策略
        """
        if not emotion_result:
            return None
        
        # 清理结果：移除标点、空格、换行
        emotion_clean = emotion_result.replace('。', '').replace('.', '').replace('，', '').replace(',', '')
        emotion_clean = emotion_clean.replace('：', '').replace(':', '').replace('：', '')
        emotion_clean = emotion_clean.strip().replace('\n', '').replace('\r', '')
        
        # 1. 完全匹配（优先）
        if emotion_clean in emotion_names:
            return emotion_clean
        
        # 2. 部分匹配（如果结果包含情绪名称）
        for name in emotion_names:
            if name in emotion_clean or emotion_clean in name:
                return name
        
        # 3. 移除常见后缀后匹配
        emotion_clean_no_suffix = emotion_clean.replace('情绪', '').replace('状态', '').replace('感觉', '')
        if emotion_clean_no_suffix in emotion_names:
            return emotion_clean_no_suffix
        
        for name in emotion_names:
            if name in emotion_clean_no_suffix or emotion_clean_no_suffix in name:
                return name
        
        # 4. 同义词匹配（扩展）
        synonym_map = {
            '快乐': '开心',
            '高兴': '开心',
            '愉快': '开心',
            '悲伤': '难过',
            '伤心': '难过',
            '沮丧': '难过',
            '担心': '焦虑',
            '不安': '焦虑',
            '紧张': '焦虑',
            '生气': '愤怒',
            '恼火': '愤怒',
            '淡定': '平静',
            '宁静': '平静',
            '累': '疲惫',
            '疲倦': '疲惫',
            '感激': '感动',
            '温暖': '感动',
            '激动': '兴奋',
            '振奋': '兴奋',
            '期望': '期待',
            '盼望': '期待',
            '寂寞': '孤独',
            '孤单': '孤独'
        }
        
        for synonym, emotion_name in synonym_map.items():
            if synonym in emotion_clean and emotion_name in emotion_names:
                return emotion_name
        
        return None

    @classmethod
    def _match_emotion_by_keywords(cls, text):
        """
        通过关键词匹配情绪（使用专业sentiment词典）
        增强：支持转折句式和积极行为识别
        """
        # 1. 检测转折句式和积极行为（优先级最高）
        has_turnaround = cls._detect_turnaround_keywords(text)
        if has_turnaround:
            # 检测积极行为关键词
            positive_actions = [
                '克服', '坚持', '努力', '面对', '战胜', '应对', '挑战', 
                '继续', '前进', '奋斗', '拼搏', '解决', '突破', '进取',
                '勇敢', '坚强', '坚韧', '不屈', '不挠'
            ]
            text_lower = text.lower()
            has_positive_action = any(action in text_lower for action in positive_actions)
            
            if has_positive_action:
                # 转折后是积极行为，识别为"期待"
                current_app.logger.debug(
                    f"关键词匹配：检测到转折句式和积极行为，返回'期待': {text[:50]}..."
                )
                return '期待'
        
        # 2. 检测强烈愤怒词汇（优先级较高）
        anger_keywords = ['恼火', '愤怒', '生气', '怒火', '气愤', '暴躁', '发火', '不满', '火大']
        text_lower_check = text.lower()
        if any(keyword in text_lower_check for keyword in anger_keywords):
            current_app.logger.debug(
                f"关键词匹配：检测到强烈愤怒词汇，返回'愤怒': {text[:50]}..."
            )
            return '愤怒'
        
        # 3. 使用专业词典
        try:
            lexicon_result = SentimentLexicon.analyze_with_lexicon(text)
            if lexicon_result and lexicon_result['emotion_scores']:
                # 返回得分最高的情绪
                top_emotion = max(
                    lexicon_result['emotion_scores'], 
                    key=lexicon_result['emotion_scores'].get
                )
                return top_emotion
        except Exception as e:
            current_app.logger.warning(f"专业词典匹配失败，使用默认关键词: {str(e)}")
        
        # 4. 降级方案：使用基础关键词（如果专业词典失败）
        emotion_keywords = {
            '开心': ['开心', '快乐', '高兴', '愉快', '欢乐', '喜悦', '兴奋', '开心地', '快乐地'],
            '难过': ['难过', '悲伤', '伤心', '痛苦', '失落', '沮丧', '孤独', '想哭', '眼泪'],
            '焦虑': ['焦虑', '担心', '忧虑', '不安', '紧张', '压力', '烦恼', '急躁', '恐慌'],
            '愤怒': ['愤怒', '生气', '怒火', '不满', '气愤', '暴躁', '发火', '恼火'],
            '平静': ['平静', '安静', '宁静', '淡定', '从容', '平和', '放松', '舒心'],
            '疲惫': ['疲惫', '累', '疲倦', '劳累', '乏力', '困倦', '筋疲力尽', '很累'],
            '感动': ['感动', '感激', '感恩', '温暖', '暖心', '触动', '动容', '泪目'],
            '兴奋': ['兴奋', '激动', '振奋', '热情', '充满', '活力', '激昂', '热血'],
            '期待': ['期待', '期望', '盼望', '希望', '等待', '憧憬', '向往', '期盼'],
            '孤独': ['孤独', '寂寞', '孤单', '独自', '一个人', '孤立', '无人', '寂寞地']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion_name, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion_name] = score
        
        if not emotion_scores:
            return '平静'  # 默认返回平静
        
        # 返回得分最高的情绪
        return max(emotion_scores, key=emotion_scores.get)
    
    @classmethod
    def _calculate_keyword_confidence(cls, text, emotion_name):
        """
        计算关键词匹配的置信度（使用专业sentiment词典）
        
        Args:
            text: 文本内容
            emotion_name: 匹配到的情绪名称
            
        Returns:
            float: 置信度（0.0 ~ 1.0）
        """
        if not emotion_name:
            return 0.0
        
        # 优先使用专业词典计算置信度
        try:
            enhance_result = SentimentLexicon.enhance_keyword_matching(text, emotion_name)
            if enhance_result and enhance_result['matched']:
                # 使用专业词典的置信度，结合强度加权
                confidence = enhance_result['confidence']
                intensity = enhance_result.get('intensity', 0.5)
                # 强度加权：强度越高，置信度越高
                final_confidence = confidence * (0.5 + intensity * 0.5)
                return min(final_confidence, 1.0)
        except Exception as e:
            current_app.logger.warning(f"专业词典置信度计算失败，使用默认方法: {str(e)}")
        
        # 降级方案：使用基础关键词
        emotion_keywords = {
            '开心': ['开心', '快乐', '高兴', '愉快', '欢乐', '喜悦', '兴奋', '开心地', '快乐地'],
            '难过': ['难过', '悲伤', '伤心', '痛苦', '失落', '沮丧', '孤独', '想哭', '眼泪'],
            '焦虑': ['焦虑', '担心', '忧虑', '不安', '紧张', '压力', '烦恼', '急躁', '恐慌'],
            '愤怒': ['愤怒', '生气', '怒火', '不满', '气愤', '暴躁', '发火', '恼火'],
            '平静': ['平静', '安静', '宁静', '淡定', '从容', '平和', '放松', '舒心'],
            '疲惫': ['疲惫', '累', '疲倦', '劳累', '乏力', '困倦', '筋疲力尽', '很累'],
            '感动': ['感动', '感激', '感恩', '温暖', '暖心', '触动', '动容', '泪目'],
            '兴奋': ['兴奋', '激动', '振奋', '热情', '充满', '活力', '激昂', '热血'],
            '期待': ['期待', '期望', '盼望', '希望', '等待', '憧憬', '向往', '期盼'],
            '孤独': ['孤独', '寂寞', '孤单', '独自', '一个人', '孤立', '无人', '寂寞地']
        }
        
        keywords = emotion_keywords.get(emotion_name, [])
        if not keywords:
            return 0.5
        
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        max_possible = len(keywords)
        
        # 置信度 = 匹配数 / 可能的关键词数，但有上限
        confidence = min(matches / max_possible, 1.0)
        
        # 如果匹配多个关键词，提高置信度
        if matches >= 2:
            confidence = min(confidence + 0.2, 1.0)
        
        return max(confidence, 0.3)  # 最低置信度0.3

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
    
    @classmethod
    def get_task_template(cls, task_name):
        """
        获取任务模板（参考cntext的设计）
        
        Args:
            task_name: 任务模板名称
            
        Returns:
            dict: 任务模板，包含prompt和output_format
        """
        return cls.EMOTION_TASK_TEMPLATES.get(task_name)
    
    @classmethod
    def analyze_emotion_enhanced(cls, text):
        """
        增强版情绪分析（结合专业sentiment词典和DeepSeek）
        返回结构化结果：{label, score, confidence, intensity}
        
        Args:
            text: 待分析的文本内容
            
        Returns:
            dict: {
                'label': str,        # 情绪标签名称
                'score': float,      # 情绪分值（-1.0 ~ 1.0，负数为负面）
                'confidence': float, # 置信度（0.0 ~ 1.0）
                'intensity': float,  # 强度（0.0 ~ 1.0）
                'method': str        # 分析方法：'hybrid'/'llm'/'lexicon'/'keyword'
            } 或 None
        """
        if not text or len(text.strip()) < 3:
            return None
        
        # 第一步：使用专业sentiment词典进行预分析
        lexicon_result = None
        try:
            lexicon_result = SentimentLexicon.analyze_with_lexicon(text)
        except Exception as e:
            current_app.logger.warning(f"专业词典预分析失败: {str(e)}")
        
        # 如果专业词典置信度很高，优先使用词典结果
        if lexicon_result and lexicon_result.get('confidence', 0) >= 0.85:
            top_emotion = max(
                lexicon_result['emotion_scores'], 
                key=lexicon_result['emotion_scores'].get
            ) if lexicon_result['emotion_scores'] else None
            
            if top_emotion:
                current_app.logger.debug(
                    f"专业词典高置信度结果: {top_emotion}, "
                    f"置信度: {lexicon_result['confidence']:.2f}"
                )
                return {
                    'label': top_emotion,
                    'score': cls._calculate_emotion_score(top_emotion),
                    'confidence': lexicon_result['confidence'],
                    'intensity': lexicon_result['intensity'],
                    'method': 'lexicon_high_confidence'
                }
        
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            # 没有API Key，使用专业词典或关键词匹配
            if lexicon_result and lexicon_result['emotion_scores']:
                top_emotion = max(
                    lexicon_result['emotion_scores'], 
                    key=lexicon_result['emotion_scores'].get
                )
                return {
                    'label': top_emotion,
                    'score': cls._calculate_emotion_score(top_emotion),
                    'confidence': lexicon_result.get('confidence', 0.6),
                    'intensity': lexicon_result.get('intensity', 0.5),
                    'method': 'lexicon'
                }
            
            # 降级到简单关键词匹配
            label = cls._match_emotion_by_keywords(text)
            confidence = cls._calculate_keyword_confidence(text, label)
            return {
                'label': label,
                'score': cls._calculate_emotion_score(label),
                'confidence': confidence,
                'intensity': 0.5,
                'method': 'keyword'
            }
        
        try:
            from app_2.model.emotion_label import EmotionLabel
            system_labels = EmotionLabel.get_system_labels()
            emotion_names = [label.name for label in system_labels]
            emotion_list = '、'.join(emotion_names)
            
            # 检测特殊情况
            has_turnaround = cls._detect_turnaround_keywords(text)
            has_mixed_emotion = cls._detect_mixed_emotion_keywords(text)
            modal_info = cls._detect_modal_particles(text)
            
            # 如果检测到混合情绪，直接返回待定
            if has_mixed_emotion:
                return {
                    'label': '待定',
                    'score': 0.0,
                    'confidence': 0.9,
                    'intensity': 0.5,
                    'method': 'mixed_emotion_detection'
                }
            
            # 将专业词典分析结果融入DeepSeek提示词
            lexicon_hint = ""
            if lexicon_result and lexicon_result['emotion_scores']:
                # 获取词典分析的前3个情绪及其得分
                sorted_emotions = sorted(
                    lexicon_result['emotion_scores'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                lexicon_hint = "\n💡 专业词典分析提示："
                lexicon_hint += f"\n   情绪倾向: {lexicon_result.get('valence', 'neutral')}"
                lexicon_hint += f"\n   情绪强度: {lexicon_result.get('intensity', 0.5):.2f}"
                if sorted_emotions:
                    emotion_str = ', '.join([f"{name}({score:.2f})" for name, score in sorted_emotions])
                    lexicon_hint += f"\n   候选情绪（按得分排序）: {emotion_str}"
                    lexicon_hint += f"\n   建议重点考虑以上候选情绪，但需结合上下文综合分析。"
            
            # 构建结构化输出的提示词
            prompt_parts = [
                f"分析文本的情绪状态，返回结构化结果。",
                f"\n可选的情绪标签：{emotion_list}",
            ]
            
            # 添加专业词典分析提示（如果可用）
            if lexicon_hint:
                prompt_parts.append(lexicon_hint)
            
            prompt_parts.extend([
                f"\n要求：",
                f"1. 识别文本的主要情绪类型（label）",
                f"2. 计算情绪分值（score）：",
                f"   - 正面情绪（开心、兴奋、期待、感动、平静）：0.0 ~ 1.0",
                f"   - 负面情绪（难过、焦虑、愤怒、疲惫、孤独）：-1.0 ~ 0.0",
                f"3. 评估置信度（confidence）：0.0 ~ 1.0，表示识别的把握程度",
                f"4. 评估强度（intensity）：0.0 ~ 1.0，表示情绪的强烈程度",
            ])
            
            # 添加特殊情况提示
            if has_turnaround:
                prompt_parts.append("\n⚠️ 注意：检测到转折句式，请特别注意转折后的内容表达真实情绪。")
            if modal_info['has_particles']:
                particles_str = '、'.join(set(modal_info['particles'])) if modal_info['particles'] else ''
                intensity_str = '、'.join(set(modal_info['intensity_words'])) if modal_info['intensity_words'] else ''
                if particles_str or intensity_str:
                    prompt_parts.append(f"\n💡 提示：检测到语气词和强度词，请结合它们判断情绪强度。")
            
            prompt_parts.append(f"\n文本内容：{text[:800]}")
            prompt_parts.append(f"\n请以JSON格式返回结果，格式：{{\"label\": \"情绪标签\", \"score\": 0.5, \"confidence\": 0.8, \"intensity\": 0.7}}")
            
            prompt = ''.join(prompt_parts)
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': cls._build_system_message()},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 150,  # 增加token数以容纳JSON
                    'temperature': 0.1,
                    'top_p': 0.9,
                    'response_format': {'type': 'json_object'}  # 要求返回JSON
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                result_str = data['choices'][0]['message']['content'].strip()
                
                # 解析JSON结果
                try:
                    result = json.loads(result_str)
                    
                    # 验证结果格式
                    if 'label' in result:
                        label = cls._parse_emotion_result(result['label'], emotion_names)
                        if label:
                            # 结合专业词典结果和DeepSeek结果
                            llm_confidence = float(result.get('confidence', 0.8))
                            llm_intensity = float(result.get('intensity', 0.5))
                            llm_score = float(result.get('score', 0.0))
                            
                            # 如果专业词典也识别出了相同或相似的情绪，提升置信度
                            final_confidence = llm_confidence
                            final_intensity = llm_intensity
                            
                            if lexicon_result and lexicon_result['emotion_scores']:
                                lexicon_top = max(
                                    lexicon_result['emotion_scores'], 
                                    key=lexicon_result['emotion_scores'].get
                                )
                                lexicon_score = lexicon_result['emotion_scores'].get(lexicon_top, 0)
                                
                                # 如果词典和DeepSeek结果一致，加权提升置信度
                                if lexicon_top == label:
                                    # 两者一致，加权计算：DeepSeek 70% + 词典 30%
                                    final_confidence = llm_confidence * 0.7 + lexicon_result['confidence'] * 0.3
                                    final_confidence = min(final_confidence, 0.95)  # 最高0.95
                                    # 强度取两者平均值
                                    final_intensity = (llm_intensity + lexicon_result['intensity']) / 2.0
                                    method = 'hybrid'
                                    current_app.logger.debug(
                                        f"专业词典和DeepSeek结果一致: {label}, "
                                        f"综合置信度: {final_confidence:.2f}"
                                    )
                                elif lexicon_score > 2.0:  # 词典有较强的信号
                                    # 结果不一致，但词典有较强信号，降低置信度
                                    final_confidence = llm_confidence * 0.8
                                    method = 'llm_with_lexicon_conflict'
                                    current_app.logger.debug(
                                        f"专业词典和DeepSeek结果不一致: 词典={lexicon_top}, "
                                        f"DeepSeek={label}, 使用DeepSeek结果但降低置信度"
                                    )
                                else:
                                    method = 'llm'
                            else:
                                method = 'llm'
                            
                            return {
                                'label': label,
                                'score': llm_score,
                                'confidence': final_confidence,
                                'intensity': final_intensity,
                                'method': method
                            }
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    # JSON解析失败，尝试从文本中提取
                    current_app.logger.warning(f"JSON解析失败: {result_str}, 错误: {str(e)}")
                    # 尝试解析文本格式的结果
                    if 'label' in result_str or any(name in result_str for name in emotion_names):
                        label = cls._parse_emotion_result(result_str, emotion_names)
                        if label:
                            return {
                                'label': label,
                                'score': cls._calculate_emotion_score(label),
                                'confidence': 0.7,
                                'intensity': 0.5,
                                'method': 'llm_text_parsed'
                            }
            
            # 降级处理
            label = cls._match_emotion_by_keywords(text)
            confidence = cls._calculate_keyword_confidence(text, label)
            return {
                'label': label,
                'score': cls._calculate_emotion_score(label),
                'confidence': confidence,
                'intensity': 0.5,
                'method': 'keyword_fallback'
            }
            
        except requests.Timeout:
            current_app.logger.error(f"增强情绪分析超时: {text[:50]}...")
            label = cls._match_emotion_by_keywords(text)
            confidence = cls._calculate_keyword_confidence(text, label)
            return {
                'label': label,
                'score': cls._calculate_emotion_score(label),
                'confidence': confidence,
                'intensity': 0.5,
                'method': 'keyword_timeout'
            }
        except Exception as e:
            current_app.logger.error(f"增强情绪分析失败: {str(e)}")
            label = cls._match_emotion_by_keywords(text)
            confidence = cls._calculate_keyword_confidence(text, label)
            return {
                'label': label,
                'score': cls._calculate_emotion_score(label),
                'confidence': confidence,
                'intensity': 0.5,
                'method': 'keyword_exception'
            }
    
    @classmethod
    def _calculate_emotion_score(cls, emotion_name):
        """
        根据情绪名称计算情绪分值
        
        Args:
            emotion_name: 情绪标签名称
            
        Returns:
            float: 情绪分值（-1.0 ~ 1.0）
        """
        if not emotion_name:
            return 0.0
        
        # 正面情绪
        positive_emotions = ['开心', '兴奋', '期待', '感动', '平静']
        # 负面情绪
        negative_emotions = ['难过', '焦虑', '愤怒', '疲惫', '孤独']
        
        if emotion_name in positive_emotions:
            # 正面情绪：0.3 ~ 1.0
            scores = {
                '开心': 0.8,
                '兴奋': 0.9,
                '期待': 0.7,
                '感动': 0.8,
                '平静': 0.5
            }
            return scores.get(emotion_name, 0.6)
        elif emotion_name in negative_emotions:
            # 负面情绪：-1.0 ~ -0.3
            scores = {
                '难过': -0.7,
                '焦虑': -0.6,
                '愤怒': -0.8,
                '疲惫': -0.5,
                '孤独': -0.6
            }
            return scores.get(emotion_name, -0.5)
        elif emotion_name == '待定':
            return 0.0
        else:
            return 0.0
    
    @classmethod
    def analyze_emotion_batch(cls, texts, max_concurrent=5):
        """
        批量情绪分析（参考cntext的批量处理方式）
        
        Args:
            texts: 文本列表
            max_concurrent: 最大并发数
            
        Returns:
            list: 情绪分析结果列表，每个元素是dict或None
        """
        import concurrent.futures
        
        results = []
        
        def analyze_single(text):
            try:
                return cls.analyze_emotion_enhanced(text)
            except Exception as e:
                current_app.logger.error(f"批量分析单个文本失败: {str(e)}")
                return None
        
        # 使用线程池进行批量处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_text = {executor.submit(analyze_single, text): text for text in texts}
            
            for future in concurrent.futures.as_completed(future_to_text):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    current_app.logger.error(f"批量分析失败: {str(e)}")
                    results.append(None)
        
        return results
    
    @classmethod
    def analyze_emotion_with_lexicon(cls, text):
        """
        结合专业sentiment词典和DeepSeek的混合分析（参考cntext的多方法结合）
        
        工作流程：
        1. 优先使用专业sentiment词典预分析（快速）
        2. 如果置信度高（>=0.85），直接返回词典结果
        3. 如果置信度中等（0.7-0.85），使用DeepSeek增强分析，结合两者结果
        4. 如果置信度低（<0.7），使用DeepSeek完整分析
        
        Args:
            text: 待分析的文本内容
            
        Returns:
            dict: 结构化情绪分析结果
        """
        # 第一步：使用专业sentiment词典预分析
        lexicon_result = None
        try:
            lexicon_result = SentimentLexicon.analyze_with_lexicon(text)
        except Exception as e:
            current_app.logger.warning(f"专业词典分析失败: {str(e)}")
        
        # 如果专业词典置信度很高（>=0.85），直接返回
        if lexicon_result and lexicon_result.get('confidence', 0) >= 0.85:
            top_emotion = max(
                lexicon_result['emotion_scores'], 
                key=lexicon_result['emotion_scores'].get
            ) if lexicon_result['emotion_scores'] else None
            
            if top_emotion:
                current_app.logger.debug(
                    f"专业词典高置信度结果: {top_emotion}, "
                    f"置信度: {lexicon_result['confidence']:.2f}"
                )
                return {
                    'label': top_emotion,
                    'score': cls._calculate_emotion_score(top_emotion),
                    'confidence': lexicon_result['confidence'],
                    'intensity': lexicon_result['intensity'],
                    'method': 'lexicon_high_confidence'
                }
        
        # 第二步：使用增强版分析（内部已结合sentiment词典和DeepSeek）
        # analyze_emotion_enhanced 方法内部会：
        # 1. 先用sentiment词典预分析
        # 2. 如果置信度>=0.85，直接返回
        # 3. 否则调用DeepSeek，并将词典结果融入提示词
        # 4. 结合两者的结果计算综合置信度
        enhanced_result = cls.analyze_emotion_enhanced(text)
        
        if enhanced_result:
            # 增强版分析已经结合了sentiment词典和DeepSeek
            # 如果方法标记为hybrid，说明两者结果一致
            method = enhanced_result.get('method', 'unknown')
            
            current_app.logger.debug(
                f"混合分析完成: {enhanced_result.get('label')}, "
                f"方法: {method}, "
                f"置信度: {enhanced_result.get('confidence', 0):.2f}"
            )
            
            return enhanced_result
        
        # 降级：如果增强版分析失败，使用基础关键词匹配
        keyword_result = cls._match_emotion_by_keywords(text)
        keyword_confidence = cls._calculate_keyword_confidence(text, keyword_result)
        
        return {
            'label': keyword_result,
            'score': cls._calculate_emotion_score(keyword_result),
            'confidence': keyword_confidence,
            'intensity': 0.5,
            'method': 'keyword_fallback'
        }

