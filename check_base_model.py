"""Check Qwen3.5-9B base model config by downloading just config.json"""
from modelscope import snapshot_download
import json
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

model_id = "Qwen/Qwen3.5-9B"
print(f"Downloading config for: {model_id}")

# Download only config.json to check architecture
try:
    cache_dir = snapshot_download(model_id, allow_patterns="config.json")
    config_path = f"{cache_dir}/config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("\n=== Key config fields ===")
    for key in ['model_type', 'architectures', 'hidden_size', 'num_attention_heads', 
                'num_hidden_layers', 'text_config', 'vision_config', 'image_token_id', 'video_token_id']:
        if key in config:
            print(f"{key}: {json.dumps(config[key], indent=2)[:200]}")
    
    # Check if it's multimodal
    is_vl = 'vision_config' in config or 'image_token_id' in config or 'video_token_id' in config
    is_text_only = 'text_config' in config and not is_vl
    
    print(f"\nIs multimodal (VL): {is_vl}")
    print(f"Is text-only: {is_text_only}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
