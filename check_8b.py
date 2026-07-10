"""Check Qwen3-8B and 0.8B model configs"""
from modelscope import snapshot_download
import json
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

test_models = [
    "Qwen/Qwen3-8B",
    "Qwen/Qwen3.5-0.8B",
]

for model_id in test_models:
    print(f"\n{'='*60}")
    print(f"Checking: {model_id}")
    print('='*60)
    
    try:
        cache_dir = snapshot_download(model_id, allow_patterns="config.json")
        config_path = f"{cache_dir}/config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"architectures: {config.get('architectures')}")
        print(f"model_type: {config.get('model_type')}")
        
        is_vl = 'vision_config' in config or 'image_token_id' in config or 'video_token_id' in config
        print(f"Is multimodal (VL): {is_vl}")
        print(f"Is text-only: {not is_vl}")
        
        if not is_vl:
            print("\n✅ 适合 LoRA 训练（纯文本）")
        else:
            print("\n⚠️  多模态模型，需要特殊处理")
        
    except Exception as e:
        print(f"Error: {e}")
