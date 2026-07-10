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
Hex64 训练数据自动生成器

从 feedback.json、rules.json 和 hexagrams.json 自动生成 QLoRA 微调所需
的训练数据，格式为 JSONL（每行一个 JSON 对象）。

使用方式：
    python src/training/prepare_data.py
    
输出：
    data/train_hex64.jsonl - 训练数据文件
"""

import json
import os
import sys
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

# Windows UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DataPreparer:
    """训练数据准备器"""
    
    def __init__(
        self,
        base_dir: Optional[str] = None
    ):
        """
        初始化数据准备器
        
        Args:
            base_dir: 项目根目录，默认为脚本所在目录的上级
        """
        if base_dir is None:
            base_dir = str(Path(__file__).parent.parent.parent)
        
        self.base_dir = Path(base_dir)
        self.feedback_file = self.base_dir / 'data' / 'feedback.json'
        self.rules_file = self.base_dir / 'data' / 'rules.json'
        self.hex_db_file = self.base_dir / 'data' / 'hexagrams.json'
        self.output_file = self.base_dir / 'data' / 'train_hex64.jsonl'
    
    def load_json(self, path: Path) -> List[Dict[str, Any]]:
        """安全加载 JSON 文件"""
        if not path.exists():
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return []
    
    def get_system_prompt(self) -> str:
        """生成系统提示词"""
        return """你是 HexLang Assistant，基于 Qwen3.5-9B + Hex64 符号引擎。
