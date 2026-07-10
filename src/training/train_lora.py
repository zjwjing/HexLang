"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing
MIT License

Hex64 QLoRA 微调脚本（Unsloth BF16 版）
使用 unsloth + trl 对 Qwen3.5-9B 进行 BF16 LoRA 微调
"""

import sys, json, os, torch
from pathlib import Path

if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def train_lora(model_path="models/unsloth_Qwen3.5-9B",
               data_path="data/train_hex64.jsonl",
               output_dir="adapters/hex64-v1",
               steps=300, lora_rank=32, lr=3e-4, batch_size=2):

    print(f"\n=== Hex64 LoRA 微调 (Unsloth BF16) ===")
    print(f"模型: {model_path}")
    print(f"数据: {data_path}")
    print(f"输出: {output_dir}")
    print(f"步数: {steps} | Rank: {lora_rank} | LR: {lr} | Batch: {batch_size}")
    print("=" * 60)

    from unsloth import FastLanguageModel
    from unsloth.chat_templates import get_chat_template, train_on_responses_only
    from trl import SFTTrainer, SFTConfig
    from datasets import Dataset

    # 1. 加载 BF16 模型（不用 4bit，避开量化兼容问题）
    print("加载模型...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=8192,
        dtype=torch.bfloat16,
        load_in_4bit=False,
        full_finetuning=False,
    )

    # 2. 加 LoRA 适配器
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

    # 3. 使用 qwen3-thinking 模板
    tokenizer = get_chat_template(tokenizer, chat_template="qwen3-thinking")

    # 4. 加载训练数据
    print(f"加载训练数据: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = [json.loads(line) for line in f if line.strip()]
    print(f"共 {len(raw_data)} 条样本")

    # 转换成 Unsloth 格式
    formatted = []
    for item in raw_data:
        msgs = item.get("messages", [])
        conv = [{"from": "system", "value": msgs[0]["content"]},
                {"from": "user", "value": msgs[1]["content"]},
                {"from": "assistant", "value": msgs[2]["content"]}]
        formatted.append({"conversations": conv})

    dataset = Dataset.from_list(formatted)

    def format_prompt(examples):
        texts = [tokenizer.apply_chat_template(c, tokenize=False, add_generation_prompt=False)
                 for c in examples["conversations"]]
        return {"text": texts}

    dataset = dataset.map(format_prompt, batched=True)

    # 5. 配置训练
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="text",
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
        ),
    )

    # 6. Response-Only Training
    trainer = train_on_responses_only(
        trainer,
        instruction_part="<|im_start|>user\n",
        response_part="<|im_start|>assistant\n",
    )

    # 7. 开始训练
    print("\n开始训练...")
    trainer.train()

    # 8. 保存适配器
    print(f"\n保存适配器到 {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("训练完成！")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, help='模型路径')
    parser.add_argument('--data', type=str, help='数据路径')
    parser.add_argument('--output', type=str, default='adapters/hex64-v1')
    parser.add_argument('--steps', type=int, default=300)
    parser.add_argument('--rank', type=int, default=32)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--batch-size', type=int, default=2)
    args = parser.parse_args()

    train_lora(
        model_path=args.model or "models/unsloth_Qwen3.5-9B",
        data_path=args.data or "data/train_hex64.jsonl",
        output_dir=args.output,
        steps=args.steps,
        lora_rank=args.rank,
        lr=args.lr,
        batch_size=getattr(args, 'batch_size', 2),
    )