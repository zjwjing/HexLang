"""
训练监控脚本 - 检查 GPU 和训练进度
"""
import subprocess
import os
import time
from pathlib import Path

def check_gpu():
    """检查 GPU 状态"""
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    for line in lines[5:10]:
        if 'python' in line.lower() or '5060' in line:
            print(line.strip())

def check_checkpoint_dir():
    """检查 checkpoint 目录"""
    base = Path('adapters/hex64-qwen3-8b-final')
    if base.exists():
        files = sorted(base.glob('checkpoint-*'), key=os.path.getmtime, reverse=True)
        if files:
            print(f"\n最新 checkpoints ({len(files)} 个):")
            for f in files[:3]:
                size = sum(f.stat().st_size for p in f.rglob('*'))
                print(f"  {f.name}: {size/1e6:.1f} MB")
        else:
            print("\n尚无 checkpoint 保存")
            
        # 检查 trainer 状态
        trainer_state = base / 'trainer_state.json'
        if trainer_state.exists():
            import json
            with open(trainer_state) as f:
                state = json.load(f)
            print(f"\n训练状态:")
            print(f"  当前步骤: {state.get('global_step', 'N/A')}")
            print(f"  总步数: {state.get('total_flos', 'N/A')}")
            train_history = state.get('train_metrics', [])
            if train_history:
                last = train_history[-1]
                print(f"  最近 loss: {last.get('loss', 'N/A')}")

if __name__ == '__main__':
    print("=== 训练监控 ===")
    check_gpu()
    check_checkpoint_dir()
