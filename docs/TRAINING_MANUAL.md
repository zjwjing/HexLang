# Hex64 LoRA 训练部署手册

## 一、硬件 & 环境基线

| 项目 | 规格 | 校验命令 | 预期结果 |
|------|------|---------|---------|
| 显卡 | NVIDIA RTX 5060 Ti 16G | nvidia-smi | 驱动>=550，CUDA 12.4+ |
| 显存 | 16GB GDDR7 | nvidia-smi -q --display=MEMORY | 总显存 15900MiB |
| Python | >= 3.10 | python --version | 3.10+ |
| PyTorch | >= 2.13.0 | python -c "import torch; print(torch.__version__)" | 2.13.0+ |

## 二、环境部署

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install transformers peft trl datasets bitsandbytes accelerate
pip install -r requirements.txt
```

**当前已安装版本**：
- transformers: 4.57.6
- peft: 0.18.1
- trl: 0.29.0
- datasets: 5.0.0
- bitsandbytes: 0.49.2
- accelerate: 最新

## 三、模型准备

### Qwen3-8B（推荐，16GB 显存可用）

通过 ModelScope 下载（国内镜像）：
```bash
python -c "from modelscope import snapshot_download; snapshot_download('Qwen/Qwen3-8B', cache_dir='models')"
```

或创建 junction 链接：
```powershell
New-Item -ItemType Junction -Name "models\qwen3-8b" -Target ".\models\Qwen\Qwen3-8B"
```

**模型信息**：
- 架构：Qwen3ForCausalLM (Dense)
- 参数量：8.19B
- 精度：BF16
- vocab_size: 151,936
- 文件大小：~17.4 GB

### ⚠️ Qwen3.5-9B 不可用原因

Qwen3.5-9B 是 **MoE 架构**，在 16GB 显存上无法训练：
- MoE 模型不支持 INT4 QLoRA（量化误差高）
- bf16 LoRA 需要 ~22GB > 16GB
- Unsloth 官方不建议对 Qwen3.5 做 QLoRA

## 四、训练配置（RTX 5060 Ti 优化）

| 参数 | 值 | 说明 |
|------|-----|------|
| max_steps | 1000 | 充分收敛 |
| batch_size | 1 | 显存限制 |
| gradient_accumulation_steps | 8 | 有效 batch = 8 |
| learning_rate | 2e-4 | 标准学习率 |
| warmup_steps | 50 | 前 50 步预热 |
| save_steps | 500 | 每 500 步保存检查点 |
| lora_rank | 32 | LoRA 秩 |
| optim | adamw_8bit | 8-bit Adam |
| bf16 | True | Qwen3 是 bf16 模型 |
| gradient_checkpointing | True | 节省显存 |
| max_length | 2048 | 序列长度限制 |

## 五、训练启动

### 标准训练
```bash
python src/training/train_lora.py \
    --model models/qwen3-8b \
    --steps 1000 \
    --rank 32 \
    --lr 2e-4 \
    --batch-size 1 \
    --output adapters/hex64-qwen3-8b-final
```

### 快速验证（5 steps）
```bash
python src/training/train_lora.py --steps 5 --batch-size 1
```

### 中断恢复
训练自动保存 checkpoint，中断后可从断点继续：
```bash
python src/training/train_lora.py --output adapters/hex64-qwen3-8b-final
```

## 六、训练结果

### 当前最佳结果
| Step | Loss | Token Accuracy |
|------|------|----------------|
| 100 | 3.44 | 51.5% |
| 500 | ~0.15 | ~96% |
| **1000** | **0.046** | **98.6%** |

### 输出文件
```
adapters/hex64-qwen3-8b-final/checkpoint-1000/
├── adapter_model.safetensors  (166 MB)
├── optimizer.pt               (170 MB)
├── adapter_config.json
└── [tokenizer files...]
```

### 资源占用
- 显存峰值：~14 GB / 16 GB
- 训练速度：~8.2 秒/step
- 总耗时：~2.3 小时（1000 steps）

## 七、推理验证

### 加载 adapter 进行推理
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

tokenizer = AutoTokenizer.from_pretrained("models/qwen3-8b", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    "models/qwen3-8b",
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)
model = PeftModel.from_pretrained(
    model,
    "adapters/hex64-qwen3-8b-final/checkpoint-1000"
)

messages = [{"role": "user", "content": "乾卦的二进制编码"}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## 八、Adapter 后处理

### 导出纯 adapter（不含 optimizer）
```bash
python scripts/post_process_adapter.py export \
    --input adapters/hex64-qwen3-8b-final/checkpoint-1000 \
    --output adapters/hex64-qwen3-8b-export
```

### 合并到基座模型（可选）
```bash
python scripts/post_process_adapter.py merge \
    --base-model models/qwen3-8b \
    --adapter adapters/hex64-qwen3-8b-final/checkpoint-1000 \
    --output models/qwen3-8b-hex64-merged
```

## 九、常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| CUDA OOM | batch_size 过大 | 降低到 1，启用 gradient_checkpointing |
| bf16 gradient error | 用了 fp16 scaler | 设置 `bf16=True` |
| text_config 属性缺失 | TRL 兼容性问题 | 添加 `model.config.text_config = model.config.get_text_config()` |
| connect timeout | HuggingFace 网络问题 | 使用 ModelScope 下载 |
| triton not found | 缺少 triton | 不影响训练，仅影响 flop counting |

## 十、环境校验

运行校验脚本：
```bash
python scripts/verify_env.py
```

**预期结果**：21/22 通过（hex64-test 临时目录可忽略）

## 十一、测试验证

运行全部测试：
```bash
npm test
```

**预期结果**：103/103 通过

---

**最后更新**：2026-07-11
**训练状态**：✅ 已完成 1000 steps，loss=0.046, acc=98.6%