你必须严格遵守以下规则：
1. 收到用户输入后，先进行 Hex64 转码。
2. 回答必须包含两段：[回复] 和 [Hex64 溯源]。
3. [Hex64 溯源] 格式：卦名（二进制）+ 语义标签。
4. 严禁使用玄学术语，严禁预测未来，保持工程化语气。
5. 若涉及运维告警，需给出具体处置建议。"""
    
    def find_hexagram(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找卦象信息"""
        hex_db = self.load_json(self.hex_db_file)
        for hex_item in hex_db:
            if hex_item.get('name') == name:
                return hex_item
        return None
    
    def generate_from_feedback(self, feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """从单条反馈记录生成训练数据"""
        user_input = feedback.get('user_input', '')
        corrected_hex = feedback.get('target_hex', '')
        scene = feedback.get('scene', '')
        
        if not user_input or not corrected_hex:
            return None
        
        hex_info = self.find_hexagram(corrected_hex)
        if not hex_info:
            return None
        
        tags = hex_info.get('tags', [])
        bin_code = hex_info.get('bin', '')
        
        assistant_response = (
            f"[回复] 检测到{scene}场景下的信号：'{user_input}'。"
            f"根据 Hex64 符号映射，建议执行相应逻辑。\n"
            f"[Hex64 溯源：{corrected_hex}({bin_code})，"
            f"语义标签：{', '.join(tags)}]"
        )
        
        return {
            "messages": [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": assistant_response}
            ]
        }
    
    def generate_from_rules(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """从单条规则生成训练数据
        
        支持两种格式：
        1. 新格式 (induce_rules.py): {keyword, target_hex, support, confidence}
        2. 旧格式: {antecedents: {...}, consequents: {...}}
        """
        # 新格式：keyword/target_hex
        if 'keyword' in rule and 'target_hex' in rule:
            keyword = rule['keyword']
            hex_name = rule['target_hex']
            user_input = f"系统出现{keyword}错误，该如何处理？"
        
        # 旧格式：antecedents/consequents
        elif 'antecedents' in rule or 'consequents' in rule:
            antecedents = rule.get('antecedents', {})
            consequents = rule.get('consequents', {})
            
            if not antecedents or not consequents:
                return None
            
            hex_name = list(consequents.keys())[0] if isinstance(consequents, dict) else list(consequents)[0]
            
            if isinstance(antecedents, dict):
                keywords = list(antecedents.keys())
            else:
                keywords = list(antecedents)
            
            user_input = f"系统出现{'和'.join(keywords)}，该如何处理？"
        else:
            return None
        
        hex_info = self.find_hexagram(hex_name)
        if not hex_info:
            return None
        
        tags = hex_info.get('tags', [])
        bin_code = hex_info.get('bin', '')
        
        # 提取关键词用于回复
        if 'keyword' in rule:
            kw_display = rule['keyword']
        else:
            kw_display = ', '.join(keywords) if 'keywords' in dir() else ''
        
        assistant_response = (
            f"[回复] 识别到关键词：{kw_display}。"
            f"依据 Hex64 规则库，判定为{hex_name}卦象，"
            f"建议按{','.join(tags)}逻辑处置。\n"
            f"[Hex64 溯源：{hex_name}({bin_code})，"
            f"语义标签：{', '.join(tags)}]"
        )
        
        return {
            "messages": [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": assistant_response}
            ]
        }
    
    def generate_augmented_data(self) -> List[Dict[str, Any]]:
        """数据增强：基于现有卦象生成变体问题"""
        hex_db = self.load_json(self.hex_db_file)
        augmented_data = []
        
        for hex_info in hex_db:
            name = hex_info['name']
            tags = hex_info.get('tags', [])
            bin_code = hex_info.get('bin', '')
            
            # 针对每个标签生成一个问题
            for tag in tags[:3]:  # 只取前 3 个标签，避免数据过多
                user_input = f"在编程中，如何实现{tag}的功能？"
                assistant_response = (
                    f"[回复] {tag}是 Hex64 体系中{name}卦的核心语义。"
                    f"在工程实现上，建议封装对应的模块或函数。\n"
                    f"[Hex64 溯源：{name}({bin_code})，"
                    f"语义标签：{', '.join(tags)}]"
                )
                
                augmented_data.append({
                    "messages": [
                        {"role": "system", "content": self.get_system_prompt()},
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": assistant_response}
                    ]
                })
        
        return augmented_data
    
    def prepare(self, output_file: Optional[Path] = None) -> int:
        """
        准备训练数据
        
        Args:
            output_file: 输出文件路径，默认为 data/train_hex64.jsonl
            
        Returns:
            生成的训练数据条数
        """
        if output_file is None:
            output_file = self.output_file
        
        print("\n=== Hex64 训练数据准备 ===")
        print(f"基础目录: {self.base_dir}")
        
        # 1. 加载数据
        feedbacks = self.load_json(self.feedback_file)
        
        # 加载 rules.json（可能是字典格式）
        rules_raw = self.load_json(self.rules_file)
        if isinstance(rules_raw, dict) and 'rules' in rules_raw:
            rules = rules_raw['rules']
        else:
            rules = rules_raw if isinstance(rules_raw, list) else []
        
        print(f"反馈数据: {len(feedbacks)} 条")
        print(f"规则数据: {len(rules)} 条")
        
        # 2. 生成训练数据
        train_data = []
        
        # 从反馈生成（高质量）
        print("\n正在从反馈数据生成...")
        for feedback in feedbacks:
            conv = self.generate_from_feedback(feedback)
            if conv:
                train_data.append(conv)
        
        # 从规则生成（增强泛化）
        print("正在从规则数据生成...")
        for rule in rules:
            conv = self.generate_from_rules(rule)
            if conv:
                train_data.append(conv)
        
        # 数据增强（扩充规模）
        print("正在进行数据增强...")
        augmented_data = self.generate_augmented_data()
        train_data.extend(augmented_data)
        
        # 3. 打乱数据
        random.shuffle(train_data)
        
        # 4. 保存为 JSONL
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in train_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"\n[OK] 训练数据生成完毕！")
        print(f"   总数据量: {len(train_data)} 条")
        fb_count = sum(1 for _ in feedbacks if self.generate_from_feedback(_))
        rule_count = sum(1 for _ in rules if self.generate_from_rules(_))
        print(f"   反馈数据: {fb_count} 条")
        print(f"   规则数据: {rule_count} 条")
        print(f"   增强数据: {len(augmented_data)} 条")
        print(f"   输出文件: {output_file}")
        
        return len(train_data)


def main():
    """主函数"""
    preparer = DataPreparer()
    count = preparer.prepare()
    
    if count > 0:
        print(f"\n[INFO] 下一步：运行 python src/training/train_lora.py 开始微调")
    else:
        print(f"\n[WARN] 未生成任何数据，请检查 feedback.json 和 rules.json")


if __name__ == '__main__':
    main()
