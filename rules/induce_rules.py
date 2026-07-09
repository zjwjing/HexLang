"""
Hex64 规则归纳引擎

从反馈数据中挖掘关键词与卦象的高频关联
用于构建“规则优先”的快速匹配层，减少 AI 推理延迟

使用方式：
    python rules/induce_rules.py
    
输出：
    data/rules.json - 包含高频关联规则
"""

import json
import os
import re
import sys
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from pathlib import Path


class RuleInducer:
    """规则归纳器 - 从反馈数据中发现模式"""
    
    def __init__(
        self,
        feedback_file: str = None,
        output_file: str = None
    ):
        """
        初始化规则归纳器
        
        Args:
            feedback_file: 反馈数据路径
            output_file: 规则输出路径
        """
        # 设置控制台编码为 UTF-8（Windows 兼容）
        if os.name == 'nt':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        
        base_dir = Path(__file__).parent.parent
        
        if feedback_file is None:
            feedback_file = base_dir / 'data' / 'feedback.json'
        
        if output_file is None:
            output_file = base_dir / 'data' / 'rules.json'
        
        self.feedback_file = feedback_file
        self.output_file = output_file
        
        # 加载反馈数据
        self.feedbacks = self._load_feedbacks()
        
        # 预定义的工程关键词映射（辅助规则发现）
        self.keyword_categories = {
            'error': ['error', 'fail', 'exception', 'crash', 'timeout'],
            'deploy': ['deploy', 'release', 'publish', 'build'],
            'system': ['system', 'init', 'boot', 'start', 'restart'],
            'network': ['connect', 'disconnect', 'network', 'http', 'api'],
            'data': ['save', 'load', 'cache', 'database', 'query']
        }
    
    def _load_feedbacks(self) -> List[Dict[str, Any]]:
        """加载反馈数据"""
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            关键词列表
        """
        # 简单分词：提取英文单词和中文词语
        english_words = re.findall(r'[a-zA-Z_]+', text.lower())
        
        # 检查是否匹配预定义类别
        matched_categories = []
        for category, keywords in self.keyword_categories.items():
            if any(kw in text.lower() for kw in keywords):
                matched_categories.append(category)
        
        return english_words + matched_categories
    
    def induce_rules(
        self,
        min_support: int = 2,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        归纳规则
        
        Args:
            min_support: 最小支持度（出现次数）
            min_confidence: 最小置信度
            
        Returns:
            规则列表
        """
        if len(self.feedbacks) < min_support:
            print(f"⚠️  反馈数据不足（需要{min_support}条，当前{len(self.feedbacks)}条）")
            return []
        
        # 统计：关键词 -> [目标卦]
        keyword_to_targets = defaultdict(list)
        
        for feedback in self.feedbacks:
            if not feedback.get('parsed'):
                continue
            
            user_input = feedback.get('user_input', '')
            target_hex = feedback.get('target_hex', '')
            
            if not user_input or not target_hex:
                continue
            
            keywords = self.extract_keywords(user_input)
            for kw in keywords:
                keyword_to_targets[kw].append(target_hex)
        
        # 计算支持度和置信度
        rules = []
        
        for keyword, targets in keyword_to_targets.items():
            support = len(targets)
            
            if support < min_support:
                continue
            
            # 多数投票确定主要关联的卦
            target_counter = Counter(targets)
            most_common_target, count = target_counter.most_common(1)[0]
            
            confidence = count / support
            
            if confidence >= min_confidence:
                rules.append({
                    'keyword': keyword,
                    'target_hex': most_common_target,
                    'support': support,
                    'confidence': round(confidence, 2),
                    'all_targets': dict(target_counter)
                })
        
        # 按置信度排序
        rules.sort(key=lambda x: x['confidence'], reverse=True)
        
        return rules
    
    def generate_training_data(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于规则生成训练数据（用于 LoRA 微调）
        
        Args:
            rules: 归纳出的规则列表
            
        Returns:
            训练数据列表（SFT 格式）
        """
        training_data = []
        
        for rule in rules:
            keyword = rule['keyword']
            target_hex = rule['target_hex']
            
            # 构造一条训练样本
            sample = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"分析输入: {keyword}"
                    },
                    {
                        "role": "assistant",
                        "content": f"[Hex64溯源] {target_hex}\n根据历史反馈，'{keyword}'通常对应{target_hex}。"
                    }
                ]
            }
            training_data.append(sample)
        
        return training_data
    
    def save_rules(self, rules: List[Dict[str, Any]]):
        """
        保存规则到文件
        
        Args:
            rules: 规则列表
        """
        output_data = {
            'version': '1.0',
            'generated_at': __import__('datetime').datetime.now().isoformat(),
            'total_rules': len(rules),
            'rules': rules
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 已保存 {len(rules)} 条规则到 {self.output_file}")
    
    def run(self, min_support: int = 2, min_confidence: float = 0.7):
        """
        执行完整的规则归纳流程
        
        Args:
            min_support: 最小支持度
            min_confidence: 最小置信度
        """
        print("\n=== Hex64 规则归纳 ===")
        print(f"反馈数据: {len(self.feedbacks)} 条")
        print(f"参数: min_support={min_support}, min_confidence={min_confidence}\n")
        
        # 1. 归纳规则
        rules = self.induce_rules(min_support, min_confidence)
        
        if not rules:
            print("⚠️  未找到符合条件的规则")
            return
        
        print(f"发现 {len(rules)} 条规则:\n")
        
        for i, rule in enumerate(rules[:10], 1):  # 显示前 10 条
            print(f"{i}. [{rule['confidence']*100:.0f}%] '{rule['keyword']}' → {rule['target_hex']}")
            print(f"   支持度: {rule['support']} 次")
        
        # 2. 保存规则
        self.save_rules(rules)
        
        # 3. 生成训练数据
        training_data = self.generate_training_data(rules)
        
        if training_data:
            train_file = self.output_file.parent / 'train_hex64.json'
            with open(train_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 已生成 {len(training_data)} 条训练数据: {train_file}")


def main():
    """主函数"""
    inducer = RuleInducer()
    inducer.run()


if __name__ == '__main__':
    main()
