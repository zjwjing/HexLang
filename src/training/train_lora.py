"""
Hex64 QLoRA 微调脚本

使用 peft + transformers 对 Qwen3.5-9B 进行 LoRA 微调
让模型学习 Hex64 的编码规则和输出格式

前置条件：
1. 已收集足够反馈数据（200+ 条）
2. 已运行 src/training/prepare_data.py 生成训练数据
3. 显存 >=8GB（INT4 量化）或 >=20GB（FP16）

依赖安装：
    pip install torch transformers peft trl datasets accelerate bitsandbytes

使用方式：
    python src/training/train_lora.py
    
输出：
    adapters/hex64-v1/ - LoRA 适配器权重（约 50MB）
"""

import os
import sys
import json
import torch
from pathlib import Path
from typing import Optional

# 修复 Windows 控制台 UTF-8 编码问题
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def load_training_data(data_file: str) -> list:
    """
    加载 JSONL 格式的训练数据
    
    Args:
        data_file: 训练数据文件路径
        
    Returns:
        训练数据列表
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return [json.loads(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"训练数据文件不存在: {data_file}")
        print("请先运行: python src/training/prepare_data.py")
        return []
    except json.JSONDecodeError as e:
        print(f"训练数据格式错误: {e}")
        return []


def train_lora(
    model_path: str = None,
    training_data_file: str = None,
    adapter_path: str = "adapters/hex64-v1",
    max_steps: int = 100,
    lora_rank: int = 16,
    learning_rate: float = 2e-4,
    batch_size: int = 2,
    use_4bit: bool = True
):
    """
    执行 LoRA 微调
    
    Args:
        model_path: 基础模型路径
        training_data_file: 训练数据文件路径
        adapter_path: 适配器保存路径
        max_steps: 最大训练步数
        lora_rank: LoRA 秩
        learning_rate: 学习率
        batch_size: 批次大小
        use_4bit: 是否使用 4 位量化
    """
    # 自动检测模型路径
    if model_path is None:
        base_dir = Path(__file__).parent.parent.parent
        models_dir = base_dir / 'models'
        
        # 查找第一个 Qwen3.5 模型
        for item in models_dir.iterdir():
            if item.is_dir() and 'qwen3.5' in item.name.lower():
                model_path = str(item)
                break
    
    if model_path is None:
        raise FileNotFoundError(
            "未找到模型\n"
            "请指定 model_path 参数，或确保 models/ 目录下有 Qwen3.5 模型"
        )
    
    # 自动检测训练数据路径
    if training_data_file is None:
        base_dir = Path(__file__).parent.parent.parent
        training_data_file = str(base_dir / 'data' / 'train_hex64.jsonl')
    
    print(f"\n=== Hex64 QLoRA 微调 ===")
    print(f"基础模型: {model_path}")
    print(f"训练数据: {training_data_file}")
    print(f"适配器输出: {adapter_path}")
    print("="*60 + "\n")
    
    # 加载训练数据
    training_data = load_training_data(training_data_file)
    
    if not training_data:
        print("训练数据为空，无法开始微调")
        return
    
    print(f"加载 {len(training_data)} 条训练样本\n")
    
    # 导入标准 peft + transformers
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
        from datasets import Dataset
    except ImportError as e:
        print(f"缺少必要依赖: {e}")
        print("请运行: pip install torch transformers peft trl datasets accelerate bitsandbytes")
        return
    
    # 加载模型和 tokenizer
    print("加载模型...")
    max_seq_length = 2048
    
    if use_4bit:
        print("  使用 4 位量化（节省显存）")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
    else:
        print("  使用全精度（需要更大显存）")
        quantization_config = None
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    # 为 kbit 训练准备模型
    if use_4bit:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    
    # 配置 LoRA
    print("添加 LoRA 适配器...")
    lora_config = LoraConfig(
        r=lora_rank,
        lora_alpha=lora_rank * 2,
        lora_dropout=0.0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # 准备训练数据
    print("准备训练数据...")
    
    def format_messages(messages):
        """格式化消息为 ChatML 格式"""
        return tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
    
    formatted_data = [format_messages(item["messages"]) for item in training_data]
    dataset = Dataset.from_dict({"text": formatted_data})
    
    # 配置训练器
    print("配置训练器...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        packing=True,
        args={
            "per_device_train_batch_size": batch_size,
            "gradient_accumulation_steps": 4,
            "warmup_steps": 5,
            "max_steps": max_steps,
            "learning_rate": learning_rate,
            "fp16": not use_4bit,
            "bf16": use_4bit,
            "logging_steps": 10,
            "optim": "adamw_8bit",
            "weight_decay": 0.01,
            "lr_scheduler_type": "linear",
            "seed": 3407,
            "output_dir": adapter_path,
            "save_steps": max_steps // 2,
            "save_total_limit": 2,
        }
    )
    
    # 开始训练
    print("\n开始训练...")
    print(f"   总步数: {max_steps}")
    print(f"   批次大小: {batch_size}")
    print(f"   学习率: {learning_rate}\n")
    
    trainer.train()
    
    # 保存适配器
    print(f"\n保存适配器到 {adapter_path}...")
    os.makedirs(adapter_path, exist_ok=True)
    
    model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    
    # 计算适配器大小
    adapter_size_mb = 0
    for root, dirs, files in os.walk(adapter_path):
        for file in files:
            adapter_size_mb += os.path.getsize(os.path.join(root, file))
    adapter_size_mb /= (1024 * 1024)
    
    print("\n" + "="*60)
    print("微调完成！")
    print(f"   适配器大小: {adapter_size_mb:.1f} MB")
    print(f"   保存路径: {adapter_path}")
    print(f"   加载命令: model.load_adapter('{adapter_path}')")
    print("="*60 + "\n")
    
    # 测试推理
    print("测试微调后的模型...")
    test_input = "系统 CPU 过载了"
    
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
    print(f"\n输入: {test_input}")
    print(f"输出:\n{response}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hex64 QLoRA 微调工具')
    parser.add_argument('--model', type=str, help='基础模型路径')
    parser.add_argument('--data', type=str, help='训练数据文件路径')
    parser.add_argument('--output', type=str, default='adapters/hex64-v1',
                       help='适配器输出路径')
    parser.add_argument('--steps', type=int, default=100, help='训练步数')
    parser.add_argument('--rank', type=int, default=16, help='LoRA 秩')
    parser.add_argument('--lr', type=float, default=2e-4, help='学习率')
    parser.add_argument('--batch-size', type=int, default=2, help='批次大小')
    parser.add_argument('--no-4bit', action='store_true', help='不使用 4 位量化')
    
    args = parser.parse_args()
    
    try:
        train_lora(
            model_path=args.model,
            training_data_file=args.data,
            adapter_path=args.output,
            max_steps=args.steps,
            lora_rank=args.rank,
            learning_rate=args.lr,
            batch_size=args.batch_size,
            use_4bit=not args.no_4bit
        )
    except Exception as e:
        print(f"\n训练失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
