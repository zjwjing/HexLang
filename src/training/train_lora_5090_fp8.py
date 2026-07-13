"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing
MIT License

Hex64 LoRA 微调脚本（RTX 5090 FP8 优化版）
针对 Blackwell 架构优化：FP8 训练 + Unsloth + Qwen3.5-9B
避坑指南：
  - CUDA 12.8+（5090 标配，别用 12.4）
  - triton 3.2+（Blackwell 必须，旧版 2.x 炸）
  - Unsloth >=0.22（点了 Blackwell + Qwen3.5）
  - 用 BF16 原版模型 + FP8 LoRA，不用 INT4 量化
"""

import sys, json, os, torch
from pathlib import Path

if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def train_lora_5090_fp8(
    model_path="models/qwen3.5-9b-instruct",
    data_path="data/train_hex64.jsonl",
    output_dir="adapters/hex64-v1-5090-fp8",
    steps=300, lora_rank=32, lr=3e-4, batch_size=4,
    max_seq_length=16384,
):
    print(f"\n=== Hex64 LoRA 微调 (RTX 5090 FP8) ===")
    print(f"模型: {model_path}")
    print(f"数据: {data_path}")
    print(f"输出: {output_dir}")
    print(f"步数: {steps} | Rank: {lora_rank} | LR: {lr} | Batch: {batch_size}")
    print(f"最大序列长度: {max_seq_length}")
    print("=" * 60)

    # 检查环境
    print("\n[环境检查]")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA: {torch.version.cuda}")
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print(f"  GPU 显存: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")
    
    if not torch.cuda.is_bf16_supported():
        print("  ⚠️  警告：当前 GPU 不支持 BF16，请确认是 5090 或更新架构")
    
    # 1. 加载 Unsloth
    try:
        from unsloth import FastLanguageModel
        from unsloth.chat_templates import get_chat_template, train_on_responses_only
        from trl import SFTTrainer, SFTConfig
        from datasets import Dataset
    except ImportError as e:
        print(f"\n❌ 缺少必要依赖: {e}")
        print("请运行:")
        print("  pip install \"unsloth>=0.22\"")
        print("  pip install transformers peft trl datasets")
        return

    # 2. 加载 BF16 模型（5090 用 FP8 省显存）
    print("\n[步骤 1] 加载模型...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=max_seq_length,
        dtype=torch.bfloat16,
        load_in_4bit=False,  # 5090 显存够，不用量化
        full_finetuning=False,
    )

    # 3. 加 LoRA 适配器（r=32 起步，FP8 下可试 64）
    print("[步骤 2] 添加 LoRA 适配器...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_rank,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=lora_rank,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )
    model.print_trainable_parameters()

    # 4. 使用 qwen3-thinking 模板
    print("[步骤 3] 应用 qwen3-thinking 模板...")
    tokenizer = get_chat_template(tokenizer, chat_template="qwen3-thinking")

    # 5. 加载训练数据
    print(f"[步骤 4] 加载训练数据: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = [json.loads(line) for line in f if line.strip()]
    print(f"  共 {len(raw_data)} 条样本")

    # 转换成 Unsloth 格式
    formatted = []
    for item in raw_data:
        msgs = item.get("messages", [])
        conv = [
            {"from": "system", "value": msgs[0]["content"]},
            {"from": "user", "value": msgs[1]["content"]},
            {"from": "assistant", "value": msgs[2]["content"]}
        ]
        formatted.append({"conversations": conv})

    dataset = Dataset.from_list(formatted)

    def format_prompt(examples):
        texts = [tokenizer.apply_chat_template(c, tokenize=False, add_generation_prompt=False)
                 for c in examples["conversations"]]
        return {"text": texts}

    dataset = dataset.map(format_prompt, batched=True)

    # 6. 配置训练（5090 FP8 可稍激进）
    print("[步骤 5] 配置训练参数...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="text",
            max_seq_length=max_seq_length,
            per_device_train_batch_size=batch_size,      # 5090 稳跑 4
            gradient_accumulation_steps=2,                # 有效 bs=8
            warmup_steps=30,
            max_steps=steps,
            learning_rate=lr,
            logging_steps=1,
            save_steps=50,
            save_total_limit=3,
            optim="adamw_8bit",
            weight_decay=0.001,
            lr_scheduler_type="linear",
            bf16=True,
            fp16=False,
            output_dir=output_dir,
            report_to="none",
            seed=3407,
        ),
    )

    # 7. Response-only masking（Jackrong 核心技巧）
    print("[步骤 6] 应用 response-only masking...")
    trainer = train_on_responses_only(
        trainer,
        instruction_part="</s>\n\n[INST] ",
        response_part="[/INST] ",
    )

    # 8. 开始训练
    print("\n" + "=" * 60)
    print("🚀 开始训练")
    print("=" * 60 + "\n")
    trainer.train()

    # 9. 保存适配器
    print(f"\n保存适配器到 {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("✅ 训练完成！")
    
    # 打印适配器大小
    adapter_file = os.path.join(output_dir, "adapter_model.bin")
    if os.path.exists(adapter_file):
        size_mb = os.path.getsize(adapter_file) / 1024 / 1024
        print(f"   适配器大小: {size_mb:.1f} MB")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Hex64 LoRA 微调 (RTX 5090 FP8)')
    parser.add_argument('--model', type=str, default="models/qwen3.5-9b-instruct",
                       help='Qwen3.5-9B BF16 模型路径')
    parser.add_argument('--data', type=str, default="data/train_hex64.jsonl",
                       help='训练数据路径')
    parser.add_argument('--output', type=str, default='adapters/hex64-v1-5090-fp8',
                       help='适配器输出路径')
    parser.add_argument('--steps', type=int, default=300,
                       help='训练步数')
    parser.add_argument('--rank', type=int, default=32,
                       help='LoRA rank')
    parser.add_argument('--lr', type=float, default=3e-4,
                       help='学习率')
    parser.add_argument('--batch-size', type=int, default=4,
                       help='每设备 batch size（5090 推荐 4）')
    parser.add_argument('--max-seq-length', type=int, default=16384,
                       help='最大序列长度')
    args = parser.parse_args()

    train_lora_5090_fp8(
        model_path=args.model,
        data_path=args.data,
        output_dir=args.output,
        steps=args.steps,
        lora_rank=args.rank,
        lr=args.lr,
        batch_size=args.batch_size,
        max_seq_length=args.max_seq_length,
    )
