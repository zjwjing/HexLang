"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing
MIT License

Hex64 QLoRA 微调脚本（原生 PEFT 版，绕过 Unsloth）
使用 transformers + peft + trl 对 Qwen3-8B 进行 INT4 LoRA 微调
彻底避开 Unsloth + triton 3.x 兼容问题
"""

import sys, json, torch
from pathlib import Path

if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def train_lora(model_path="models/qwen3-8b",
               data_path="data/train_hex64.jsonl",
               output_dir="adapters/hex64-v2",
               steps=300, lora_rank=32, lr=3e-4, batch_size=2):

    print(f"\n=== Hex64 LoRA 微调 (原生 PEFT + INT4) ===")
    print(f"模型: {model_path}")
    print(f"数据: {data_path}")
    print(f"输出: {output_dir}")
    print(f"步数: {steps} | Rank: {lora_rank} | LR: {lr} | Batch: {batch_size}")
    print("=" * 60)

    # 1. 加载 tokenizer
    print("1. 加载 tokenizer...")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, trust_remote_code=True, padding_side="right"
    )
    if tokenizer.eos_token is None:
        tokenizer.eos_token = "</s>"
    print(f"   vocab_size={tokenizer.vocab_size}")

    # 2. 加载模型（INT4 量化）
    print("2. 加载模型 (INT4 Quantized)...")
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False
    print(f"   VRAM: {torch.cuda.memory_allocated()/1e9:.1f} GB")

    # 3. 加 LoRA 适配器
    print("3. 添加 LoRA 适配器...")
    from peft import LoraConfig, get_peft_model

    lora_cfg = LoraConfig(
        r=lora_rank,
        lora_alpha=lora_rank,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    model = get_peft_model(model, lora_cfg)
    model.enable_input_require_grads()
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Trainable: {trainable_params:,} / {total_params:,} ({100*trainable_params/total_params:.2f}%)")

    # 4. 加载训练数据
    print(f"4. 加载训练数据: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = [json.loads(line) for line in f if line.strip()]
    print(f"   共 {len(raw_data)} 条样本")

    # 转换成对话格式
    conversations = []
    for item in raw_data:
        msgs = item.get("messages", [])
        if len(msgs) < 3:
            continue
        conv = [
            {"role": "system", "content": msgs[0]["content"]},
            {"role": "user", "content": msgs[1]["content"]},
            {"role": "assistant", "content": msgs[2]["content"]},
        ]
        conversations.append(conv)
    print(f"   有效对话: {len(conversations)} 条")

    # 5. 格式化文本
    print("5. 格式化对话文本...")
    texts = [tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=False)
             for conv in conversations]
    print(f"   格式化后: {len(texts)} 条")

    from datasets import Dataset
    dataset = Dataset.from_dict({"text": texts})

    # 6. 配置训练
    print("6. 配置训练参数...")
    from trl import SFTTrainer, SFTConfig

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="text",
            max_length=4096,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
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
            remove_unused_columns=False,
        ),
    )

    # 7. 开始训练
    print("\n=== 开始训练 ===")
    trainer.train()

    # 8. 保存适配器
    print(f"\n保存适配器到 {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("训练完成！")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default="models/qwen3-8b")
    parser.add_argument('--data', type=str, default="data/train_hex64.jsonl")
    parser.add_argument('--output', type=str, default='adapters/hex64-v2')
    parser.add_argument('--steps', type=int, default=300)
    parser.add_argument('--rank', type=int, default=32)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--batch-size', type=int, default=2)
    args = parser.parse_args()

    train_lora(
        model_path=args.model,
        data_path=args.data,
        output_dir=args.output,
        steps=args.steps,
        lora_rank=args.rank,
        lr=args.lr,
        batch_size=getattr(args, 'batch_size', 2),
    )
