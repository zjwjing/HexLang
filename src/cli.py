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
HexLang CLI - 命令行入口

交互式对话界面，集成 Hex64 转码和 Qwen AI 推理

使用方式：
    python src/cli.py                    # 使用 Ollama API（默认）
    python src/cli.py --no-ollama        # 仅使用转码功能

功能：
    - 自然语言对话
    - Hex64 特征编码
    - 反馈提交（修正误判）
    - 历史记录管理
"""

import sys
import os
import json
from datetime import datetime

# Windows UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.encoder import Hex64Encoder
from src.models.qwen_loader import QwenLoader
from src.models.ollama_loader import OllamaLoader


# System Prompt - 严格约束模型行为
SYSTEM_PROMPT = """你是 HexLang Assistant，基于 Qwen3.5-9B + Hex64 符号引擎。

## 工作职责
1. 分析用户输入的文本/日志/指令
2. 调用 Hex64 转码工具获取特征编码
3. 结合卦象语义提供工程化建议
4. 输出格式：[回复] + [Hex64溯源]

## 重要约束
- Hex64 是确定性编码基础设施，不涉及任何玄学预测
- 卦象标签映射到工程概念：如"订阅"、"监听"、"重构"、"告警"等
- 严禁算命、预测、风水等解读
- 保持专业、客观的工程化语气

## 输出格式示例
[回复] 检测到系统异常，建议启动熔断机制...

[Hex64溯源] 天水讼（冲突/停止）
  二进制：101111
  标签：团结，协作，开源，社区，共享，大同
  特征：[1, 0, 1, 1, 1, 1]
