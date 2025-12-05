#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试DeepSeek情绪识别准确度
提供测试用例，评估识别准确率
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app_2 import create_app
from app_2.service.llm_service import LLMService


# 测试用例
TEST_CASES = [
    # (文本内容, 期望情绪, 难度)
    ("今天天气真好，心情也不错！", "开心", "简单"),
    ("工作压力很大，总是睡不好，很焦虑", "焦虑", "简单"),
    ("一个人在家，感觉好孤独", "孤独", "简单"),
    ("感谢朋友的帮助，真的很感动", "感动", "简单"),
    ("今天考试考得很好，太开心了！", "开心", "简单"),
    
    ("最近总是担心未来，感觉压力很大", "焦虑", "中等"),
    ("虽然很累，但是感觉很充实", "开心", "中等"),  # 转折句式：转折后是情绪（充实）→ 开心
    ("看到别人幸福，我也感到开心", "开心", "中等"),
    ("虽然有点难过，但还是要坚持下去", "难过", "中等"),
    
    ("今天发生了很多事情，心情很复杂", "待定", "困难"),  # 复杂情绪
    ("又开心又难过，不知道是什么感觉", "待定", "困难"),  # 混合情绪
    ("没有什么特别的感觉，就是很平静", "平静", "中等"),
    
    # 隐含情绪
    ("最近总是失眠，身体也感觉很累", "疲惫", "中等"),
    ("虽然表面平静，但内心还是有点不安", "焦虑", "困难"),
    
    # 负面情绪
    ("被人误解了，真的很生气", "愤怒", "简单"),
    ("感觉自己被抛弃了，很难过", "难过", "简单"),
    
    # 正面情绪
    ("期待明天的旅行，感觉很兴奋", "兴奋", "简单"),
    ("希望这次能成功，真的很期待", "期待", "简单"),
    
    # 转折句式测试
    ("虽然很累，但是感觉很充实", "开心", "中等"),  # 转折后是情绪（充实）→ 开心
    ("虽然有点难过，但还是要坚持下去", "难过", "中等"),  # 转折后是行为（坚持）→ 识别转折前的情绪：难过
    ("虽然表面平静，但内心还是有点不安", "焦虑", "困难"),  # 转折后是情绪（不安）→ 焦虑
    ("尽管工作很辛苦，但还是很有成就感", "开心", "中等"),  # 转折后是情绪（成就感）→ 开心
    ("即使很累，也觉得很值得", "开心", "中等"),  # 转折后是情绪（值得）→ 开心
    ("虽然遇到困难，但是我会克服的", "期待", "中等"),  # 转折后是行为（克服）→ 识别为期待（积极态度）
    ("虽然很焦虑，但还是会努力面对", "焦虑", "困难"),  # 转折后是行为（面对）→ 识别转折前的情绪：焦虑
    ("虽然今天下雨，但心情还是很好", "开心", "中等"),  # 转折后是情绪（很好）→ 开心
    
    # 语气词测试
    ("今天真的太好啦！", "开心", "简单"),  # 语气词"啦"和强度词"真的"、"太" → 强烈的开心
    ("我好难过啊...", "难过", "简单"),  # 语气词"啊"和强度词"好" → 较强的难过
    ("太焦虑了...", "焦虑", "简单"),  # 强度词"太" → 很强的焦虑
    ("特别感动呢！", "感动", "简单"),  # 强度词"特别"和语气词"呢" → 强烈的感动
    ("超级开心呀！", "开心", "简单"),  # 强度词"超级"和语气词"呀" → 强烈的开心
    ("真的很生气！", "愤怒", "简单"),  # 强度词"真的" → 强烈的愤怒
    ("好期待啊！", "期待", "简单"),  # 强度词"好"和语气词"啊" → 较强的期待
    ("有点累了呢", "疲惫", "简单"),  # 强度词"有点"和语气词"呢" → 轻度的疲惫

    # 爬取的专业测试数据
    ("今天心情特别好，感觉整个人都充满了活力", "开心", "简单"),
    ("看到了期待已久的电影，太开心了", "开心", "简单"),
    ("和朋友一起吃饭聊天，真的很愉快", "开心", "简单"),
    ("收到了心仪的礼物，特别感动和开心", "开心", "简单"),
    ("今天工作顺利，心情舒畅", "开心", "简单"),
    ("今天心情很低落，感觉做什么都没意思", "难过", "简单"),
    ("失去了重要的东西，很难过", "难过", "简单"),
    ("看到悲伤的电影，忍不住流泪", "难过", "简单"),
    ("一个人在家，感觉很孤独和难过", "难过", "简单"),
    ("遇到了挫折，心情很沮丧", "难过", "简单"),
    ("明天有重要的考试，心里很紧张和焦虑", "焦虑", "简单"),
    ("工作压力太大，总是担心做不好", "焦虑", "简单"),
    ("最近总是失眠，感觉很焦虑", "焦虑", "简单"),
    ("面对不确定的未来，心里很不安", "焦虑", "简单"),
    ("很多任务要完成，感觉压力很大", "焦虑", "简单"),
    ("遇到不公平的事情，非常愤怒", "愤怒", "简单"),
    ("被别人冒犯，心里很不满", "愤怒", "简单"),
    ("看到不合理的现象，很恼火", "愤怒", "简单"),
    ("今天没什么特别的事，心情很平静", "平静", "简单"),
    ("在图书馆看书，感觉很宁静", "平静", "简单"),
    ("独自一人在海边，内心很平静", "平静", "简单"),
    ("做完冥想后，心情变得很平静", "平静", "简单"),
    ("连续工作了好几天，感觉很累", "疲惫", "简单"),
    ("今天运动过度，身体很疲惫", "疲惫", "简单"),
    ("熬夜到很晚，早上起床很累", "疲惫", "简单"),
    ("处理了很多事情，身心俱疲", "疲惫", "简单"),
    ("看到朋友的帮助，真的很感动", "感动", "简单"),
    ("听到了温暖的话语，心里很感动", "感动", "简单"),
    ("收到了意外的关心，特别感动", "感动", "简单"),
    ("看到了感人的故事，眼泪止不住", "感动", "简单"),
    ("即将要去旅行，心情很兴奋", "兴奋", "简单"),
    ("听到了好消息，非常激动", "兴奋", "简单"),
    ("完成了困难的任务，很兴奋", "兴奋", "简单"),
    ("看到了精彩的表演，热情高涨", "兴奋", "简单"),
    ("期待着明天的旅行", "期待", "简单"),
    ("希望能成功完成这个项目", "期待", "简单"),
    ("盼望着和朋友见面", "期待", "简单"),
    ("对未来的计划充满期待", "期待", "简单"),
    ("一个人在家，感觉很孤独", "孤独", "简单"),
    ("在陌生的城市，没有人陪伴", "孤独", "简单"),
    ("朋友们都有事，自己很孤单", "孤独", "简单"),
    ("深夜一个人，内心很寂寞", "孤独", "简单"),
    ("今天考试，心情很开心", "开心", "简单"),
    ("今天考试，心情很特别开心", "开心", "简单"),
    ("今天面试，心情很开心", "开心", "简单"),
    ("今天面试，心情很特别开心", "开心", "简单"),
    ("考试，感觉特别愉快", "开心", "简单"),
    ("考试，感觉特别特别愉快", "开心", "简单"),
    ("面试，感觉特别愉快", "开心", "简单"),
]


