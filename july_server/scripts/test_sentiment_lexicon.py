#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试专业sentiment词典功能
"""

import sys
import os

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 设置控制台编码（Windows）
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from app_2.service.sentiment_lexicon import SentimentLexicon


def test_lexicon_loading():
    """测试词典加载"""
    print("="*80)
    print("[测试] 测试专业词典加载")
    print("="*80)
    
    lexicons = SentimentLexicon.load_lexicons()
    
    if lexicons:
        print("\n[成功] 词典加载成功！")
        print(f"  正面情感词语: {len(lexicons.get('positive_emotion', []))} 个")
        print(f"  负面情感词语: {len(lexicons.get('negative_emotion', []))} 个")
        print(f"  正面评价词语: {len(lexicons.get('positive_evaluation', []))} 个")
        print(f"  负面评价词语: {len(lexicons.get('negative_evaluation', []))} 个")
        
        intensity_words = lexicons.get('intensity_words', {})
        print(f"  程度级别词语:")
        print(f"    极高: {len(intensity_words.get('very_high', []))} 个")
        print(f"    高: {len(intensity_words.get('high', []))} 个")
        print(f"    中等: {len(intensity_words.get('medium', []))} 个")
        print(f"    低: {len(intensity_words.get('low', []))} 个")
        
        print(f"\n  主张词语: {len(lexicons.get('claim_words', []))} 个")
        
        # 显示部分示例
        if lexicons.get('positive_emotion'):
            print(f"\n[示例] 正面情感词语（前10个）:")
            for word in lexicons['positive_emotion'][:10]:
                print(f"    {word}")
        
        if lexicons.get('negative_emotion'):
            print(f"\n[示例] 负面情感词语（前10个）:")
            for word in lexicons['negative_emotion'][:10]:
                print(f"    {word}")
    else:
        print("\n[警告] 词典加载失败，使用默认词典")
    
    return lexicons


def test_emotion_analysis():
    """测试情绪分析"""
    print("\n" + "="*80)
    print("[测试] 测试情绪分析功能")
    print("="*80)
    
    test_cases = [
        ("今天心情特别好，感觉整个人都充满了活力", "开心"),
        ("看到了期待已久的电影，太开心了", "开心"),
        ("今天心情很低落，感觉做什么都没意思", "难过"),
        ("失去了重要的东西，很难过", "难过"),
        ("明天有重要的考试，心里很紧张和焦虑", "焦虑"),
        ("工作压力太大，总是担心做不好", "焦虑"),
        ("被人误解了，真的很生气", "愤怒"),
        ("今天没什么特别的事，心情很平静", "平静"),
        ("连续工作了好几天，感觉很累", "疲惫"),
        ("看到朋友的帮助，真的很感动", "感动"),
    ]
    
    print("\n[测试用例]")
    for i, (text, expected) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 测试用例:")
        print(f"  文本: {text}")
        print(f"  期望: {expected}")
        
        try:
            # 使用专业词典分析
            result = SentimentLexicon.analyze_with_lexicon(text)
            
            if result:
                emotion_scores = result.get('emotion_scores', {})
                if emotion_scores:
                    top_emotion = max(emotion_scores, key=emotion_scores.get)
                    confidence = result.get('confidence', 0.0)
                    intensity = result.get('intensity', 0.5)
                    valence = result.get('valence', 'neutral')
                    
                    match = top_emotion == expected
                    icon = "[正确]" if match else "[错误]"
                    
                    print(f"  结果: {icon} {top_emotion}")
                    print(f"  得分: {emotion_scores.get(top_emotion, 0):.2f}")
                    print(f"  置信度: {confidence:.2f}")
                    print(f"  强度: {intensity:.2f}")
                    print(f"  倾向: {valence}")
                    
                    # 显示所有情绪得分
                    if len(emotion_scores) > 1:
                        print(f"  所有情绪得分:")
                        sorted_scores = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                        for emotion, score in sorted_scores:
                            print(f"    {emotion}: {score:.2f}")
                else:
                    print(f"  结果: [未匹配] 未找到匹配的情绪")
            else:
                print(f"  结果: [失败] 分析失败")
        except Exception as e:
            print(f"  错误: {str(e)}")


def test_keyword_matching():
    """测试关键词匹配"""
    print("\n" + "="*80)
    print("[测试] 测试关键词匹配增强功能")
    print("="*80)
    
    test_cases = [
        ("今天心情特别好，感觉整个人都充满了活力", "开心"),
        ("今天心情很低落，感觉做什么都没意思", "难过"),
        ("明天有重要的考试，心里很紧张和焦虑", "焦虑"),
    ]
    
    print("\n[测试用例]")
    for i, (text, emotion_name) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 测试用例:")
        print(f"  文本: {text}")
        print(f"  情绪: {emotion_name}")
        
        try:
            result = SentimentLexicon.enhance_keyword_matching(text, emotion_name)
            
            if result:
                matched = result.get('matched', False)
                confidence = result.get('confidence', 0.0)
                intensity = result.get('intensity', 0.5)
                matched_keywords = result.get('matched_keywords', [])
                
                icon = "[匹配]" if matched else "[未匹配]"
                print(f"  结果: {icon}")
                print(f"  置信度: {confidence:.2f}")
                print(f"  强度: {intensity:.2f}")
                if matched_keywords:
                    print(f"  匹配的关键词: {', '.join(matched_keywords[:5])}")
            else:
                print(f"  结果: [失败] 匹配失败")
        except Exception as e:
            print(f"  错误: {str(e)}")


def main():
    """主函数"""
    print("="*80)
    print("[测试] 专业Sentiment词典功能测试")
    print("="*80)
    
    # 1. 测试词典加载
    lexicons = test_lexicon_loading()
    
    # 2. 测试情绪分析
    if lexicons:
        test_emotion_analysis()
        
        # 3. 测试关键词匹配
        test_keyword_matching()
    
    print("\n" + "="*80)
    print("[完成] 测试完成！")
    print("="*80)
    print("\n[提示] 使用说明:")
    print("1. 专业词典已集成到 llm_service.py 中")
    print("2. 关键词匹配会自动使用专业词典")
    print("3. analyze_emotion_with_lexicon 方法优先使用专业词典")
    print("4. 如果专业词典失败，会降级到基础关键词匹配")


if __name__ == '__main__':
    main()

