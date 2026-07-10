"""Search for correct Qwen3.5-9B-Instruct model on ModelScope"""
from modelscope.hub.api import HubApi
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

api = HubApi()

# Try different search approaches
print("Searching for Qwen3.5-9B-Instruct on ModelScope...")

# Method 1: List all revisions for potential model IDs
test_ids = [
    "Qwen/Qwen3.5-9B-Instruct",
    "Qwen/Qwen3.5-9B",
    "qwen/Qwen3.5-9B-Instruct",
    "Qwen/Qwen3-9B-Instruct",
    "Qwen/Qwen3.5-9B-Base",
]

for model_id in test_ids:
    try:
        revisions = api.list_model_revisions(model_id)
        print(f"✅ Found: {model_id} - {len(list(revisions))} revisions")
    except Exception as e:
        print(f"❌ Not found: {model_id} - {type(e).__name__}: {str(e)[:100]}")
