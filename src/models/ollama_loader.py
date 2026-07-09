"""
Ollama 模型加载器

通过 Ollama 本地 API 调用 Qwen3.5-9B 等模型
无需下载 HuggingFace 格式，直接使用已有 Ollama 模型

API: http://localhost:11434/api/chat
"""

import json
import sys
import requests
from typing import Optional, List, Dict, Any

# Windows UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class OllamaLoader:
    """Ollama 模型加载器，通过 HTTP API 调用本地模型"""

    def __init__(self, model_name: str = "qwen3.5:9b", base_url: str = "http://localhost:11434"):
        """
        初始化 Ollama 加载器
        
        Args:
            model_name: Ollama 模型名称（如 qwen3.5:9b）
            base_url: Ollama API 地址
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/chat"
        
        print(f"[INFO] 连接 Ollama: {base_url}")
        print(f"[INFO] 模型: {model_name}")
        
        # 验证连接
        if not self._check_connection():
            raise RuntimeError(
                f"无法连接 Ollama API ({base_url})\n"
                "请确保 Ollama 正在运行: ollama serve"
            )
        
        print("[OK] Ollama 连接成功")
    
    def _check_connection(self) -> bool:
        """检查 Ollama API 是否可访问"""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 1024,
        temperature: float = 0.7,
        do_sample: bool = True
    ) -> str:
        """
        对话接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            max_new_tokens: 最大生成 token 数
            temperature: 采样温度
            do_sample: 是否采样
            
        Returns:
            模型回复文本
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "num_predict": max_new_tokens,
                "temperature": temperature,
                "top_k": 20,
                "top_p": 0.95,
            },
            "keep_alive": -1,  # 保持模型加载状态
        }
        
        try:
            resp = requests.post(
                self.api_url,
                json=payload,
                timeout=120,
                stream=True
            )
            resp.raise_for_status()
            
            # 收集所有输出（Qwen3.5 只输出到 thinking 字段）
            full_response = ""
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    msg = chunk.get("message", {})
                    
                    # Qwen3.5 的 thinking mode：内容在 thinking 字段
                    thinking = msg.get("thinking", "")
                    content = msg.get("content", "")
                    
                    # 优先使用 thinking，fallback 到 content
                    if thinking:
                        full_response += thinking
                    elif content:
                        full_response += content
                    
                    if chunk.get("done", False):
                        break
                
                # 防止无限循环
                if len(full_response) > 10000:
                    break
            
            return full_response
                
        except requests.exceptions.Timeout:
            return "[ERROR] 请求超时，模型响应时间过长"
        except requests.exceptions.ConnectionError:
            return "[ERROR] 无法连接 Ollama，请确保 ollama serve 正在运行"
        except Exception as e:
            return f"[ERROR] 对话失败: {str(e)}"
    
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
            system_prompt: 系统提示词
            **kwargs: 其他参数（传递给 chat 方法）
            
        Returns:
            模型回复
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if history:
            messages.extend(history[-6:])  # 保留最近 3 轮对话
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat(messages, **kwargs)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出所有可用模型"""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return data.get("models", [])
        except Exception as e:
            print(f"[WARN] 获取模型列表失败: {e}")
            return []


# 便捷函数
def load_ollama(model_name: str = "qwen3.5:9b") -> OllamaLoader:
    """加载 Ollama 模型（便捷函数）"""
    return OllamaLoader(model_name)


if __name__ == "__main__":
    # 测试 Ollama 连接
    try:
        loader = OllamaLoader()
        print("\n=== Ollama 测试 ===")
        
        # 简单测试
        messages = [
            {"role": "system", "content": "你是一个有用的助手"},
            {"role": "user", "content": "你好，介绍一下你自己"}
        ]
        
        response = loader.chat(messages, max_new_tokens=100, temperature=0.5)
        print(f"\n用户: 你好，介绍一下你自己")
        print(f"模型: {response[:200]}...")
        
    except RuntimeError as e:
        print(f"\n[WARN] {e}")
        print("请确保 Ollama 正在运行: ollama serve")
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
