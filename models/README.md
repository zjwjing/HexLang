# models/ - AI 模型目录

本目录存放本地 AI 模型文件。

## 支持的模型版本

| 模型版本 | 显存占用 | 适用硬件 | 说明 |
|---------|---------|---------|------|
| Qwen3.5-9B-Instruct-FP16 | ~18GB | RTX 3090/4090 (24GB) | 全精度，适合微调 |
| Qwen3.5-9B-Instruct-GPTQ-Int4 | ~6GB | RTX 3060 (12GB) | GPTQ 量化，推理快 |
| Qwen3.5-9B-Instruct-AWQ-Int4 | ~6GB | RTX 3060 (12GB) | AWQ 量化，显存更低 |
| Qwen3.5-9B-Instruct-Q8_0 (GGUF) | ~10GB | 任何现代 CPU/GPU | llama.cpp/Ollama 格式 |

## 推荐配置

- **RTX 3060 (12GB)**: 使用 GPTQ-Int4 或 AWQ-Int4
- **RTX 3090/4090 (24GB)**: 使用 FP16 保留精度，方便后期微调
- **CPU 推理**: 使用 GGUF 格式 + llama.cpp

## 模型下载

```bash
# 使用 ModelScope 下载（推荐国内用户）
modelscope download --model qwen/Qwen3.5-9B-Instruct-GPTQ-Int4 --local_dir ./models/qwen3.5-9b-gptq-int4

# 或使用 HuggingFace
huggingface-cli download qwen/Qwen3.5-9B-Instruct-GPTQ-Int4 --local-dir ./models/qwen3.5-9b-gptq-int4
```

## 模型验证

下载完成后，运行以下命令验证模型能否正常加载：

```bash
python -c "from src.models.qwen_loader import QwenLoader; loader = QwenLoader(); print('模型加载成功！')"
```
