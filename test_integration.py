"""测试集成 LoRA 适配器的 QwenLoader"""
import sys
import io

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*60)
print("测试 QwenLoader + LoRA 适配器集成")
print("="*60 + "\n")

try:
    from src.models.qwen_loader import QwenLoader
    
    print("1. 加载 QwenLoader（自动检测模型 + LoRA 适配器）...")
    loader = QwenLoader(adapter_path="adapters/hex64-v1")
    
    print("\n2. 测试 chat_with_history...")
    response = loader.chat_with_history(
        "系统 CPU 过载了",
        max_new_tokens=200,
        temperature=0.1,
        do_sample=False
    )
    
    print(f"\n输入: 系统 CPU 过载了")
    print(f"输出:\n{response}")
    print("\n" + "="*60)
    print("✅ 集成测试通过！")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
