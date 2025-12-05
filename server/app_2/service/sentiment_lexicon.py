# -*- coding: utf-8 -*-
"""
情感词典服务
从sentiment文件夹加载专业的情感词典，用于增强情绪识别功能
"""

import os
import re


class SentimentLexicon:
    """情感词典类"""
    
    # 情感词典缓存
    _lexicons = None
    
    # 情绪标签映射
    EMOTION_MAPPING = {
        # 正面情绪
        '开心': {
            'positive_emotion': True,
            'keywords': []
        },
        '兴奋': {
            'positive_emotion': True,
            'keywords': []
        },
        '期待': {
            'positive_emotion': True,
            'keywords': []
        },
        '感动': {
            'positive_emotion': True,
            'keywords': []
        },
        '平静': {
            'positive_emotion': True,
            'keywords': []
        },
        # 负面情绪
        '难过': {
            'positive_emotion': False,
            'keywords': []
        },
        '焦虑': {
            'positive_emotion': False,
            'keywords': []
        },
        '愤怒': {
            'positive_emotion': False,
            'keywords': []
        },
        '疲惫': {
            'positive_emotion': False,
            'keywords': []
        },
        '孤独': {
            'positive_emotion': False,
            'keywords': []
        },
        '待定': {
            'positive_emotion': None,
            'keywords': []
        }
    }
    
    # 程度级别词语（用于判断情绪强度）
    INTENSITY_WORDS = {
        'very_high': [],  # 极其、最、万分等
        'high': [],       # 很、非常、特别等
        'medium': [],     # 比较、较为、颇等
        'low': []         # 有点、稍微、略等
    }
    
    @classmethod
    def load_lexicons(cls):
        """加载sentiment文件夹中的词典"""
        if cls._lexicons is not None:
            return cls._lexicons
        
        # 获取sentiment文件夹路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        sentiment_dir = os.path.join(project_root, 'sentiment')
        
        if not os.path.exists(sentiment_dir):
            print(f"[警告] sentiment文件夹不存在: {sentiment_dir}")
            return cls._get_default_lexicons()
        
        lexicons = {
            'positive_emotion': [],      # 正面情感词语
            'negative_emotion': [],       # 负面情感词语
            'positive_evaluation': [],    # 正面评价词语
            'negative_evaluation': [],   # 负面评价词语
            'intensity_words': {          # 程度级别词语
                'very_high': [],
                'high': [],
                'medium': [],
                'low': []
            },
            'claim_words': []             # 主张词语
        }
        
        # 读取正面情感词语
        positive_emotion_file = os.path.join(sentiment_dir, '正面情感词语（中文）.txt')
        if os.path.exists(positive_emotion_file):
            lexicons['positive_emotion'] = cls._read_lexicon_file(positive_emotion_file)
            print(f"[加载] 正面情感词语: {len(lexicons['positive_emotion'])} 个")
        
        # 读取负面情感词语
        negative_emotion_file = os.path.join(sentiment_dir, '负面情感词语（中文）.txt')
        if os.path.exists(negative_emotion_file):
            lexicons['negative_emotion'] = cls._read_lexicon_file(negative_emotion_file)
            print(f"[加载] 负面情感词语: {len(lexicons['negative_emotion'])} 个")
        
        # 读取正面评价词语
        positive_eval_file = os.path.join(sentiment_dir, '正面评价词语（中文）.txt')
        if os.path.exists(positive_eval_file):
            lexicons['positive_evaluation'] = cls._read_lexicon_file(positive_eval_file)
            print(f"[加载] 正面评价词语: {len(lexicons['positive_evaluation'])} 个")
        
        # 读取负面评价词语
        negative_eval_file = os.path.join(sentiment_dir, '负面评价词语（中文）.txt')
        if os.path.exists(negative_eval_file):
            lexicons['negative_evaluation'] = cls._read_lexicon_file(negative_eval_file)
            print(f"[加载] 负面评价词语: {len(lexicons['negative_evaluation'])} 个")
        
        # 读取程度级别词语
        intensity_file = os.path.join(sentiment_dir, '程度级别词语（中文）.txt')
        if os.path.exists(intensity_file):
            intensity_data = cls._read_intensity_file(intensity_file)
            lexicons['intensity_words'].update(intensity_data)
            total_intensity = sum(len(v) for v in intensity_data.values())
            print(f"[加载] 程度级别词语: {total_intensity} 个")
        
        # 读取主张词语
        claim_file = os.path.join(sentiment_dir, '主张词语（中文）.txt')
        if os.path.exists(claim_file):
            lexicons['claim_words'] = cls._read_lexicon_file(claim_file)
            print(f"[加载] 主张词语: {len(lexicons['claim_words'])} 个")
        
        # 构建情绪关键词映射
        cls._build_emotion_keywords(lexicons)
        
        cls._lexicons = lexicons
        return lexicons
    
    @classmethod
    def _read_lexicon_file(cls, filepath):
        """
        读取词典文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            list: 词语列表
        """
        words = []
        
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
            
            content = None
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print(f"[警告] 无法读取文件: {filepath}")
                return words
            
            # 解析文件内容
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 跳过标题行（包含数字的行）
                if re.match(r'^[^a-zA-Z\u4e00-\u9fa5]*\d+', line):
                    continue
                
                # 提取词语（去除数字、标点等）
                words_in_line = re.findall(r'[\u4e00-\u9fa5]+', line)
                words.extend(words_in_line)
            
            # 去重并过滤
            words = list(set(words))
            words = [w for w in words if len(w) >= 2]  # 至少2个字符
            
        except Exception as e:
            print(f"[错误] 读取词典文件失败: {filepath}, 错误: {str(e)}")
        
        return words
    
    @classmethod
    def _read_intensity_file(cls, filepath):
        """
        读取程度级别词语文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            dict: 按级别分类的词语字典
        """
        intensity_dict = {
            'very_high': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        try:
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
            
            content = None
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return intensity_dict
            
            lines = content.strip().split('\n')
            
            current_level = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 检测级别标识
                if 'extreme' in line.lower() or 'most' in line.lower() or '极其' in line:
                    current_level = 'very_high'
                elif 'very' in line.lower() or '很' in line or '非常' in line:
                    current_level = 'high'
                elif 'medium' in line.lower() or '比较' in line or '较为' in line:
                    current_level = 'medium'
                elif 'little' in line.lower() or '有点' in line or '稍微' in line:
                    current_level = 'low'
                else:
                    # 提取词语
                    words = re.findall(r'[\u4e00-\u9fa5]+', line)
                    if words and current_level:
                        intensity_dict[current_level].extend(words)
            
            # 去重
            for level in intensity_dict:
                intensity_dict[level] = list(set(intensity_dict[level]))
                intensity_dict[level] = [w for w in intensity_dict[level] if len(w) >= 1]
        
        except Exception as e:
            print(f"[错误] 读取程度级别文件失败: {filepath}, 错误: {str(e)}")
        
        return intensity_dict
    
    @classmethod
    def _build_emotion_keywords(cls, lexicons):
        """
        构建情绪关键词映射
        
        Args:
            lexicons: 词典字典
        """
        # 正面情绪关键词（从正面情感词语和正面评价词语中提取）
        positive_keywords = set(lexicons.get('positive_emotion', []))
        positive_keywords.update(lexicons.get('positive_evaluation', []))
        
        # 负面情绪关键词（从负面情感词语和负面评价词语中提取）
        negative_keywords = set(lexicons.get('negative_emotion', []))
        negative_keywords.update(lexicons.get('negative_evaluation', []))
        
        # 映射到具体情绪标签
        # 开心、兴奋、期待、感动、平静 - 使用正面关键词
        positive_emotions = ['开心', '兴奋', '期待', '感动', '平静']
        for emotion in positive_emotions:
            cls.EMOTION_MAPPING[emotion]['keywords'] = list(positive_keywords)
        
        # 难过、焦虑、愤怒、疲惫、孤独 - 使用负面关键词
        negative_emotions = ['难过', '焦虑', '愤怒', '疲惫', '孤独']
        for emotion in negative_emotions:
            cls.EMOTION_MAPPING[emotion]['keywords'] = list(negative_keywords)
    
    @classmethod
    def _get_default_lexicons(cls):
        """获取默认词典（如果无法加载文件）"""
        return {
            'positive_emotion': [],
            'negative_emotion': [],
            'positive_evaluation': [],
            'negative_evaluation': [],
            'intensity_words': {
                'very_high': ['极其', '最', '万分', '极度'],
                'high': ['很', '非常', '特别', '十分', '相当'],
                'medium': ['比较', '较为', '颇', '挺', '蛮'],
                'low': ['有点', '稍微', '略', '少许']
            },
            'claim_words': []
        }
    
    @classmethod
    def analyze_with_lexicon(cls, text):
        """
        使用专业词典分析文本情绪
        
        Args:
            text: 待分析的文本
            
        Returns:
            dict: {
                'emotion_scores': dict,  # 各情绪得分
                'intensity': float,      # 情绪强度
                'valence': str,          # 情绪倾向：'positive'/'negative'/'neutral'
                'confidence': float     # 置信度
            }
        """
        lexicons = cls.load_lexicons()
        
        if not lexicons:
            return None
        
        text_lower = text.lower()
        emotion_scores = {}
        
        # 统计各情绪关键词出现次数
        for emotion, info in cls.EMOTION_MAPPING.items():
            if emotion == '待定':
                continue
            
            keywords = info.get('keywords', [])
            if not keywords:
                continue
            
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # 计算权重（考虑词语长度，长词权重更高）
                    weight = len(keyword) / 4.0  # 最长4个字，权重1.0
                    score += weight
            
            if score > 0:
                emotion_scores[emotion] = score
        
        # 计算情绪倾向
        positive_score = sum(
            emotion_scores.get(e, 0) 
            for e in ['开心', '兴奋', '期待', '感动', '平静']
        )
        negative_score = sum(
            emotion_scores.get(e, 0) 
            for e in ['难过', '焦虑', '愤怒', '疲惫', '孤独']
        )
        
        if positive_score > negative_score * 1.5:
            valence = 'positive'
        elif negative_score > positive_score * 1.5:
            valence = 'negative'
        else:
            valence = 'neutral'
        
        # 计算强度
        intensity = cls._calculate_intensity(text, lexicons['intensity_words'])
        
        # 计算置信度
        total_score = sum(emotion_scores.values())
        confidence = min(total_score / 10.0, 1.0)  # 最多匹配10个词时置信度为1.0
        confidence = max(confidence, 0.3)  # 最低0.3
        
        return {
            'emotion_scores': emotion_scores,
            'intensity': intensity,
            'valence': valence,
            'confidence': confidence
        }
    
    @classmethod
    def _calculate_intensity(cls, text, intensity_words):
        """
        计算情绪强度
        
        Args:
            text: 文本内容
            intensity_words: 程度级别词语字典
            
        Returns:
            float: 强度值（0.0 ~ 1.0）
        """
        text_lower = text.lower()
        
        # 检查极高程度词
        for word in intensity_words.get('very_high', []):
            if word in text_lower:
                return 1.0
        
        # 检查高程度词
        for word in intensity_words.get('high', []):
            if word in text_lower:
                return 0.8
        
        # 检查中等程度词
        for word in intensity_words.get('medium', []):
            if word in text_lower:
                return 0.5
        
        # 检查低程度词
        for word in intensity_words.get('low', []):
            if word in text_lower:
                return 0.3
        
        # 默认强度
        return 0.5
    
    @classmethod
    def get_top_emotion(cls, text):
        """
        使用词典获取主要情绪
        
        Args:
            text: 待分析的文本
            
        Returns:
            str: 情绪标签名称
        """
        result = cls.analyze_with_lexicon(text)
        if not result or not result['emotion_scores']:
            return None
        
        # 返回得分最高的情绪
        top_emotion = max(result['emotion_scores'], key=result['emotion_scores'].get)
        return top_emotion
    
    @classmethod
    def enhance_keyword_matching(cls, text, emotion_name):
        """
        使用专业词典增强关键词匹配
        
        Args:
            text: 待分析的文本
            emotion_name: 情绪名称
            
        Returns:
            dict: {
                'matched': bool,        # 是否匹配
                'confidence': float,   # 置信度
                'intensity': float,    # 强度
                'matched_keywords': list  # 匹配的关键词
            }
        """
        lexicons = cls.load_lexicons()
        emotion_info = cls.EMOTION_MAPPING.get(emotion_name)
        
        if not emotion_info:
            return {
                'matched': False,
                'confidence': 0.0,
                'intensity': 0.5,
                'matched_keywords': []
            }
        
        text_lower = text.lower()
        keywords = emotion_info.get('keywords', [])
        
        matched_keywords = []
        for keyword in keywords:
            if keyword in text_lower:
                matched_keywords.append(keyword)
        
        if not matched_keywords:
            return {
                'matched': False,
                'confidence': 0.0,
                'intensity': 0.5,
                'matched_keywords': []
            }
        
        # 计算置信度
        confidence = min(len(matched_keywords) / 5.0, 1.0)
        confidence = max(confidence, 0.3)
        
        # 计算强度
        intensity = cls._calculate_intensity(text, lexicons.get('intensity_words', {}))
        
        return {
            'matched': True,
            'confidence': confidence,
            'intensity': intensity,
            'matched_keywords': matched_keywords[:10]  # 最多返回10个
        }

