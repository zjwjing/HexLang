"""
Hex64 Rule Mapper — 业务规则 → 卦象映射器

将 if-else 业务规则转换为确定性卦象编码，实现：
- 规则可视化：晦涩的条件逻辑 → 可读的卦象符号
- 规则溯源：出问题直接看卦象流转路径，10秒定位错误步骤
- 规则校验：通过互卦分析规则链的中间状态

定位：确定性规则编码工具，非玄学系统
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# DJB2 哈希（与 JS/Python 版一致）
def _djb2_hash(text: str) -> int:
    h = 5381
    for ch in text:
        h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    return h


class RuleMapper:
    """规则→卦象映射器"""

    def __init__(self, hex_db_path: Optional[str] = None):
        if hex_db_path is None:
            hex_db_path = str(Path(__file__).parent.parent.parent / 'data' / 'hex64_full.json')

        with open(hex_db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.hex_db = data.get('hexagrams', data)
        self.bin_to_hex = {h['bin']: h for h in self.hex_db}
        self.name_to_bin = {h['name']: h['bin'] for h in self.hex_db}
        self.tag_to_op = data.get('tagToOp', {})

    def _condition_to_bin(self, rule_id: str, conditions: List[str]) -> str:
        """将规则条件列表映射为 6 位二进制"""
        bits = []
        for i, cond in enumerate(conditions[:6]):
            h = _djb2_hash(f"{rule_id}:{cond}")
            bits.append(h % 2)
        # 补齐 6 位
        while len(bits) < 6:
            bits.append(0)
        return ''.join(str(b) for b in bits)

    def map_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """将单条规则映射为卦象"""
        rule_id = rule.get('id', 'unknown')
        conditions = rule.get('conditions', [])
        action = rule.get('action', '')

        bin_code = self._condition_to_bin(rule_id, conditions)
        hex_data = self.bin_to_hex.get(bin_code)

        # 计算互卦
        bits = [int(b) for b in bin_code]
        inter_bits = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]]
        inter_bin = ''.join(str(b) for b in inter_bits)
        inter_hex = self.bin_to_hex.get(inter_bin)

        # 计算爻权重
        yao_weights = hex_data.get('yao_weights', [0.5] * 6) if hex_data else [0.5] * 6

        # 计算特征向量
        feature_vec = [b * w for b, w in zip(bits, yao_weights)]

        return {
            'rule_id': rule_id,
            'conditions': conditions,
            'action': action,
            'hex': {
                'name': hex_data['name'] if hex_data else '未知',
                'binary': bin_code,
                'english': hex_data.get('en', '') if hex_data else '',
                'tags': hex_data.get('tags', []) if hex_data else [],
                'weight': hex_data.get('weight', 0.5) if hex_data else 0.5,
            },
            'inter_hex': {
                'name': inter_hex['name'] if inter_hex else '未知',
                'binary': inter_bin,
            },
            'yao_weights': yao_weights,
            'feature_vector': feature_vec,
            'note': '确定性规则编码，非玄学预测',
        }

    def map_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量映射规则"""
        return [self.map_rule(rule) for rule in rules]

    def map_from_config(self, config_path: str) -> List[Dict[str, Any]]:
        """从配置文件加载规则并映射"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        rules = config.get('rules', [])
        return self.map_rules(rules)

    def format_rule_chain(self, mapped_rules: List[Dict[str, Any]]) -> str:
        """格式化规则链为可读文本"""
        lines = []
        for i, r in enumerate(mapped_rules):
            arrow = '→' if i < len(mapped_rules) - 1 else '∎'
            hex_name = r['hex']['name']
            inter_name = r['inter_hex']['name']
            conds = ' ∧ '.join(r['conditions'])
            lines.append(f"  [{r['rule_id']}] {conds}")
            lines.append(f"    → {hex_name} ({r['hex']['binary']})")
            lines.append(f"    → 互卦: {inter_name} ({r['inter_hex']['binary']})")
            lines.append(f"    → 动作: {r['action']}")
            if i < len(mapped_rules) - 1:
                lines.append(f"    {arrow}")
        return '\n'.join(lines)


if __name__ == '__main__':
    mapper = RuleMapper()

    # 示例规则：运维告警
    rules = [
        {
            'id': 'R001',
            'conditions': ['cpu_usage > 80%', 'mem_usage > 75%'],
            'action': '触发告警，通知运维团队',
        },
        {
            'id': 'R002',
            'conditions': ['error_rate > 1%', 'uptime_days > 30'],
            'action': '启动故障排查流程',
        },
        {
            'id': 'R003',
            'conditions': ['network_latency > 100ms'],
            'action': '切换备用链路',
        },
    ]

    results = mapper.map_rules(rules)
    print('=== 规则→卦象映射结果 ===\n')
    print(mapper.format_rule_chain(results))
    print()

    for r in results:
        print(f"[{r['rule_id']}] {r['hex']['name']} ({r['hex']['binary']})")
        print(f"  标签: {', '.join(r['hex']['tags'])}")
        print(f"  互卦: {r['inter_hex']['name']} ({r['inter_hex']['binary']})")
        print(f"  爻权重: {r['yao_weights']}")
        print(f"  特征向量: {[round(v, 2) for v in r['feature_vector']]}")
        print()