def test_single_case(text, expected, difficulty):
    """测试单个用例（使用原有方法）"""
    try:
        result = LLMService.analyze_emotion_from_text(text)
        match = result == expected
        icon = "✅" if match else "❌"
        
        status = "正确" if match else "错误"
        color = "绿色" if match else "红色"
        
        print(f"{icon} [{difficulty:^4}] {status:^4} | 文本: {text[:40]:<40} | 期望: {expected:<6} | 实际: {result:<6}")
        
        return match
    except Exception as e:
        print(f"❌ [错误] 测试失败 | 文本: {text[:40]} | 错误: {str(e)[:30]}")
        return False


def test_all_cases():
    """测试所有用例"""
    print("=" * 100)
    print("DeepSeek 情绪识别准确度测试")
    print("=" * 100)
    print()
    
    results = {
        'total': 0,
        'correct': 0,
        'wrong': 0,
        'by_difficulty': {
            '简单': {'total': 0, 'correct': 0},
            '中等': {'total': 0, 'correct': 0},
            '困难': {'total': 0, 'correct': 0}
        }
    }
    
    print(f"{'难度':^6} | {'状态':^6} | {'文本内容':<40} | {'期望':<6} | {'实际':<6}")
    print("-" * 100)
    
    for text, expected, difficulty in TEST_CASES:
        results['total'] += 1
        results['by_difficulty'][difficulty]['total'] += 1
        
        match = test_single_case(text, expected, difficulty)
        
        if match:
            results['correct'] += 1
            results['by_difficulty'][difficulty]['correct'] += 1
        else:
            results['wrong'] += 1
    
    print()
    print("=" * 100)
    print("测试结果统计")
    print("=" * 100)
    
    # 总体准确度
    accuracy = (results['correct'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\n总体准确度: {results['correct']}/{results['total']} = {accuracy:.2f}%")
    
    # 按难度统计
    print(f"\n按难度统计:")
    for difficulty in ['简单', '中等', '困难']:
        diff_results = results['by_difficulty'][difficulty]
        if diff_results['total'] > 0:
            diff_accuracy = (diff_results['correct'] / diff_results['total'] * 100)
            print(f"  {difficulty:^6}: {diff_results['correct']}/{diff_results['total']} = {diff_accuracy:.2f}%")
    
    # 错误分析
    if results['wrong'] > 0:
        print(f"\n❌ 错误用例 ({results['wrong']} 个):")
        for text, expected, difficulty in TEST_CASES:
            result = LLMService.analyze_emotion_from_text(text)
            if result != expected:
                print(f"  文本: {text[:50]}...")
                print(f"  期望: {expected}, 实际: {result}")
                print()
    
    return results


def test_custom_text(text):
    """测试自定义文本"""
    print(f"\n测试文本: {text}")
    print("-" * 80)
    
    result = LLMService.analyze_emotion_from_text(text)
    print(f"识别结果: {result}")
    
    # 同时显示关键词匹配结果（对比）
    keyword_result = LLMService._match_emotion_by_keywords(text)
    print(f"关键词匹配: {keyword_result}")
    
    if result == keyword_result:
        print("✅ DeepSeek和关键词匹配结果一致")
    else:
        print("⚠️  DeepSeek和关键词匹配结果不一致")


def benchmark_performance():
    """性能基准测试"""
    import time
    
    print("\n" + "=" * 80)
    print("性能基准测试")
    print("=" * 80)
    
    # 选择几个测试用例
    test_samples = TEST_CASES[:5]
    
    times = []
    for text, expected, difficulty in test_samples:
        start_time = time.time()
        result = LLMService.analyze_emotion_from_text(text)
        elapsed = time.time() - start_time
        times.append(elapsed)
        print(f"文本: {text[:30]:<30} | 耗时: {elapsed:.2f}s | 结果: {result}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n平均耗时: {avg_time:.2f}s")
        print(f"最快: {min(times):.2f}s")
        print(f"最慢: {max(times):.2f}s")


def test_enhanced_single_case(text, expected, difficulty):
    """测试增强版单个用例（使用结构化输出）"""
    try:
        result = LLMService.analyze_emotion_enhanced(text)
        if result is None:
            print(f"❌ 文本: {text[:50]}...")
            print(f"   结果: None")
            return False, None
        
        label = result.get('label')
        match = label == expected
        icon = "✅" if match else "❌"
        
        status = "正确" if match else "错误"
        score = result.get('score', 0.0)
        confidence = result.get('confidence', 0.0)
        intensity = result.get('intensity', 0.0)
        method = result.get('method', 'unknown')
        
        print(f"{icon} {status} ({difficulty})")
        print(f"   文本: {text[:50]}...")
        print(f"   期望: {expected}")
        print(f"   实际: {label}")
        if not match:
            print(f"   详细: score={score:.2f}, confidence={confidence:.2f}, intensity={intensity:.2f}, method={method}")
        
        return match, result
    except Exception as e:
        print(f"❌ 错误 ({difficulty})")
        print(f"   文本: {text[:50]}...")
        print(f"   错误: {str(e)}")
        return False, None


def test_batch_analysis():
    """测试批量分析功能"""
    print("\n" + "="*80)
    print("📊 测试批量情绪分析")
    print("="*80)
    
    test_texts = [
        "今天天气真好，心情也不错！",
        "工作压力很大，总是睡不好",
        "一个人在家，感觉好孤独",
        "感谢朋友的帮助，真的很感动",
        "今天考试考得很好，太开心了！"
    ]
    
    print(f"\n待分析文本 ({len(test_texts)}条):")
    for i, text in enumerate(test_texts, 1):
        print(f"  {i}. {text}")
    
    print(f"\n开始批量分析...")
    results = LLMService.analyze_emotion_batch(test_texts, max_concurrent=3)
    
    print(f"\n分析结果:")
    print("-"*80)
    for i, (text, result) in enumerate(zip(test_texts, results), 1):
        if result:
            label = result.get('label', 'N/A')
            score = result.get('score', 0.0)
            confidence = result.get('confidence', 0.0)
            method = result.get('method', 'unknown')
            print(f"{i}. 文本: {text[:40]}...")
            print(f"   结果: {label} | 分值: {score:.2f} | 置信度: {confidence:.2f} | 方法: {method}")
        else:
            print(f"{i}. 文本: {text[:40]}...")
            print(f"   结果: 分析失败")
        print()


def test_enhanced_analysis():
    """测试增强版分析功能（结构化输出）"""
    print("\n" + "="*80)
    print("🚀 测试增强版情绪分析（结构化输出）")
    print("="*80)
    
    test_cases = [
        ("今天真的太好啦！", "开心"),
        ("我好难过啊...", "难过"),
        ("太焦虑了...", "焦虑"),
        ("特别感动呢！", "感动"),
        ("虽然很累，但是感觉很充实", "开心"),
    ]
    
    correct_count = 0
    total_count = len(test_cases)
    
    for text, expected in test_cases:
        match, result = test_enhanced_single_case(text, expected, "增强版")
        if match:
            correct_count += 1
        print()
    
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    print("-"*80)
    print(f"增强版分析准确率: {correct_count}/{total_count} ({accuracy:.1f}%)")
    print("="*80)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        import sys
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == 'test':
                # 运行所有测试用例
                test_all_cases()
                
            elif command == 'custom' and len(sys.argv) > 2:
                # 测试自定义文本
                text = ' '.join(sys.argv[2:])
                test_custom_text(text)
                
            elif command == 'benchmark':
                # 性能测试
                benchmark_performance()
                
            elif command == 'enhanced':
                # 增强版测试（结构化输出）
                test_enhanced_analysis()
                
            elif command == 'batch':
                # 批量测试
                test_batch_analysis()
                
            else:
                print("用法:")
                print("  python scripts/test_deepseek_accuracy.py test              # 运行所有测试用例")
                print("  python scripts/test_deepseek_accuracy.py custom <文本>      # 测试自定义文本")
                print("  python scripts/test_deepseek_accuracy.py benchmark         # 性能基准测试")
                print("  python scripts/test_deepseek_accuracy.py enhanced          # 增强版测试（结构化输出）")
                print("  python scripts/test_deepseek_accuracy.py batch             # 批量分析测试")
                print("\n示例:")
                print("  python scripts/test_deepseek_accuracy.py test")
                print("  python scripts/test_deepseek_accuracy.py custom \"今天心情很好\"")
                print("  python scripts/test_deepseek_accuracy.py benchmark")
                print("  python scripts/test_deepseek_accuracy.py enhanced")
                print("  python scripts/test_deepseek_accuracy.py batch")
        else:
            # 默认运行所有测试
            test_all_cases()

