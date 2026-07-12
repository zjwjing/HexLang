#!/usr/bin/env python3
"""
Hex64 训练中断恢复脚本

功能：
1. 自动检测最近的 checkpoint
2. 从 checkpoint 恢复训练状态
3. 验证 checkpoint 完整性
4. 支持自动触发重训（反馈闭环）

使用方式：
    # 从最新 checkpoint 恢复
    python scripts/resume_training.py --adapter adapters/hex64-v2
    
    # 指定 checkpoint 步骤
    python scripts/resume_training.py --adapter adapters/hex64-v2 --resume-step 150
    
    # 自动触发重训（从 feedback.json 检测新数据）
    python scripts/resume_training.py --auto-retrain
"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TrainingResumer:
    """训练中断恢复器"""
    
    def __init__(self, adapter_path="adapters/hex64-v2", resume_step=None):
        self.adapter_path = Path(adapter_path)
        self.resume_step = resume_step
        self.checkpoint_dir = None
        self.latest_checkpoint = None
        self.training_state = None
        
    def find_latest_checkpoint(self):
        """查找最新的 checkpoint"""
        print("\n[步骤 1] 查找最新 checkpoint...")
        
        if not self.adapter_path.exists():
            print(f"❌ Adapter 目录不存在: {self.adapter_path}")
            return False
        
        # 查找 checkpoint-* 目录
        checkpoints = sorted([
            d for d in self.adapter_path.iterdir()
            if d.is_dir() and d.name.startswith('checkpoint-')
        ], key=lambda x: int(x.name.split('-')[1]))
        
        if not checkpoints:
            print("⚠️  未找到 checkpoint，将从头开始训练")
            return False
        
        self.latest_checkpoint = checkpoints[-1]
        self.resume_step = int(self.latest_checkpoint.name.split('-')[1])
        
        print(f"✅ 找到最新 checkpoint: {self.latest_checkpoint.name}")
        print(f"   步骤: {self.resume_step}")
        
        # 检查 checkpoint 完整性
        return self.validate_checkpoint(self.latest_checkpoint)
    
    def validate_checkpoint(self, checkpoint_path):
        """验证 checkpoint 完整性"""
        print(f"\n[步骤 2] 验证 checkpoint 完整性...")
        
        required_files = [
            "pytorch_model.bin",
            "trainer_state.json",
            "training_args.bin",
        ]
        
        all_valid = True
        for file_name in required_files:
            file_path = checkpoint_path / file_name
            if file_path.exists():
                size_mb = file_path.stat().st_size / 1024 / 1024
                print(f"  ✅ {file_name}: {size_mb:.1f} MB")
            else:
                print(f"  ❌ {file_name}: 缺失")
                all_valid = False
        
        # 加载训练状态
        trainer_state_file = checkpoint_path / "trainer_state.json"
        if trainer_state_file.exists():
            with open(trainer_state_file, 'r', encoding='utf-8') as f:
                self.training_state = json.load(f)
            
            print(f"\n[训练状态]")
            print(f"  当前步数: {self.training_state.get('global_step', 'N/A')}")
            print(f"  总步数: {self.training_state.get('total_flos', 'N/A')}")
            print(f"  最佳损失: {self.training_state.get('best_loss', 'N/A')}")
            
            # 检查是否已完成
            if self.training_state.get('state', {}).get('global_step', 0) > 0:
                print(f"  上次训练进度: {self.training_state['state']['global_step']} 步")
        else:
            print(f"  ⚠️  trainer_state.json 缺失")
            all_valid = False
        
        return all_valid
    
    def prepare_resume_config(self):
        """准备恢复训练的配置文件"""
        print(f"\n[步骤 3] 准备恢复配置...")
        
        config = {
            "resume_from_checkpoint": str(self.latest_checkpoint),
            "resume_step": self.resume_step,
            "timestamp": datetime.now().isoformat(),
            "adapter_path": str(self.adapter_path),
        }
        
        config_file = self.adapter_path / "resume_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 恢复配置已保存到: {config_file}")
        return config
    
    def auto_retrain_trigger(self):
        """自动触发重训（从 feedback.json 检测新数据）"""
        print(f"\n[步骤 4] 检查是否需要自动重训...")
        
        feedback_file = Path("data/feedback.json")
        if not feedback_file.exists():
            print("  ⚠️  feedback.json 不存在")
            return False
        
        with open(feedback_file, 'r', encoding='utf-8') as f:
            try:
                feedbacks = json.load(f)
            except:
                feedbacks = []
        
        if len(feedbacks) == 0:
            print("  ℹ️  无新反馈数据")
            return False
        
        # 检查是否有新的反馈（与上次训练后积累的）
        last_train_time = None
        if self.training_state:
            last_train_time = self.training_state.get('event_data', {}).get('trainer_save', {}).get('time', 0)
        
        new_feedbacks = []
        for fb in feedbacks:
            if not isinstance(fb, dict):
                continue
            ts = fb.get('timestamp', '')
            if last_train_time:
                if ts > str(last_train_time):
                    new_feedbacks.append(fb)
            else:
                new_feedbacks.append(fb)
        
        if new_feedbacks:
            print(f"  ✅ 发现 {len(new_feedbacks)} 条新反馈，触发自动重训")
            return True
        else:
            print("  ℹ️  无新反馈数据，无需重训")
            return False
    
    def run_resume(self):
        """执行恢复流程"""
        print("\n" + "="*60)
        print("Hex64 训练中断恢复")
        print("="*60 + "\n")
        
        # 1. 查找 checkpoint
        if not self.find_latest_checkpoint():
            print("\n⚠️  无法找到有效 checkpoint，建议从头开始训练")
            print("运行: python src/training/train_lora.py")
            return False
        
        # 2. 准备配置
        config = self.prepare_resume_config()
        
        # 3. 检查自动重训
        should_retrain = self.auto_retrain_trigger()
        
        # 4. 生成恢复命令
        print(f"\n[步骤 5] 恢复训练命令:")
        print(f"python src/training/train_lora.py \\")
        print(f"    --model models/qwen3.5-9b \\")
        print(f"    --data data/train_hex64.jsonl \\")
        print(f"    --output {self.adapter_path} \\")
        print(f"    --resume-from-checkpoint {self.latest_checkpoint} \\")
        print(f"    --resume-step {self.resume_step}")
        
        if should_retrain:
            print(f"\n🔄 检测到新反馈数据，建议先重新生成训练数据:")
            print(f"python src/training/prepare_data.py")
        
        print(f"\n{'='*60}")
        print(f"✅ 恢复准备完成")
        print(f"   从步骤 {self.resume_step} 继续训练")
        print(f"   Checkpoint: {self.latest_checkpoint}")
        print(f"{'='*60}\n")
        
        return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Hex64 训练中断恢复工具")
    parser.add_argument("--adapter", type=str, default="adapters/hex64-v2",
                       help="Adapter 路径")
    parser.add_argument("--resume-step", type=int, default=None,
                       help="指定恢复的步骤（默认使用最新 checkpoint）")
    parser.add_argument("--auto-retrain", action="store_true",
                       help="自动检测新反馈并触发重训")
    parser.add_argument("--validate-only", action="store_true",
                       help="仅验证 checkpoint 完整性，不准备恢复")
    
    args = parser.parse_args()
    
    resumer = TrainingResumer(
        adapter_path=args.adapter,
        resume_step=args.resume_step
    )
    
    if args.validate_only:
        # 仅验证模式
        print("仅验证 checkpoint 完整性...")
        success = resumer.find_latest_checkpoint()
        sys.exit(0 if success else 1)
    else:
        success = resumer.run_resume()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
