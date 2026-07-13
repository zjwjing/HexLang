"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing
MIT License

Hex64 LoRA 微调脚本（带 64 维卦分布辅助损失）
基于 bagau-llm 思路：在主损失（Causal LM）之外，增加辅助损失预测输入对应的 64 维卦分布

使用方式：
    python src/training/train_lora_with_aux_loss.py \
        --model models/qwen3-8b \
        --data data/train_hex64.jsonl \
        --aux-weight 0.3 \
        --output adapters/hex64-v3-aux
"""

import sys, json, os, torch
from pathlib import Path
from typing import Dict, List, Tuple

if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Hex64AuxLossDataset(torch.utils.data.Dataset):
    """带辅助损失的 Hex64 训练数据集
    
    每条样本包含：
    - text: 对话文本（用于主损失 Causal LM）
    - target_index: 目标卦索引 0-63（用于辅助损失）
    - one_hot: 64 维 one-hot 向量
    """
    
    def __init__(self, data_path: str, encoder):
        self.encoder = encoder
        self.samples = []
        
        print(f"加载训练数据: {data_path}")
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    messages = item.get('messages', [])
                    if len(messages) < 3:
                        continue
                    
                    # 从用户输入提取卦象索引
                    user_input = messages[1]['content']
                    
                    # 从 assistant response 中提取卦名
                    assistant_response = messages[2]['content']
                    hex_name = self._extract_hex_name(assistant_response)
                    
                    if hex_name:
                        hex_result = self.encoder.encode(user_input)
                        # 验证编码器预测是否与标注一致
                        predicted_name = hex_result['hex_name']
                        is_consistent = (predicted_name == hex_name)
                        
                        self.samples.append({
                            'messages': messages,
                            'target_name': hex_name,
                            'target_index': self.encoder.name_to_hex.get(hex_name, 0),
                            'is_consistent': is_consistent,
                        })
                except Exception:
                    continue
        
        print(f"共 {len(self.samples)} 条有效样本")
        consistent = sum(1 for s in self.samples if s['is_consistent'])
        print(f"其中 {consistent}/{len(self.samples)} 条与编码器一致 ({consistent/len(self.samples)*100:.1f}%)")
    
    def _extract_hex_name(self, response: str) -> str:
        """从 [Hex64 溯源：卦名(bin)] 格式提取卦名"""
        import re
        match = re.search(r'[Hex64\s+溯源[：:]\s*([^\(]+)', response)
        if match:
            return match.group(1).strip()
        return ""
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        return self.samples[idx]


def train_lora_with_aux_loss(
    model_path="models/qwen3-8b",
    data_path="data/train_hex64.jsonl",
    output_dir="adapters/hex64-v3-aux",
    steps=300,
    lora_rank=32,
    lr=3e-4,
    batch_size=2,
    aux_weight=0.3,  # 辅助损失权重
):
    print(f"\n=== Hex64 LoRA 微调 (带 64 维卦分布辅助损失) ===")
    print(f"模型: {model_path}")
    print(f"数据: {data_path}")
    print(f"输出: {output_dir}")
    print(f"步数: {steps} | Rank: {lora_rank} | LR: {lr} | Batch: {batch_size}")
    print(f"辅助损失权重: {aux_weight}")
    print("=" * 60)

    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model
    from trl import SFTTrainer, SFTConfig
    from datasets import Dataset
    from src.core.encoder import Hex64Encoder
    
    # 1. 加载编码器和 tokenizer
    print("\n[步骤 1] 加载 Hex64 编码器...")
    encoder = Hex64Encoder()
    
    print("[步骤 2] 加载 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
        padding_side='left'
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. 加载 INT4 量化模型
    print("[步骤 3] 加载模型（INT4 NF4）...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map='auto',
        trust_remote_code=True,
    )
    model.eval()

    # 3. 加 LoRA 适配器
    print("[步骤 4] 添加 LoRA 适配器...")
    lora_config = LoraConfig(
        r=lora_rank,
        lora_alpha=lora_rank,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 4. 加载训练数据
    print("[步骤 5] 准备训练数据...")
    dataset = Hex64AuxLossDataset(data_path, encoder)
    
    # 转换为对话格式
    def format_conversation(examples):
        texts = []
        for msgs in examples['messages']:
            text = tokenizer.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=False
            )
            texts.append(text)
        return {"text": texts}
    
    # 创建 HuggingFace Dataset
    hf_dataset = Dataset.from_list([{
        'messages': s['messages'],
        'target_index': s['target_index'],
    } for s in dataset.samples])
    hf_dataset = hf_dataset.map(format_conversation, batched=True, remove_columns=hf_dataset.column_names)

    # 5. 配置辅助损失模块
    print("[步骤 6] 配置辅助损失模块...")
    
    class AuxLossTrainer(SFTTrainer):
        """带辅助损失的 Trainer"""
        
        def __init__(self, *args, aux_weight=0.3, **kwargs):
            super().__init__(*args, **kwargs)
            self.aux_weight = aux_weight
            
            # 辅助分类头：隐藏层维度 → 64
            hidden_size = model.config.hidden_size
            self.aux_classifier = torch.nn.Sequential(
                torch.nn.Linear(hidden_size, hidden_size // 2),
                torch.nn.ReLU(),
                torch.nn.Dropout(0.1),
                torch.nn.Linear(hidden_size // 2, 64),
            )
            self.aux_classifier.to(model.device)
            
            # 将分类头注册为可训练参数
            self.trainable_aux_params = list(self.aux_classifier.parameters())
            for p in self.trainable_aux_params:
                p.requires_grad = True
        
        def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
            # 1. 主损失：Causal LM
            outputs = model(**inputs)
            lm_loss = outputs.loss
            
            # 2. 辅助损失：从最后隐藏状态提取卦象预测
            # 取最后一个 token 的隐藏状态
            last_hidden = outputs.last_hidden_state  # [B, L, H]
            aux_input = last_hidden[:, -1, :]  # [B, H]
            
            aux_logits = self.aux_classifier(aux_input)  # [B, 64]
            
            # 从 inputs 中获取目标索引
            target_indices = inputs.pop('target_indices', None)
            if target_indices is not None:
                target_indices = target_indices.to(model.device)
                aux_loss = torch.nn.functional.cross_entropy(aux_logits, target_indices)
            else:
                aux_loss = torch.tensor(0.0, device=model.device)
            
            # 3. 总损失 = 主损失 + aux_weight * 辅助损失
            total_loss = lm_loss + self.aux_weight * aux_loss
            
            if return_outputs:
                return (total_loss, outputs)
            return total_loss
        
        def prepare_model_inputs(self, batch):
            """扩展 batch 以包含 target_indices"""
            inputs = {
                'input_ids': batch['input_ids'],
                'attention_mask': batch['attention_mask'],
            }
            if 'target_indices' in batch:
                inputs['target_indices'] = torch.tensor(batch['target_indices'])
            return inputs
    
    # 6. 配置训练参数
    print("[步骤 7] 配置训练参数...")
    training_args = SFTConfig(
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
        bf16=False,
        fp16=True,
        output_dir=output_dir,
        report_to="none",
        seed=3407,
    )

    trainer = AuxLossTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=hf_dataset,
        args=training_args,
        aux_weight=aux_weight,
    )

    # 7. 开始训练
    print("\n" + "=" * 60)
    print("🚀 开始训练（含 64 维卦分布辅助损失）")
    print("=" * 60 + "\n")
    trainer.train()

    # 8. 保存适配器和辅助分类头
    print(f"\n保存适配器到 {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # 保存辅助分类头
    aux_path = os.path.join(output_dir, "aux_classifier.pt")
    torch.save({
        'classifier_state_dict': trainer.aux_classifier.state_dict(),
        'aux_weight': aux_weight,
    }, aux_path)
    print(f"辅助分类头已保存到: {aux_path}")
    print("✅ 训练完成！")
    
    # 打印适配器大小
    adapter_file = os.path.join(output_dir, "adapter_model.safetensors")
    if os.path.exists(adapter_file):
        size_mb = os.path.getsize(adapter_file) / 1024 / 1024
        print(f"   适配器大小: {size_mb:.1f} MB")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Hex64 LoRA 微调 (带辅助损失)')
    parser.add_argument('--model', type=str, default="models/qwen3-8b",
                       help='基座模型路径')
    parser.add_argument('--data', type=str, default="data/train_hex64.jsonl",
                       help='训练数据路径')
    parser.add_argument('--output', type=str, default='adapters/hex64-v3-aux',
                       help='适配器输出路径')
    parser.add_argument('--steps', type=int, default=300,
                       help='训练步数')
    parser.add_argument('--rank', type=int, default=32,
                       help='LoRA rank')
    parser.add_argument('--lr', type=float, default=3e-4,
                       help='学习率')
    parser.add_argument('--batch-size', type=int, default=2,
                       help='每设备 batch size')
    parser.add_argument('--aux-weight', type=float, default=0.3,
                       help='辅助损失权重 (默认 0.3)')
    args = parser.parse_args()

    train_lora_with_aux_loss(
        model_path=args.model,
        data_path=args.data,
        output_dir=args.output,
        steps=args.steps,
        lora_rank=args.rank,
        lr=args.lr,
        batch_size=args.batch_size,
        aux_weight=args.aux_weight,
    )
