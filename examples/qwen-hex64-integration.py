"""
Hex64 AI 集成模块 - Qwen3.5-9B 版本

将 Hex64 转码引擎封装为 Qwen AI 工具，增强推理可解释性
不涉及任何玄学预测，纯工程化实现

依赖安装：
    pip install transformers accelerate torch modelscope

使用方式：
    1. 直接转码：hex64_tool.encode("input_text")
    2. AI 集成：pipeline.chat("分析这段日志")
    3. 工具调用：通过 Function Calling 接口
"""

import hashlib
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class Hex64Encoder:
    """Hex64 转码工具，符合 Qwen Tool Calling 规范"""
    
    def __init__(self, hex_db_path: Optional[str] = None):
        """
        初始化 Hex64 编码器
        
        Args:
            hex_db_path: 六十四卦数据文件路径，默认为 data/hexagrams.json
        """
        if hex_db_path is None:
            # 自动定位 data/hexagrams.json
            hex_db_path = str(Path(__file__).parent.parent / 'data' / 'hexagrams.json')
        
        with open(hex_db_path, 'r', encoding='utf-8') as f:
            self.hex_db = json.load(f)
        
        # 构建 bin -> hexagram 映射
        self.bin_to_hex = {hex_item['bin']: hex_item for hex_item in self.hex_db}
        
        # 构建 name -> hexagram 映射
        self.name_to_hex = {hex_item['name']: hex_item for hex_item in self.hex_db}
    
    def encode(self, input_str: str) -> Dict[str, Any]:
        """
        将输入字符串编码为 Hex64 卦特征
        
        Args:
            input_str: 输入文本
            
        Returns:
            结构化编码结果
        """
        if not input_str:
            raise ValueError("输入不能为空")
        
        # 使用 DJB2 哈希算法（与 JavaScript 版本一致）
        h = 5381
        for char in input_str:
            h = ((h << 5) + h + ord(char)) & 0xFFFFFFFF
        
        # 映射到 0-63
        idx = h % 64
        bin_code = format(idx, '06b')
        
        # 查找卦数据
        hex_data = self.bin_to_hex.get(bin_code)
        if not hex_data:
            raise RuntimeError(f"未找到二进制 {bin_code} 对应的卦数据")
        
        # 构建特征向量
        feature_vec = [int(bit) for bit in bin_code]
        
        # 构建 GPIO 信号
        control_signal = ['ON' if bit == 1 else 'OFF' for bit in feature_vec]
        
        return {
            'input': input_str,
            'index': idx,
            'binary': bin_code,
            'hex_name': hex_data['name'],
            'pinyin': hex_data.get('pinyin', ''),
            'english': hex_data.get('en', ''),
            'category': hex_data.get('category', ''),
            'tags': hex_data.get('tags', []),
            'weight': hex_data.get('weight', 0.5),
            'feature_vector': feature_vec,
            'control_signal': control_signal,
            'explanation': f"对应卦象：{hex_data['name']}，语义标签：{','.join(hex_data['tags'])}"
        }
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        返回 Qwen Tool Calling 要求的 Schema
        
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
                        }
                    },
                    'required': ['input_str']
                }
            }
        }
    
    def batch_encode(self, inputs: List[str]) -> List[Dict[str, Any]]:
        """
        批量编码
        
        Args:
            inputs: 输入文本列表
            
        Returns:
            编码结果列表
        """
        return [self.encode(input_str) for input_str in inputs]


