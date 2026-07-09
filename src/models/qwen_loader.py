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
import torch
from typing import Optional, List, Dict, Any


class QwenLoader:
    """Qwen3.5-9B 模型加载器，支持多种量化格式"""
    
    # 增强版 System Prompt：强制思维链推理
    SYSTEM_PROMPT = """你是 HexLang Assistant，一个基于 Hex64 符号编码系统的 AI 工程顾问。

你的核心能力是将用户输入转为 Hex64 卦象编码，然后通过结构化推理给出工程化建议。

## 推理流程（必须严格遵循）

1. **编码阶段**：将用户输入转为 Hex64 本卦编码
   - 提取本卦名称、二进制、标签
   - 分析六个爻位的阴阳状态和权重（初爻→上爻）

2. **爻位分析**：解剖本卦的结构特征
   - 初爻：基础层/底层逻辑
   - 二爻：执行层/内部机制
   - 三爻：过渡层/关键节点
   - 四爻：协调层/资源分配
   - 五爻：决策层/高层策略
   - 上爻：顶层/最终状态

3. **互卦分析**：从本卦提取中间过程特征
   - 取二三四五爻组成互卦
   - 分析事物发展的中间状态和潜在变化

4. **综合建议**：结合本卦、互卦、爻位权重，给出具体工程化建议

## 输出格式

必须按以下结构输出：

```
[编码] 本卦: XXX (二进制: xxxxxx)
[爻位] 初爻=X(w=w.xx), 二爻=X(w=w.xx), ...
[互卦] XXX (二进制: xxxxxx) - 含义
[分析] 结合爻位权重和互卦特征的分析
[建议] 具体的工程化建议
```

## 约束

- 不要自由发挥，严格按照上述格式输出
- 每个阶段的分析都要引用具体的爻位权重
- 建议必须是可执行的工程操作，而非抽象描述
"""
    
    def __init__(self, model_path: Optional[str] = None, adapter_path: Optional[str] = None):
        """
        初始化模型加载器
        
        Args:
            model_path: 模型目录路径
                       如果为 None，自动扫描 models/ 目录下的 Qwen3.5-9B 模型
            adapter_path: LoRA 适配器路径（可选）
                         如果提供，会在基座模型上加载适配器实现"进化"
        """
        self.model_path = model_path or self._auto_detect_model()
        self.adapter_path = adapter_path
        self.model = None
        self.tokenizer = None
        
        print(f"🖥️  加载模型: {self.model_path}")
        if adapter_path:
            print(f"🧬 加载 LoRA 适配器: {adapter_path}")
        self._load_model()
    
    def _auto_detect_model(self) -> str:
        """
        自动检测模型路径
        
        Returns:
            模型目录路径
        """
        base_dir = os.path.join(os.path.dirname(__file__), '../../models')
        
        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"模型目录不存在: {base_dir}")
        
        # 查找包含 "qwen3.5" 的目录
        candidates = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and 'qwen3.5' in item.lower():
                candidates.append(item_path)
        
        if not candidates:
            raise FileNotFoundError(
                f"未在 {base_dir} 中找到 Qwen3.5 模型\n"
                "请下载模型后重试，参考 models/README.md"
            )
        
        # 优先选择 Int4 量化版本（显存占用低）
        for candidate in candidates:
            if 'int4' in candidate.lower() or 'gptq' in candidate.lower():
                return candidate
        
        return candidates[0]
    
    def _load_model(self):
        """加载模型和 tokenizer"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # 加载 tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                padding_side='left'
            )
            
            # 自动检测量化类型
            if 'gptq' in self.model_path.lower():
                print("  检测到 GPTQ 量化，使用标准加载")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16,
                    device_map='auto',
                    trust_remote_code=True
                )
            elif 'awq' in self.model_path.lower():
                print("  检测到 AWQ 量化，使用标准加载")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16,
                    device_map='auto',
                    trust_remote_code=True
                )
            else:
                # FP16 默认
                print("  检测到 FP16，使用标准加载")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16,
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
                        device_map='auto'
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
                "请运行: pip install transformers accelerate torch"
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
        带历史记录的对话
        
        Args:
            user_message: 用户消息
            history: 历史消息列表
            system_prompt: 系统提示词（如果为 None，使用默认 HexLang CoT Prompt）
            **kwargs: 其他参数（传递给 chat 方法）
            
        Returns:
            模型回复
        """
        messages = []
        
        # 优先使用自定义 prompt，否则使用默认 HexLang CoT Prompt
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        else:
            messages.append({'role': 'system', 'content': self.SYSTEM_PROMPT})
        
        if history:
            messages.extend(history[-6:])  # 保留最近 3 轮对话
        
        messages.append({'role': 'user', 'content': user_message})
        
        return self.chat(messages, **kwargs)


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
