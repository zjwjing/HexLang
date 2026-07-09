"""
Hex64 编码器 - 核心转码模块

将任意输入文本映射到六十四卦特征向量
采用确定性算法（DJB2 哈希），不涉及任何玄学预测
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path


class Hex64Encoder:
    """Hex64 转码器 - 将文本映射到六十四卦特征"""
    
    def __init__(self, hex_db_path: Optional[str] = None):
        """
        初始化编码器
        
        Args:
            hex_db_path: 六十四卦数据文件路径
                         默认为 data/hexagrams.json
        """
        if hex_db_path is None:
            # 自动定位 data/hexagrams.json
            hex_db_path = str(Path(__file__).parent.parent.parent / 'data' / 'hexagrams.json')
        
        with open(hex_db_path, 'r', encoding='utf-8') as f:
            self.hex_db = json.load(f)
        
        # 构建 bin -> hexagram 映射（O(1) 查找）
        self.bin_to_hex = {hex_item['bin']: hex_item for hex_item in self.hex_db}
        
        # 构建 name -> hexagram 映射
        self.name_to_hex = {hex_item['name']: hex_item for hex_item in self.hex_db}
        
        # 标签到操作码映射（从 hex64_full.json 加载）
        full_db_path = str(Path(__file__).parent.parent.parent / 'data' / 'hex64_full.json')
        with open(full_db_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
            self.tag_to_op = full_data.get('tagToOp', {})
            
        # 爻权重数据（从 hex64_full.json 加载）
        self.yao_weights_db = {}
        for hex_item in full_data.get('hexagrams', []):
            if 'yao_weights' in hex_item and len(hex_item['yao_weights']) == 6:
                self.yao_weights_db[hex_item['bin']] = hex_item['yao_weights']
    
    def _djb2_hash(self, input_str: str) -> int:
        """
        DJB2 哈希算法（与 JavaScript 版本一致）
        
        Args:
            input_str: 输入字符串
            
        Returns:
            哈希值（32位无符号整数）
        """
        h = 5381
        for char in input_str:
            h = ((h << 5) + h + ord(char)) & 0xFFFFFFFF
        return h
    
    def _compute_inter_hex(self, bits: List[int]) -> Dict[str, Any]:
        """
        计算互卦（取中间四爻组成新卦）
        
        互卦逻辑：
        - 本卦六爻：[初, 二, 三, 四, 五, 上]
        - 互卦下卦 = 二、三、四爻（bits[1:4]）
        - 互卦上卦 = 三、四、五爻（bits[2:5]）
        - 互卦完整 = 下卦 + 上卦 = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]]
        
        这类似于 CNN 的局部感受野，捕捉事物的中间过程。
        
        Args:
            bits: 本卦六爻二进制列表
            
        Returns:
            互卦信息字典
        """
        # 互卦二进制：下卦（二三四）+ 上卦（三四五）
        inter_bits = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]]
        inter_bin_str = ''.join(str(b) for b in inter_bits)
        
        # 查找互卦数据
        inter_hex_data = self.bin_to_hex.get(inter_bin_str)
        
        if inter_hex_data:
            # 获取互卦的爻权重（从 yao_weights_db 加载）
            inter_yao_weights = self.yao_weights_db.get(inter_bin_str, [0.5] * 6)
            # 计算互卦加权特征
            inter_feature = [b * w for b, w in zip(inter_bits, inter_yao_weights)]
            
            return {
                'is_present': True,
                'binary': inter_bin_str,
                'hex_name': inter_hex_data['name'],
                'pinyin': inter_hex_data.get('pinyin', ''),
                'english': inter_hex_data.get('en', ''),
                'tags': inter_hex_data.get('tags', []),
                'weight': inter_hex_data.get('weight', 0.5),
                'yao_weights': inter_yao_weights,
                'feature_vector': inter_feature,
                'explanation': f"互卦：{inter_hex_data['name']}（中间过程特征）"
            }
        else:
            return {'is_present': False}
    
    def encode(self, input_str: str, include_details: bool = True) -> Dict[str, Any]:
        """
        将输入字符串编码为 Hex64 卦特征（增强版）
        
        新增特性：
        1. 爻级加权特征向量：bit[i] * yao_weights[i]
        2. 互卦分析：提取中间过程特征（12维上下文）
        3. 思维链提示：包含爻位分析引导
        
        Args:
            input_str: 输入文本
            include_details: 是否包含详细信息（拼音、英文等）
            
        Returns:
            结构化编码结果
        """
        if not input_str or not isinstance(input_str, str):
            raise ValueError("输入必须是非空字符串")
        
        # 计算哈希并映射到 0-63
        hash_val = self._djb2_hash(input_str)
        idx = hash_val % 64
        bin_code = format(idx, '06b')
        
        # 查找卦数据
        hex_data = self.bin_to_hex.get(bin_code)
        if not hex_data:
            raise RuntimeError(f"未找到二进制 {bin_code} 对应的卦数据")
        
        # 基础二进制位
        bits = [int(bit) for bit in bin_code]
        
        # === 改进一：爻级加权特征向量 ===
        yao_weights = self.yao_weights_db.get(bin_code)
        if yao_weights and len(yao_weights) == 6:
            # 使用爻权重：每个爻位有不同的重要性
            feature_vec = [b * w for b, w in zip(bits, yao_weights)]
        else:
            # 降级：无爻权重时使用统一权重
            feature_vec = bits[:]
        
        # === 基础 GPIO 信号 ===
        control_signal = ['ON' if bit == 1 else 'OFF' for bit in bits]
        
        # === 操作码列表 ===
        ops = []
        for tag in hex_data.get('tags', []):
            op = self.tag_to_op.get(tag, tag.upper())
            if op not in ops:
                ops.append(op)
        
        # 确保 yao_weights 始终存在（用于输出）
        if not yao_weights or len(yao_weights) != 6:
            yao_weights = [hex_data.get('weight', 0.5)] * 6
        
        # === 爻位分析（用于思维链） ===
        yao_analysis = []
        yao_names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
        for i, (bit, name) in enumerate(zip(bits, yao_names)):
            yao_type = '阳' if bit == 1 else '阴'
            weight = yao_weights[i]
            yao_analysis.append(f"{name}={yao_type}(w={weight:.2f})")
        
        result = {
            'input': input_str,
            'index': idx,
            'binary': bin_code,
            'hex_name': hex_data['name'],
            'tags': hex_data.get('tags', []),
            'weight': hex_data.get('weight', 0.5),
            'feature_vector': feature_vec,
            'control_signal': control_signal,
            'operations': ops,
            'yao_weights': yao_weights,
            'yao_analysis': yao_analysis,
        }
        
        # === 改进二：互卦特征 ===
        inter_hex = self._compute_inter_hex(bits)
        result['inter_hex'] = inter_hex
        
        # 组合特征：本卦 + 互卦 = 12维上下文
        if inter_hex.get('is_present'):
            result['combined_feature'] = feature_vec + inter_hex['feature_vector']
            result['combined_dim'] = 12
        else:
            result['combined_feature'] = feature_vec
            result['combined_dim'] = 6
        
        if include_details:
            result.update({
                'pinyin': hex_data.get('pinyin', ''),
                'english': hex_data.get('en', ''),
                'category': hex_data.get('category', ''),
                'pseudo_code': f"HEX({hex_data['name']}) {{ {'; '.join(ops)}; }}",
                'explanation': f"对应卦象：{hex_data['name']}，语义标签：{','.join(hex_data['tags'])}",
                'position_encoding': '爻位权重已注入特征向量，Qwen可感知爻位重要性差异'
            })
        
        return result
    
    def batch_encode(self, inputs: List[str], include_details: bool = True) -> List[Dict[str, Any]]:
        """
        批量编码
        
        Args:
            inputs: 输入文本列表
            include_details: 是否包含详细信息
            
        Returns:
            编码结果列表
        """
        return [self.encode(input_str, include_details) for input_str in inputs]
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        返回 AI 工具调用 Schema（符合 OpenAI/Qwen 规范）
        
        Returns:
            工具定义 Schema
        """
        return {
            'type': 'function',
            'function': {
                'name': 'hex64_encode',
                'description': '将任意输入转为Hex64卦编码特征，用于增强AI推理的可解释性，不涉及任何玄学预测功能',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'input_str': {
                            'type': 'string',
                            'description': '需要转码的输入内容，如文本、日志、指令等'
                        },
                        'include_details': {
                            'type': 'boolean',
                            'description': '是否包含详细信息（拼音、英文翻译等）',
                            'default': True
                        }
                    },
                    'required': ['input_str']
                }
            }
        }
    
    def get_feature_interpretation(self, encoded: Dict[str, Any]) -> Dict[str, Any]:
        """
        解释特征向量的工程含义
        
        Args:
            encoded: encode() 返回的结果
            
        Returns:
            特征解释
        """
        feature_vec = encoded['feature_vector']
        yang_count = sum(feature_vec)
        yin_count = 6 - yang_count
        
        return {
            'yang_yin_ratio': f'{yang_count}阳{yin_count}阴',
            'dominant_energy': '阳性（主动/外放）' if yang_count > yin_count else '阴性（被动/内敛）',
            'gpio_state': ' → '.join(encoded['control_signal']),
            'semantic_theme': '、'.join(encoded['tags'][:3]),
            'engineering_mapping': encoded.get('operations', [])
        }


# 便捷函数
def quick_encode(text: str) -> Dict[str, Any]:
    """快速编码（不创建对象）"""
    encoder = Hex64Encoder()
    return encoder.encode(text)


if __name__ == '__main__':
    # 测试
    encoder = Hex64Encoder()
    
    test_inputs = ['Hello World', 'timeout_error', 'deploy_production', 'system_init']
    
    print("=== Hex64 编码器测试 ===\n")
    
    for text in test_inputs:
        result = encoder.encode(text)
        print(f"输入: {text}")
        print(f"  卦象: {result['hex_name']} ({result.get('english', '')})")
        print(f"  二进制: {result['binary']}")
        print(f"  标签: {', '.join(result['tags'])}")
        print(f"  特征: {result['feature_vector']}")
        print(f"  操作码: {', '.join(result['operations'])}")
        print()