class QwenHex64Pipeline:
    """
    Qwen3.5-9B + Hex64 集成管道
    
    示例用法：
        pipeline = QwenHex64Pipeline()
        result = pipeline.chat("分析这段日志：timeout_error_404")
    """
    
    def __init__(
        self,
        model_path: str = './models/qwen3.5-9b-instruct-gptq-int4',
        device: str = 'auto'
    ):
        """
        初始化 Qwen + Hex64 管道
        
        Args:
            model_path: Qwen 模型路径
            device: 设备选择 ('auto', 'cuda', 'cpu')
        """
        self.hex_tool = Hex64Encoder()
        self.model_path = model_path
        self.device = device
        
        # 延迟加载模型（避免不必要的 GPU 占用）
        self._model = None
        self._tokenizer = None
    
    @property
    def model(self):
        """懒加载模型"""
        if self._model is None:
            self._load_model()
        return self._model
    
    @property
    def tokenizer(self):
        """懒加载 tokenizer"""
        if self._tokenizer is None:
            self._load_model()
        return self._tokenizer
    
    def _load_model(self):
        """加载 Qwen 模型和 tokenizer"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"正在加载模型: {self.model_path}")
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map=self.device,
                trust_remote_code=True,
                torch_dtype=torch.float16
            )
            
            self._model.eval()
            print("模型加载完成")
            
        except ImportError:
            raise ImportError(
                "请安装依赖: pip install transformers accelerate torch modelscope"
            )
    
    def chat(
        self,
        user_message: str,
        use_hex64: bool = True,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        与 Qwen 模型对话，可选择性地使用 Hex64 编码
        
        Args:
            user_message: 用户消息
            use_hex64: 是否使用 Hex64 编码增强
            system_prompt: 系统提示词
            
        Returns:
            对话结果
        """
        # 默认 System Prompt
        if system_prompt is None:
            system_prompt = """你是一个专业的软件工程助手，使用Hex64符号编码系统增强代码可解释性。

## 重要约束
1. Hex64是确定性编码基础设施，基于邵雍先天六十四卦与二进制映射
2. 所有运算逻辑完全 deterministic（确定性），不涉及任何玄学预测
3. 卦象标签映射到工程概念：如"订阅"、"监听"、"重构"、"告警"等
4. 不要对卦象进行算命、预测、风水等解读

## 使用方式
当用户输入文本时，你可以调用 hex64_encode 工具获取其特征编码，然后：
- 解释编码的语义含义
- 提供对应的代码模板
- 给出工程实践建议"""
        
        # 如果需要 Hex64 编码
        hex64_result = None
        if use_hex64:
            try:
                hex64_result = self.hex_tool.encode(user_message)
            except Exception as e:
                print(f"Hex64 编码失败: {e}")
        
        # 构建消息
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        # 如果有 Hex64 结果，附加到消息中
        if hex64_result:
            hex_info = (
                f"\n\n[Hex64 编码结果]\n"
                f"卦象: {hex64_result['hex_name']} ({hex64_result['english']})\n"
                f"二进制: {hex64_result['binary']}\n"
                f"标签: {', '.join(hex64_result['tags'])}\n"
                f"分类: {hex64_result['category']}"
            )
            messages[1]['content'] += hex_info
        
        # 调用模型
        try:
            text = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = self._tokenizer([text], return_tensors='pt').to(self.model.device)
            
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=1024,
                temperature=0.7,
                do_sample=True
            )
            
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self._tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
        except Exception as e:
            response = f"模型调用失败: {e}"
        
        return {
            'response': response,
            'hex64': hex64_result,
            'messages': messages
        }
    
    def tool_call(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理工具调用
        
        Args:
            tool_calls: 工具调用列表，格式如：
                [
                    {
                        'id': 'call_123',
                        'function': {
                            'name': 'hex64_encode',
                            'arguments': '{"input_str": "test"}'
                        }
                    }
                ]
                
        Returns:
            工具调用结果列表
        """
        results = []
        
        for tool_call in tool_calls:
            func_name = tool_call['function']['name']
            func_args = json.loads(tool_call['function']['arguments'])
            
            if func_name == 'hex64_encode':
                try:
                    result = self.hex_tool.encode(func_args['input_str'])
                    results.append({
                        'tool_call_id': tool_call['id'],
                        'role': 'tool',
                        'content': json.dumps(result, ensure_ascii=False, indent=2)
                    })
                except Exception as e:
                    results.append({
                        'tool_call_id': tool_call['id'],
                        'role': 'tool',
                        'content': f'错误: {str(e)}'
                    })
            else:
                results.append({
                    'tool_call_id': tool_call['id'],
                    'role': 'tool',
                    'content': f'未知工具: {func_name}'
                })
        
        return results


# 便捷函数
def quick_encode(text: str) -> Dict[str, Any]:
    """快速编码（不加载模型）"""
    encoder = Hex64Encoder()
    return encoder.encode(text)


if __name__ == '__main__':
    # 测试 Hex64 编码
    print("=== Hex64 快速编码测试 ===\n")
    
    test_inputs = ['Hello World', 'timeout_error', 'deploy_production', 'system_init']
    
    for text in test_inputs:
        result = quick_encode(text)
        print(f"输入: {text}")
        print(f"  卦象: {result['hex_name']} ({result['english']})")
        print(f"  二进制: {result['binary']}")
        print(f"  标签: {', '.join(result['tags'])}")
        print(f"  特征: {result['feature_vector']}")
        print()
    
    print("=== 工具 Schema ===\n")
    encoder = Hex64Encoder()
    print(json.dumps(encoder.get_tool_schema(), ensure_ascii=False, indent=2))
