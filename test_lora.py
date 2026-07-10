"""测试微调后的 Hex64 模型推理"""
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

print("\n" + "="*60)
print("测试微调后的 Hex64 模型")
print("="*60 + "\n")

# 加载基础模型
model_path = "models/qwen3-8b"
adapter_path = "adapters/hex64-v1"

print(f"1. 加载基础模型（INT4 量化）: {model_path}")

# 使用与训练时相同的量化配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

base_model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

print(f"2. 加载 LoRA 适配器: {adapter_path}")
model = PeftModel.from_pretrained(
    base_model,
    adapter_path,
)
model.eval()

print(f"3. 加载 tokenizer")
tokenizer = AutoTokenizer.from_pretrained(adapter_path, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# 测试用例
test_cases = [
    "系统 CPU 过载了",
    "数据库连接池耗尽",
    "磁盘空间不足",
    "网络延迟升高",
    "内存泄漏检测",
]

print(f"\n{'='*60}")
print("推理测试")
print('='*60 + "\n")

for test_input in test_cases:
    messages = [
        {"role": "system", "content": "你是 HexLang Assistant"},
        {"role": "user", "content": test_input}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.1,
            do_sample=False
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # 提取用户消息后的回复
    user_msg_idx = response.find(test_input)
    if user_msg_idx >= 0:
        reply = response[user_msg_idx + len(test_input):].strip()
    else:
        reply = response
    
    print(f"输入: {test_input}")
    print(f"输出: {reply[:300]}")
    print("-" * 60)
