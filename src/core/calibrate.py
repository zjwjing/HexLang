"""
Hex64 校准脚本

根据反馈数据自动校准卦象标签权重
用于反馈自修正机制

使用方式：
    python src/core/calibrate.py
    
功能：
1. 读取 feedback.json 中的修正记录
2. 统计高频修正模式
3. 更新 hexagrams.json 中的 scene_weights
4. 生成校准报告
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter


class Calibrator:
    """校准器 - 根据反馈数据更新卦象权重"""
    
    def __init__(
        self,
        feedback_file: Optional[str] = None,
        hex_db_path: Optional[str] = None
    ):
        """
        初始化校准器
        
        Args:
            feedback_file: 反馈文件路径
            hex_db_path: 六十四卦数据文件路径
        """
        if feedback_file is None:
            base_dir = Path(__file__).parent.parent.parent
            feedback_file = str(base_dir / 'data' / 'feedback.json')
        
        if hex_db_path is None:
            hex_db_path = str(base_dir / 'data' / 'hexagrams.json')
        
        self.feedback_file = feedback_file
        self.hex_db_path = hex_db_path
        
        # 加载数据
        self.feedbacks = self._load_feedbacks()
        self.hex_db = self._load_hex_db()
    
    def _load_feedbacks(self) -> List[Dict[str, Any]]:
        """加载反馈数据"""
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _load_hex_db(self) -> List[Dict[str, Any]]:
        """加载六十四卦数据"""
        with open(self.hex_db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_corrections(self) -> Dict[str, Any]:
        """
        分析修正模式
        
        Returns:
            分析报告
        """
        if not self.feedbacks:
            return {
                'total_corrections': 0,
                'by_scene': {},
                'by_input': {},
                'high_frequency_patterns': []
            }
        
        # 按场景统计
        scene_counter = Counter(f.get('scene', 'unknown') for f in self.feedbacks)
        
        # 按输入统计
        input_counter = Counter(f.get('user_input', '') for f in self.feedbacks)
        
        # 高频修正模式（同一输入出现 2 次以上）
        high_frequency = [
            {
                'input': input_text,
                'count': count,
                'corrections': [
                    f for f in self.feedbacks if f.get('user_input') == input_text
                ]
            }
            for input_text, count in input_counter.items()
            if count >= 2
        ]
        
        return {
            'total_corrections': len(self.feedbacks),
            'by_scene': dict(scene_counter),
            'by_input': dict(input_counter),
            'high_frequency_patterns': high_frequency
        }
    
    def calculate_weight_updates(self) -> Dict[str, float]:
        """
        计算权重更新建议
        
        Returns:
            卦名 -> 权重调整值的映射
        """
        corrections = self.analyze_corrections()
        high_freq = corrections.get('high_frequency_patterns', [])
        
        weight_updates = {}
        
        for pattern in high_freq:
            input_text = pattern['input']
            corrections_list = pattern['corrections']
            
            # 统计目标卦的多数投票
            target_counter = Counter(
                c.get('target_hex') for c in corrections_list
            )
            
            if target_counter:
                most_common_hex, count = target_counter.most_common(1)[0]
                weight_updates[most_common_hex] = count / len(corrections_list)
        
        return weight_updates
    
    def apply_calibrations(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        应用校准
        
        Args:
            dry_run: 是否仅模拟运行（不实际修改文件）
            
        Returns:
            校准报告
        """
        print("\n=== Hex64 校准报告 ===")
        print(f"时间: {datetime.now().isoformat()}")
        print(f"反馈总数: {len(self.feedbacks)}")
        
        # 分析修正模式
        analysis = self.analyze_corrections()
        print(f"\n修正分析:")
        print(f"  高频修正模式: {len(analysis['high_frequency_patterns'])} 个")
        
        if analysis['high_frequency_patterns']:
            for pattern in analysis['high_frequency_patterns'][:5]:
                print(f"    - {pattern['input']}: {pattern['count']} 次修正")
        
        # 计算权重更新
        weight_updates = self.calculate_weight_updates()
        print(f"\n权重更新建议:")
        
        if weight_updates:
            for hex_name, weight in weight_updates.items():
                print(f"  {hex_name}: +{weight:.2f}")
        else:
            print("  暂无足够数据进行校准")
        
        # 是否实际修改文件
        if not dry_run and weight_updates:
            print("\n⚠️  正在更新 hexagrams.json...")
            self._update_hex_db(weight_updates)
            print("✅ 校准完成")
        elif dry_run:
            print("\n💡 这是模拟运行，使用 --apply 参数实际应用校准")
        
        return {
            'feedbacks_count': len(self.feedbacks),
            'analysis': analysis,
            'weight_updates': weight_updates,
            'applied': not dry_run
        }
    
    def _update_hex_db(self, weight_updates: Dict[str, float]):
        """
        更新六十四卦数据文件
        
        Args:
            weight_updates: 卦名 -> 权重调整值
        """
        # 重新加载最新数据
        with open(self.hex_db_path, 'r', encoding='utf-8') as f:
            hex_db = json.load(f)
        
        # 更新权重
        for hex_item in hex_db:
            hex_name = hex_item['name']
            if hex_name in weight_updates:
                current_weight = hex_item.get('weight', 0.5)
                new_weight = min(1.0, current_weight + weight_updates[hex_name])
                hex_item['weight'] = round(new_weight, 2)
                print(f"  更新 {hex_name}: {current_weight} → {new_weight}")
        
        # 保存
        with open(self.hex_db_path, 'w', encoding='utf-8') as f:
            json.dump(hex_db, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hex64 校准工具')
    parser.add_argument(
        '--apply',
        action='store_true',
        help='实际应用校准（默认仅模拟）'
    )
    parser.add_argument(
        '--feedback-file',
        type=str,
        help='反馈文件路径'
    )
    parser.add_argument(
        '--hex-db-path',
        type=str,
        help='六十四卦数据文件路径'
    )
    
    args = parser.parse_args()
    
    calibrator = Calibrator(
        feedback_file=args.feedback_file,
        hex_db_path=args.hex_db_path
    )
    
    calibrator.apply_calibrations(dry_run=not args.apply)


if __name__ == '__main__':
    main()
