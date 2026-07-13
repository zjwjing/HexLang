"""List available Qwen3.5 models on ModelScope"""
from modelscope.hub.api import HubApi
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api = HubApi()

# Try various model IDs that might exist
test_ids = [
    "Qwen/Qwen3.5-2B",
    "Qwen/Qwen3.5-2B-Instruct",
    "Qwen/Qwen3.5-0.5B",
    "Qwen/Qwen3.5-0.5B-Instruct",
    "Qwen/Qwen3.5-1.7B",
    "Qwen/Qwen3.5-1.7B-Instruct",
    "Qwen/Qwen3-8B",
    "Qwen/Qwen3-8B-Instruct",
    "Qwen/Qwen3-14B",
    "Qwen/Qwen3-14B-Instruct",
]

print("Checking available Qwen3.5 models on ModelScope...\n")
available = []

for model_id in test_ids:
    try:
        revisions = list(api.list_model_revisions(model_id))
        print(f"✅ {model_id} - {len(revisions)} revisions")
        available.append(model_id)
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "404" in error_msg:
            print(f"❌ {model_id} - NOT FOUND")
        else:
            print(f"⚠️  {model_id} - {type(e).__name__}: {error_msg[:80]}")

print(f"\n\nAvailable models: {available}")
