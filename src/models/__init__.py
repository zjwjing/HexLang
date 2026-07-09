# src/models/ - AI 模型模块
"""
AI 模型加载和管理模块
支持 Qwen3.5-9B 及其各种量化版本
支持 Ollama API 调用
"""

from .qwen_loader import QwenLoader, load_qwen
from .ollama_loader import OllamaLoader, load_ollama

__all__ = ['QwenLoader', 'load_qwen', 'OllamaLoader', 'load_ollama']
