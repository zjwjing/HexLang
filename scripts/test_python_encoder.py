"""Hex64 Python Encoder 单元测试"""
import unittest
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class TestHex64Encoder(unittest.TestCase):
    """Hex64Encoder 核心功能测试"""

    @classmethod
    def setUpClass(cls):
        from src.core.encoder import Hex64Encoder
        cls.encoder = Hex64Encoder()

    def test_encode_returns_required_fields(self):
        """编码结果应包含所有必要字段"""
        result = self.encoder.encode("test_input")
        required_fields = [
            'input', 'index', 'binary', 'hex_name', 'tags',
            'weight', 'feature_vector', 'control_signal',
            'operations', 'yao_weights', 'yao_analysis'
        ]
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")

    def test_encode_deterministic(self):
        """相同输入应产生相同输出"""
        result1 = self.encoder.encode("deterministic_test")
        result2 = self.encoder.encode("deterministic_test")
        self.assertEqual(result1['index'], result2['index'])
        self.assertEqual(result1['binary'], result2['binary'])
        self.assertEqual(result1['hex_name'], result2['hex_name'])

    def test_encode_different_inputs(self):
        """不同输入应产生不同卦象"""
        r1 = self.encoder.encode("input_a")
        r2 = self.encoder.encode("input_b")
        # 大概率不同（虽然理论上可能碰撞）
        self.assertNotEqual(r1['hex_name'], r2['hex_name'])

    def test_binary_is_6_bits(self):
        """二进制编码应为 6 位"""
        result = self.encoder.encode("any_input")
        self.assertEqual(len(result['binary']), 6)
        self.assertTrue(all(c in '01' for c in result['binary']))

    def test_index_range(self):
        """索引应在 0-63 范围内"""
        for i in range(100):
            result = self.encoder.encode(f"input_{i}")
            self.assertGreaterEqual(result['index'], 0)
            self.assertLess(result['index'], 64)

    def test_feature_vector_length(self):
        """特征向量长度应为 6"""
        result = self.encoder.encode("test")
        self.assertEqual(len(result['feature_vector']), 6)

    def test_yao_weights_length(self):
        """爻权重长度应为 6"""
        result = self.encoder.encode("test")
        self.assertEqual(len(result['yao_weights']), 6)

    def test_control_signal_format(self):
        """控制信号应为 ON/OFF 数组"""
        result = self.encoder.encode("test")
        self.assertEqual(len(result['control_signal']), 6)
        for signal in result['control_signal']:
            self.assertIn(signal, ['ON', 'OFF'])

    def test_inter_hex_present(self):
        """互卦分析应存在"""
        result = self.encoder.encode("test")
        self.assertIn('inter_hex', result)
        self.assertIn('is_present', result['inter_hex'])

    def test_combined_feature_length(self):
        """组合特征应为 12 维（本卦 6 + 互卦 6）"""
        result = self.encoder.encode("test")
        if 'combined_feature' in result:
            self.assertEqual(len(result['combined_feature']), 12)

    def test_embedding_64d(self):
        """64 维 embedding 应存在"""
        result = self.encoder.encode("test")
        self.assertIn('embedding_64d', result)
        self.assertEqual(len(result['embedding_64d']), 64)

    def test_batch_encode(self):
        """批量编码应返回等长列表"""
        inputs = ["a", "b", "c"]
        results = self.encoder.batch_encode(inputs)
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertIn('hex_name', r)

    def test_get_feature_interpretation(self):
        """特征解释应返回正确格式"""
        result = self.encoder.encode("test")
        interpretation = self.encoder.get_feature_interpretation(result)
        self.assertIn('yang_yin_ratio', interpretation)
        self.assertIn('dominant_energy', interpretation)
        self.assertIn('gpio_state', interpretation)

    def test_tool_schema(self):
        """工具 Schema 应符合 OpenAI 规范"""
        schema = self.encoder.get_tool_schema()
        self.assertEqual(schema['type'], 'function')
        self.assertIn('function', schema)
        self.assertEqual(schema['function']['name'], 'hex64_encode')
        self.assertIn('parameters', schema['function'])


class TestQuickEncode(unittest.TestCase):
    """便捷函数测试"""

    def test_quick_encode(self):
        from src.core.encoder import quick_encode
        result = quick_encode("quick_test")
        self.assertIn('hex_name', result)
        self.assertIn('binary', result)


class TestDataIntegrity(unittest.TestCase):
    """数据完整性测试"""

    def test_hexagrams_json_valid(self):
        """hexagrams.json 应包含 64 个卦"""
        data_path = Path(__file__).parent / 'data' / 'hexagrams.json'
        with open(data_path, 'r', encoding='utf-8') as f:
            hexagrams = json.load(f)
        self.assertEqual(len(hexagrams), 64)

    def test_hex64_full_json_valid(self):
        """hex64_full.json 应包含 tagToOp 映射"""
        data_path = Path(__file__).parent / 'data' / 'hex64_full.json'
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('hexagrams', data)
        self.assertIn('tagToOp', data)
        self.assertEqual(len(data['hexagrams']), 64)

    def test_no_duplicate_binaries(self):
        """不应有重复的二进制编码"""
        data_path = Path(__file__).parent / 'data' / 'hex64_full.json'
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        binaries = [h['bin'] for h in data['hexagrams']]
        self.assertEqual(len(binaries), len(set(binaries)), "Duplicate binary codes found!")

    def test_all_binaries_6_bits(self):
        """所有二进制编码应为 6 位"""
        data_path = Path(__file__).parent / 'data' / 'hex64_full.json'
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for hexagram in data['hexagrams']:
            self.assertEqual(len(hexagram['bin']), 6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
