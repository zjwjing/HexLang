"""
Hex64 QLoRA 微调脚本

使用 unsloth 库对 Qwen3.5-9B 进行 LoRA 微调
让模型学习 Hex64 的编码规则和输出格式

前置条件：
1. 已收集足够反馈数据（200+ 条）
2. 已运行 rules/induce_rules.py 生成训练数据
3. 显存 ≥8GB（INT4 量化）或 ≥20GB（FP16）

使用方式：
    python train_lora.py
    
输出：
    adapters/hex64-v1/ - LoRA 适配器权重（约 50MB）
"""

import os
import json
import torch
from pathlib import Path
from typing import List, Dict, Any


def load_training_data(data_file: str = None) -> List[Dict[str, Any]]:
    """
    加载训练数据
    
    Args:
        data_file: 训练数据文件路径
        
    Returns:
        训练数据列表
    """
    if data_file is None:
        base_dir = Path(__file__).parent.parent
        data_file = base_dir / 'data' / 'train_hex64.json'
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  训练数据文件不存在: {data_file}")
        print("💡 请先运行: python rules/induce_rules.py")
        return []
    except json.JSONDecodeError:
        print(f"❌ 训练数据文件格式错误: {data_file}")
        return []


def create_conversation_dataset(training_data: List[Dict[str, Any]]) -> List[str]:
    """
    将训练数据转换为对话格式文本
    
    Args:
        training_data: 训练数据列表
        
    Returns:
        对话文本列表
    """
    conversations = []
    
    for sample in training_data:
        messages = sample.get('messages', [])
        
        # 构建对话文本
        text_parts = []
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'user':
                text_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
            elif role == 'assistant':
                text_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")
            elif role == 'system':
                text_parts.append(f"<|im_start|>system\n{content}<|im_end|>")
        
        conversation = "\n".join(text_parts) + "\n"
        conversations.append(conversation)
    
    return conversations


def train_lora(
    model_path: str = None,
    training_data_file: str = None,
    adapter_path: str = "adapters/hex64-v1",
    max_epochs: int = 3,
    lora_rank: int = 16,
    learning_rate: float = 2e-4,
    batch_size: int = 4,
    use_4bit: bool = True
):
    """
    执行 LoRA 微调
    
    Args:
        model_path: 基础模型路径
        training_data_file: 训练数据文件路径
        adapter_path: 适配器保存路径
        max_epochs: 最大训练轮数
        lora_rank: LoRA 秩
        learning_rate: 学习率
        batch_size: 批次大小
        use_4bit: 是否使用 4 位量化
    """
    # 自动检测模型路径
    if model_path is None:
        base_dir = Path(__file__).parent.parent
        models_dir = base_dir / 'models'
        
        # 查找第一个 Qwen3.5 模型
        if models_dir.exists():
            for item in models_dir.iterdir():
                if item.is_dir() and 'qwen3.5' in item.name.lower():
                    model_path = str(item)
                    break
    
    if model_path is None:
        raise FileNotFoundError(
            "未找到模型\n"
            "请指定 model_path 参数，或确保 models/ 目录下有 Qwen3.5 模型"
        )
    
    print(f"\n=== Hex64 QLoRA 微调 ===")
    print(f"基础模型: {model_path}")
    print(f"训练数据: {training_data_file or 'data/train_hex64.json'}")
    print(f"适配器输出: {adapter_path}")
    print("="*60 + "\n")
    
    # 加载训练数据
    training_data = load_training_data(training_data_file)
    
    if not training_data:
        print("❌ 训练数据为空，无法开始微调")
        return
    
    print(f"✅ 加载 {len(training_data)} 条训练样本\n")
    
    # 尝试导入 unsloth
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from datasets import Dataset
    except ImportError:
        print("❌ 缺少必要依赖")
        print("请运行: pip install unsloth trl datasets")
        return
    
    # 加载模型
    print("🔄 加载模型...")
    max_seq_length = 2048
    dtype = None  # 自动检测
    
    if use_4bit:
        load_in_4bit = True
        print("  使用 4 位量化（节省显存）")
    else:
        load_in_4bit = False
        print("  使用全精度（需要更大显存）")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        dtype=dtype
    )
    
    # 添加 LoRA 适配器
    print("🔄 添加 LoRA 适配器...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_rank,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_alpha=lora_rank * 2,
        lora_dropout=0,  # 零 dropout（防止过拟合小数据集）
        bias="none",
        use_gradient_checkpointing="unsloth",
        use_rslora=True,
        loftq_config=None
    )
    
    model.print_trainable_parameters()
    
    # 准备训练数据
    print("🔄 准备训练数据...")
    conversations = create_conversation_dataset(training_data)
    
    dataset = Dataset.from_dict({"text": conversations})
    
    # 配置训练器
    print("🔄 配置训练器...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        packing=True,  # 打包多个样本
        args={
            "per_device_train_batch_size": batch_size,
            "gradient_accumulation_steps": 4,
            "warmup_steps": 5,
            "max_steps": max_epochs * len(dataset),
            "learning_rate": learning_rate,
            "fp16": not use_4bit,
            "bf16": use_4bit,
            "logging_steps": 10,
            "optim": "adamw_8bit",
            "weight_decay": 0.01,
            "lr_scheduler_type": "linear",
            "seed": 42,
        }
    )
    
    # 开始训练
    print("\n🚀 开始训练...")
    trainer.train()
    
    # 保存适配器
    print(f"\n💾 保存适配器到 {adapter_path}...")
    os.makedirs(adapter_path, exist_ok=True)
    
    model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    
    print("\n" + "="*60)
    print("✅ 微调完成！")
    print(f"   适配器大小: {os.path.getsize(os.path.join(adapter_path, 'adapter_model.bin')) / 1024 / 1024:.1f} MB")
    print(f"   加载命令: model.load_adapter('{adapter_path}')")
    print("="*60 + "\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hex64 QLoRA 微调工具')
    parser.add_argument('--model', type=str, help='基础模型路径')
    parser.add_argument('--data', type=str, help='训练数据文件路径')
    parser.add_argument('--output', type=str, default='adapters/hex64-v1',
                       help='适配器输出路径')
    parser.add_argument('--epochs', type=int, default=3, help='训练轮数')
    parser.add_argument('--rank', type=int, default=16, help='LoRA 秩')
    parser.add_argument('--lr', type=float, default=2e-4, help='学习率')
    parser.add_argument('--batch-size', type=int, default=4, help='批次大小')
    parser.add_argument('--no-4bit', action='store_true', help='不使用 4 位量化')
    
    args = parser.parse_args()
    
    try:
        train_lora(
            model_path=args.model,
            training_data_file=args.data,
            adapter_path=args.output,
            max_epochs=args.epochs,
            lora_rank=args.rank,
            learning_rate=args.lr,
            batch_size=args.batch_size,
            use_4bit=not args.no_4bit
        )
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
