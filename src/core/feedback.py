"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Hex64 反馈管理系统

记录用户修正反馈，用于：
1. 标签自修正（累积 3 次同输入修正 → 更新 hexagrams.json）
2. 训练数据生成（为 LoRA 微调准备数据）
3. 规则归纳（从反馈中发现高频关联）

使用方式：
    from src.core.feedback import FeedbackManager
    
    manager = FeedbackManager()
    manager.submit_feedback("timeout_error", "天水讼", "泽雷随", "ops")
    feedbacks = manager.get_feedbacks()
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter


class FeedbackManager:
    """反馈管理器 - 记录和存储用户修正反馈"""
    
    def __init__(self, feedback_file: Optional[str] = None):
        """
        初始化反馈管理器
        
        Args:
            feedback_file: 反馈数据存储路径
                          默认为 data/feedback.json
        """
        if feedback_file is None:
            base_dir = Path(__file__).parent.parent.parent
            feedback_file = str(base_dir / 'data' / 'feedback.json')
        
        self.feedback_file = feedback_file
        self._ensure_feedback_file()
    
    def _ensure_feedback_file(self):
        """确保反馈文件存在"""
        if not os.path.exists(self.feedback_file):
            # 创建空反馈文件
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def submit_feedback(
        self,
        user_input: str,
        original_hex: str,
        target_hex: str,
        scene: str,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        提交反馈
        
        Args:
            user_input: 用户输入文本
            original_hex: 原卦名（模型输出的）
            target_hex: 目标卦名（用户期望的）
            scene: 场景描述
            confidence: 置信度（0-1，默认 1.0）
            
        Returns:
            反馈条目
        """
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'original_hex': original_hex,
            'target_hex': target_hex,
            'scene': scene,
            'confidence': confidence,
            'parsed': True
        }
        
        # 加载现有反馈
        feedbacks = self.load_feedbacks()
        
        # 添加新反馈
        feedbacks.append(feedback_entry)
        
        # 保存
        self.save_feedbacks(feedbacks)
        
        return feedback_entry
    
    def load_feedbacks(self) -> List[Dict[str, Any]]:
        """
        加载所有反馈
        
        Returns:
            反馈列表
        """
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_feedbacks(self, feedbacks: List[Dict[str, Any]]):
        """
        保存反馈列表
        
        Args:
            feedbacks: 反馈列表
        """
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)
    
    def get_feedbacks_by_scene(self, scene: str) -> List[Dict[str, Any]]:
        """
        按场景获取反馈
        
        Args:
            scene: 场景名称
            
        Returns:
            该场景下的反馈列表
        """
        feedbacks = self.load_feedbacks()
        return [f for f in feedbacks if f.get('scene') == scene]
    
    def get_feedbacks_by_input(self, user_input: str) -> List[Dict[str, Any]]:
        """
        按输入文本获取反馈
        
        Args:
            user_input: 用户输入
            
        Returns:
            匹配该输入的反馈列表
        """
        feedbacks = self.load_feedbacks()
        return [f for f in feedbacks if f.get('user_input') == user_input]
    
    def get_correction_stats(self) -> Dict[str, Any]:
        """
        获取修正统计信息
        
        Returns:
            统计字典
        """
        feedbacks = self.load_feedbacks()
        
        if not feedbacks:
            return {
                'total': 0,
                'by_scene': {},
                'by_input': {},
                'top_corrections': []
            }
        
        # 按场景统计
        scene_counter = Counter(f.get('scene', 'unknown') for f in feedbacks)
        
        # 按输入统计
        input_counter = Counter(f.get('user_input', '') for f in feedbacks)
        
        # 高频修正（同一输入出现 2 次以上）
        top_corrections = [
            {'input': input, 'count': count}
            for input, count in input_counter.most_common(10)
            if count >= 2
        ]
        
        return {
            'total': len(feedbacks),
            'by_scene': dict(scene_counter),
            'by_input': dict(input_counter),
            'top_corrections': top_corrections
        }
    
    def should_auto_correct(self, user_input: str, threshold: int = 3) -> bool:
        """
        检查是否应该自动修正标签
        
        Args:
            user_input: 用户输入
            threshold: 触发自动修正的阈值（默认 3 次）
            
        Returns:
            是否应该自动修正
        """
        feedbacks = self.get_feedbacks_by_input(user_input)
        return len(feedbacks) >= threshold
    
    def get_correction_suggestion(self, user_input: str) -> Optional[str]:
        """
        获取修正建议（多数投票）
        
        Args:
            user_input: 用户输入
            
        Returns:
            目标卦名，如果没有足够反馈则返回 None
        """
        feedbacks = self.get_feedbacks_by_input(user_input)
        
        if not feedbacks:
            return None
        
        # 多数投票
        target_counter = Counter(f.get('target_hex') for f in feedbacks)
        most_common = target_counter.most_common(1)
        
        return most_common[0][0] if most_common else None


# 便捷函数
def submit_feedback(
    user_input: str,
    original_hex: str,
    target_hex: str,
    scene: str,
    feedback_file: Optional[str] = None
) -> Dict[str, Any]:
    """快速提交反馈"""
    manager = FeedbackManager(feedback_file)
    return manager.submit_feedback(user_input, original_hex, target_hex, scene)


if __name__ == '__main__':
    # 测试反馈管理
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)
    
    manager = FeedbackManager()
    
    print("=== Hex64 反馈管理系统测试 ===\n")
    
    # 提交测试反馈
    test_feedbacks = [
        ("timeout_error", "天水讼", "泽雷随", "ops"),
        ("deploy_production", "地天泰", "火天大有", "devops"),
        ("timeout_error", "天水讼", "泽雷随", "ops"),  # 重复反馈
        ("system_init", "火风鼎", "坤为地", "system"),
    ]
    
    print("提交测试反馈...")
    for user_input, original, target, scene in test_feedbacks:
        manager.submit_feedback(user_input, original, target, scene)
        print(f"  OK {user_input}: {original} -> {target} ({scene})")
    
    print("\n反馈统计:")
    stats = manager.get_correction_stats()
    print(f"  总反馈数: {stats['total']}")
    print(f"  按场景: {stats['by_scene']}")
    print(f"  高频修正: {stats['top_corrections']}")
    
    print("\n修正建议:")
    suggestion = manager.get_correction_suggestion("timeout_error")
    print(f"  timeout_error -> {suggestion}")
