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
Qwen 模型加载器

支持多种量化格式：
- FP16（全精度）
- GPTQ-Int4（4位量化）
- AWQ-Int4（4位量化）
- GGUF（llama.cpp 格式）

自动检测模型类型并加载
"""

import os
import json
import hashlib
import torch
from typing import Optional, List, Dict, Any


class SemanticCache:
    """语义缓存：基于 Hex64 编码的推理结果缓存"""

    def __init__(self, cache_path: Optional[str] = None, max_size: int = 1000):
        if cache_path is None:
            cache_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'semantic_cache.json')
        self.cache_path = cache_path
        self.max_size = max_size
        self.cache = self._load()

    def _load(self) -> Dict:
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _make_key(self, hex_result: dict) -> str:
        bin_code = hex_result.get('binary', '')
        yao = hex_result.get('yao_weights', [0] * 6)
        rounded = [round(w, 1) for w in yao]
        return f"{bin_code}|{','.join(str(r) for r in rounded)}"

    def get(self, hex_result: dict) -> Optional[str]:
        key = self._make_key(hex_result)
        entry = self.cache.get(key)
        if entry:
            return entry.get('response')
        return None

    def put(self, hex_result: dict, response: str):
        key = self._make_key(hex_result)
        self.cache[key] = {
            'binary': hex_result.get('binary'),
            'hex_name': hex_result.get('hex_name'),
            'yao_weights': hex_result.get('yao_weights'),
            'response': response,
        }
        if len(self.cache) > self.max_size:
            oldest = list(self.cache.keys())[0]
            del self.cache[oldest]
        self._save()


class QwenLoader:
    """Qwen3.5-9B 模型加载器，支持多种量化格式"""

    SYSTEM_PROMPT = """你是 HexLang Assistant，一个基于 Hex64 符号编码系统的 AI 工程顾问。

你的核心能力是将用户输入转为 Hex64 卦象编码，然后通过结构化推理给出工程化建议。

## 强制逻辑对齐规则（必须严格遵守）

1. 你必须先输出 [Hex64] 字段（包含本卦、互卦、爻权重）。
2. 你的后续回答必须严格符合卦象的语义边界，不得超越卦象逻辑自由发挥。
3. 如果输入涉及违规、虚假或有害信息，你必须输出对应的卦象（如"天水讼"或"山风蛊"），并明确指出逻辑矛盾，不得提供执行建议。
4. Hex64 是确定性编码工具，不提供反解功能，卦象仅作为输入特征的指纹，不构成任何预测能力。

## 禁止词库

禁止使用：预测、运势、吉凶、算命、风水、五行、八字、命理、星座、塔罗、老天爷、天机、命中注定。
如果用户输入涉及上述词汇，直接回复："Hex64 为工程符号系统，不支持玄学查询。请输入工程/技术/运维相关问题。"

## 思考步骤（必须按顺序执行，每步输出结果）

步骤1. 输入解析：提取用户输入的关键实体和动作。
步骤2. 卦象映射：根据 Hex64 编码，本卦为 [Name]，核心语义为 [Tags]。
步骤3. 互卦推演：中间过程涉及 [InterName]，表明 [InterMeaning]。
步骤4. 爻位分析：重点观察第 [N] 爻，权重 [Weight]，代表 [Significance]。
步骤5. 工程建议：基于上述结构化分析，给出唯一的可执行建议。

## 爻位语义映射

- 初爻（权重最低）：基础层/底层逻辑/基础设施
- 二爻：执行层/内部机制/数据流
- 三爻（过渡）：关键节点/瓶颈/状态转换
- 四爻：协调层/资源分配/外部接口
- 五爻（权重最高）：决策层/高层策略/核心业务
- 上爻：顶层/最终状态/输出/用户界面

## 输出格式

必须按以下结构输出：

```
[Hex64] 本卦: XXX (二进制: xxxxxx) | 互卦: XXX (二进制: xxxxxx)
[爻位] 初爻=X(w=w.xx), 二爻=X(w=w.xx), 三爻=X(w=w.xx), 四爻=X(w=w.xx), 五爻=X(w=w.xx), 上爻=X(w=w.xx)
[思考] 步骤1→步骤2→步骤3→步骤4→步骤5 的结构化推理链
[建议] 具体的工程化建议（仅一条，可执行）
```

## 约束

