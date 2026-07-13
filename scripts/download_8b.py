"""Download Qwen3-8B BF16 model from ModelScope"""
from modelscope import snapshot_download
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

model_id = "Qwen/Qwen3-8B"
local_dir = "models/qwen3-8b"

print(f"\n{'='*60}")
print(f"Downloading: {model_id}")
print(f"To: {local_dir}")
print('='*60 + '\n')

try:
    cache_dir = snapshot_download(
        model_id,
        local_dir=local_dir,
        cache_dir=None  # Use default cache
    )
    print(f"\n✅ Download complete!")
    print(f"Model directory: {cache_dir}")
    
    # List downloaded files
    import os
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(local_dir):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
                file_count += 1
    
    print(f"Total files: {file_count}")
    print(f"Total size: {total_size / (1024**3):.2f} GB")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
