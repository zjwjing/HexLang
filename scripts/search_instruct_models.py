"""Search for pure text Instruct models on ModelScope"""
from modelscope.hub.api import HubApi
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api = HubApi()

# Try various model IDs that might be pure text instruct versions
test_ids = [
    # Qwen3 series (pure text)
    "Qwen/Qwen3-8B-Base",
    "Qwen/Qwen3-14B-Base",
    "Qwen/Qwen3-32B",
    "Qwen/Qwen3-32B-Instruct",
    "Qwen/Qwen3-1.7B",
    "Qwen/Qwen3-1.7B-Instruct",
    "Qwen/Qwen3-4B",
    "Qwen/Qwen3-4B-Instruct",
    
    # GPTQ quantized versions
    "Qwen/Qwen3.5-0.8B-GPTQ-Int4",
    "Qwen/Qwen3-8B-GPTQ-Int4",
    
    # Alternative org names
    "qwen/Qwen3-8B",
    "qwen/Qwen3-8B-Instruct",
]

print("Searching for pure text Qwen models on ModelScope...\n")
available = []

for model_id in test_ids:
    try:
        revisions = list(api.list_model_revisions(model_id))
        print(f"✅ {model_id} - {len(revisions)} revisions")
        available.append(model_id)
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "404" in error_msg:
            pass  # silent skip
        else:
            print(f"⚠️  {model_id} - {type(e).__name__}: {error_msg[:80]}")

print(f"\n\nFound {len(available)} models:")
for m in available:
    print(f"  - {m}")