"""


class HexLangCLI:
    """HexLang 命令行界面"""
    
    def __init__(self, adapter_path: str = None, use_ollama: bool = True, ollama_model: str = "qwen3.5:9b"):
        """初始化 CLI
        
        Args:
            adapter_path: LoRA 适配器路径（可选）
            use_ollama: 是否使用 Ollama API（默认 True，推荐）
            ollama_model: Ollama 模型名称（默认 qwen3.5:9b）
        """
        print("🚀 初始化 HexLang...")
        
        # 初始化 Hex64 编码器
        self.encoder = Hex64Encoder()
        print("✅ Hex64 编码器就绪")
        
        # 尝试加载 AI 模型
        if use_ollama:
            try:
                from src.models.ollama_loader import OllamaLoader
                self.qwen = OllamaLoader(model_name=ollama_model)
                print(f"✅ Ollama 模型加载成功: {ollama_model}")
                self.has_model = True
                self.model_type = "ollama"
            except Exception as e:
                print(f"⚠️  Ollama 加载失败: {e}")
                print("💡 提示: 运行 'python src/cli.py --no-ollama' 仅使用转码功能")
                self.has_model = False
                self.model_type = None
        else:
            try:
                self.qwen = QwenLoader(adapter_path=adapter_path)
                print("✅ Qwen 模型加载成功")
                self.has_model = True
                self.model_type = "local"
            except FileNotFoundError as e:
                print(f"⚠️  {e}")
                print("💡 提示：运行 'python src/cli.py --encode-only' 仅使用转码功能")
                self.has_model = False
                self.model_type = None
            except Exception as e:
                print(f"❌ 模型加载失败: {e}")
                self.has_model = False
                self.model_type = None
        
        # 对话历史
        self.history = []
        
        # 反馈文件路径
        self.feedback_file = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'feedback.json'
        )
        
        print("\n" + "="*60)
        print(" HexLang v0.1 (Qwen3.5-9B + Hex64)")
        print("="*60)
        print("命令说明：")
        print("  - 直接输入文本进行对话")
        print("  - 输入 'exit' 或 'quit' 退出")
        print("  - 输入 'history' 查看对话历史")
        print("  - 输入 'clear' 清空历史")
        print("  - 输入 'feedback 原卦→目标卦 场景:xxx' 提交修正")
        print("="*60 + "\n")
    
    def encode_only(self, text: str) -> dict:
        """仅转码，不调用 AI 模型"""
        try:
            result = self.encoder.encode(text)
            interpretation = self.encoder.get_feature_interpretation(result)
            
            output = f"\n[Hex64 编码结果]\n"
            output += f"输入: {text}\n"
            output += f"卦象: {result['hex_name']} ({result.get('english', '')})\n"
            output += f"二进制: {result['binary']}\n"
            output += f"标签: {', '.join(result['tags'])}\n"
            output += f"分类: {result.get('category', '')}\n"
            output += f"特征: {result['feature_vector']}\n"
            output += f"GPIO: {' | '.join(result['control_signal'])}\n"
            output += f"操作码: {', '.join(result['operations'])}\n"
            output += f"\n[特征解释]\n"
            output += f"阴阳比例: {interpretation['yang_yin_ratio']}\n"
            output += f"主导能量: {interpretation['dominant_energy']}\n"
            output += f"语义主题: {interpretation['semantic_theme']}\n"
            
            return output
        except Exception as e:
            return f"\n❌ 编码失败: {e}"
    
    def chat(self, user_message: str) -> str:
        """对话接口"""
        if not self.has_model:
            return self.encode_only(user_message)
        
        try:
            # 1. Hex64 转码
            hex_result = self.encoder.encode(user_message)
            interpretation = self.encoder.get_feature_interpretation(hex_result)
            
            # 2. 构建 Hex64 观察信息
            hex_observation = (
                f"[Hex64观察]\n"
                f"输入「{user_message}」→ "
                f"卦：{hex_result['hex_name']}({hex_result['binary']})，"
                f"标签：{','.join(hex_result['tags'])}，"
                f"向量：{hex_result['feature_vector']}"
            )
            
            # 3. 构建消息列表
            messages = [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                *self.history[-6:],  # 保留最近 3 轮
                {'role': 'user', 'content': user_message}
            ]
            
            # 4. 附加 Hex64 观察到系统消息
            messages.append({'role': 'system', 'content': hex_observation})
            
            # 5. 调用模型
            response = self.qwen.chat(messages, max_new_tokens=1024, temperature=0.7)
            
            # 6. 更新历史
            self.history.append({'role': 'user', 'content': user_message})
            self.history.append({'role': 'assistant', 'content': response})
            
            # 7. 格式化输出
            output = f"\n[回复]\n{response}\n"
            output += f"\n[Hex64溯源]\n"
            output += f"卦象: {hex_result['hex_name']} ({hex_result.get('english', '')})\n"
            output += f"二进制: {hex_result['binary']}\n"
            output += f"标签: {', '.join(hex_result['tags'])}\n"
            output += f"分类: {hex_result.get('category', '')}\n"
            output += f"特征: {hex_result['feature_vector']}\n"
            
            return output
            
        except Exception as e:
            return f"\n❌ 对话失败: {e}\n\n请尝试仅使用转码功能：{self.encode_only(user_message)}"
    
    def process_feedback(self, feedback_text: str) -> str:
        """处理反馈"""
        try:
            # 解析反馈格式：feedback 原卦→目标卦 场景:xxx
            parts = feedback_text.replace('feedback ', '').strip()
            swap, scene_part = parts.split(' 场景:')
            origin, target = swap.split('→')
            origin = origin.strip()
            target = target.strip()
            scene = scene_part.strip()
            
            # 保存到反馈文件
            feedback_entry = {
                'timestamp': datetime.now().isoformat(),
                'original_hex': origin,
                'target_hex': target,
                'scene': scene,
                'parsed': True
            }
            
            # 读取现有反馈
            feedbacks = []
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    try:
                        feedbacks = json.load(f)
                    except json.JSONDecodeError:
                        feedbacks = []
            
            # 添加新反馈
            feedbacks.append(feedback_entry)
            
            # 保存
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            
            return f"✅ 反馈已记录：{origin} → {target}（{scene}）\n共 {len(feedbacks)} 条反馈"
            
        except Exception as e:
            return f"⚠️ 反馈格式错误\n正确格式：feedback 原卦→目标卦 场景:xxx\n错误详情：{e}"
    
    def run(self):
        """运行交互式对话"""
        print("HexLang 已启动，输入文本开始对话...\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # 退出命令
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n再见！👋")
                    break
                
                # 清空历史
                if user_input.lower() == 'clear':
                    self.history = []
                    print("✅ 对话历史已清空\n")
                    continue
                
                # 查看历史
                if user_input.lower() == 'history':
                    print("\n=== 对话历史 ===")
                    for i, msg in enumerate(self.history[-10:], 1):
                        role = '👤 用户' if msg['role'] == 'user' else '🤖 助手'
                        print(f"{i}. {role}: {msg['content'][:100]}...")
                    print()
                    continue
                
                # 反馈命令
                if user_input.lower().startswith('feedback'):
                    print(self.process_feedback(user_input))
                    print()
                    continue
                
                # 普通对话
                response = self.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n再见！👋")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HexLang - Qwen3.5-9B + Hex64 智能助手')
    parser.add_argument('--encode-only', action='store_true', 
                       help='仅使用转码功能，不加载 AI 模型')
    parser.add_argument('--input', type=str, help='单次输入文本')
    parser.add_argument('--adapter', type=str, default=None,
                       help='LoRA 适配器路径（进化后的模型）')
    parser.add_argument('--ollama-model', type=str, default='qwen3.5:9b',
                       help='Ollama 模型名称（默认 qwen3.5:9b）')
    parser.add_argument('--no-ollama', action='store_true',
                       help='禁用 Ollama，使用本地模型或仅转码')
    
    args = parser.parse_args()
    
    cli = HexLangCLI(
        adapter_path=args.adapter,
        use_ollama=not args.no_ollama,
        ollama_model=args.ollama_model
    )
    
    if args.encode_only:
        cli.has_model = False
        print("\n💡 已禁用 AI 模型，仅使用 Hex64 转码功能\n")
    
    if args.input:
        # 单次输入模式
        if cli.has_model:
            print(cli.chat(args.input))
        else:
            print(cli.encode_only(args.input))
    else:
        # 交互式模式
        cli.run()


if __name__ == '__main__':
    main()