- 不要自由发挥，严格按照上述格式输出
- 每个阶段的分析都要引用具体的爻位权重
- 建议必须是可执行的工程操作，而非抽象描述
- 如果无法确定，明确说"信息不足，无法分析"，不要编造
"""

    def __init__(self, model_path: Optional[str] = None, adapter_path: Optional[str] = "adapters/hex64-qwen3-8b-final", enable_cache: bool = True):
        self.model_path = model_path or self._auto_detect_model()
        self.adapter_path = adapter_path
        self.model = None
        self.tokenizer = None
        self.cache = SemanticCache() if enable_cache else None
        self._encoder = None
        print(f"🖥️  加载模型: {self.model_path}")
        if adapter_path:
            print(f"🧬 加载 LoRA 适配器: {adapter_path}")
        self._load_model()

    def _get_encoder(self):
        if self._encoder is None:
            from src.core.encoder import Hex64Encoder
            self._encoder = Hex64Encoder()
        return self._encoder
    
    def _auto_detect_model(self) -> str:
        """
        自动检测模型路径
        
        Returns:
            模型目录路径
        """
        base_dir = os.path.join(os.path.dirname(__file__), '../../models')
        
        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"模型目录不存在: {base_dir}")
        
        # 查找包含 "qwen3" 的目录（排除 qwen3.5 VL 和 qwen3_vl）
        candidates = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                name_lower = item.lower()
                if 'qwen3' in name_lower and 'qwen3.5' not in name_lower and 'qwen3_vl' not in name_lower:
                    candidates.append(item_path)
        
        if not candidates:
            raise FileNotFoundError(
                f"未在 {base_dir} 中找到 Qwen3 模型\n"
                "请下载模型后重试：modelscope download --model Qwen/Qwen3.5-9B --local_dir models/qwen3.5-9b"
            )
        
        return candidates[0]
    
    def _load_model(self):
        """加载模型和 tokenizer"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            
            # 加载 tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                padding_side='left'
            )
            
            # 使用 INT4 量化加载（与训练时一致）
            print("  使用 INT4 量化加载（节省显存）")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                quantization_config=bnb_config,
                device_map='auto',
                trust_remote_code=True
            )
            
            self.model.eval()
            print("✅ 模型加载完成")
            
            # 加载 LoRA 适配器（如果提供）
            if self.adapter_path and os.path.exists(self.adapter_path):
                print(f"  🧬 加载进化适配器: {self.adapter_path}")
                try:
                    from peft import PeftModel
                    self.model = PeftModel.from_pretrained(
                        self.model,
                        self.adapter_path,
                    )
                    print("  ✅ 适配器加载成功，模型已完成进化！")
                except ImportError:
                    print("  ⚠️  缺少 peft 库，无法加载适配器。请运行: pip install peft")
                except Exception as e:
                    print(f"  ⚠️  适配器加载失败: {e}")
                    print("  将继续使用未进化的基座模型")
            elif self.adapter_path:
                print(f"  ⚠️  适配器路径不存在: {self.adapter_path}")
                print("  将使用未进化的基座模型")
            
        except ImportError as e:
            raise ImportError(
                f"缺少依赖: {e}\n"
                "请运行: pip install transformers accelerate torch peft bitsandbytes"
            )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        do_sample: bool = True
    ) -> str:
        """
        对话接口
        
        Args:
            messages: 消息列表，格式如：
                [
                    {'role': 'system', 'content': '...'},
                    {'role': 'user', 'content': '...'}
                ]
            max_new_tokens: 最大生成 token 数
            temperature: 采样温度（0 = 贪婪解码）
            do_sample: 是否采样
            
        Returns:
            模型回复文本
        """
        if self.tokenizer is None or self.model is None:
            raise RuntimeError("模型未加载")
        
        # 转换为模型格式
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer(text, return_tensors='pt').to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # 解码生成的 token
        generated_ids = outputs[0][inputs.input_ids.shape[1]:]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        return response
    
    def chat_with_history(
        self,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        带历史记录的对话（集成语义缓存）

        Args:
            user_message: 用户消息
            history: 历史消息列表
            system_prompt: 系统提示词（如果为 None，使用默认 HexLang CoT Prompt）
            **kwargs: 其他参数（传递给 chat 方法）

        Returns:
            模型回复
        """
        # 1. 计算 Hex64 编码
        encoder = self._get_encoder()
        hex_result = encoder.encode(user_message)

        # 2. 检查语义缓存
        if self.cache:
            cached = self.cache.get(hex_result)
            if cached:
                print(f"⚡ 语义缓存命中: {hex_result['hex_name']} ({hex_result['binary']})")
                return cached

        # 3. 构建消息
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        else:
            messages.append({'role': 'system', 'content': self.SYSTEM_PROMPT})

        if history:
            messages.extend(history[-6:])

        # 在用户消息前注入 Hex64 编码上下文
        hex_context = (
            f"[Hex64 编码]\n"
            f"本卦: {hex_result['hex_name']} ({hex_result['binary']})\n"
            f"标签: {', '.join(hex_result['tags'])}\n"
            f"权重: {hex_result['weight']}\n"
            f"爻权重: {hex_result['yao_weights']}\n"
            f"互卦: {hex_result['inter_hex'].get('hex_name', '无')} ({hex_result['inter_hex'].get('binary', '-')})\n"
            f"\n{user_message}"
        )
        messages.append({'role': 'user', 'content': hex_context})

        # 4. 调用模型
        response = self.chat(messages, **kwargs)

        # 5. 写入缓存
        if self.cache:
            self.cache.put(hex_result, response)

        return response


# 便捷函数
def load_qwen(model_path: Optional[str] = None) -> QwenLoader:
    """加载 Qwen 模型（便捷函数）"""
    return QwenLoader(model_path)


if __name__ == '__main__':
    # 测试模型加载
    try:
        loader = QwenLoader()
        print("\n=== 模型加载测试 ===")
        
        # 简单测试
        messages = [
            {'role': 'system', 'content': '你是一个有用的助手'},
            {'role': 'user', 'content': '你好，介绍一下你自己'}
        ]
        
        response = loader.chat(messages, max_new_tokens=100, temperature=0.5)
        print(f"\n用户: 你好，介绍一下你自己")
        print(f"模型: {response}")
        
    except FileNotFoundError as e:
        print(f"\n⚠️  {e}")
        print("请先下载模型文件，参考 models/README.md")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
