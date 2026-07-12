import sys
import os
import json
import argparse
from pathlib import Path

# UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def merge_adapter(args):
    """合并 LoRA adapter 成完整模型"""
    print(f"\n{'='*60}")
    print("合并 LoRA Adapter")
    print(f"{'='*60}\n")
    
    base_model = Path(args.base_model)
    adapter = Path(args.adapter)
    output = Path(args.output)
    
    if not base_model.exists():
        print(f"❌ 基座模型不存在: {base_model}")
        return False
    
    if not adapter.exists():
        print(f"❌ Adapter 不存在: {adapter}")
        return False
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        import torch
        
        print(f"[1/5] 加载基座模型: {base_model}")
        tokenizer = AutoTokenizer.from_pretrained(
            base_model,
            trust_remote_code=True
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,
            device_map="cpu",
            trust_remote_code=True,
        )
        
        print(f"[2/5] 加载 Adapter: {adapter}")
        model = PeftModel.from_pretrained(model, adapter)
        
        print(f"[3/5] 合并模型...")
        model = model.merge_and_unload()
        
        print(f"[4/5] 保存合并后的模型到: {output}")
        output.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(output, safe_serialization=True)
        tokenizer.save_pretrained(output)
        
        total_size = sum(f.stat().st_size for f in output.glob("**/*.safetensors") if f.is_file())
        size_gb = total_size / 1024**3
        
        print(f"\n[5/5] ✅ 合并完成！")
        print(f"   输出目录: {output}")
        print(f"   模型大小: {size_gb:.2f} GB")
        return True
        
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False
    except Exception as e:
        print(f"❌ 合并失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def export_gguf(args):
    """导出 GGUF 格式"""
    print(f"\n{'='*60}")
    print("导出 GGUF 格式")
    print(f"{'='*60}\n")
    
    model_path = Path(args.model)
    output_path = Path(args.output)
    quantize = args.quantize.upper()
    
    if not model_path.exists():
        print(f"❌ 模型不存在: {model_path}")
        return False
    
    try:
        from llama_cpp import Llama
        import subprocess
        
        print(f"[1/4] 检查 llama-cpp-python...")
        print(f"   已安装")
        
        print(f"[2/4] 加载模型: {model_path}")
        
        print(f"[3/4] 量化并导出: {quantize}")
        print(f"   输出: {output_path}")
        
        result = subprocess.run(
            ["llama-quantize", str(model_path), str(output_path), quantize],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n[4/4] ✅ GGUF 导出完成！")
            if output_path.exists():
                size_mb = output_path.stat().st_size / 1024 / 1024
                print(f"   文件大小: {size_mb:.0f} MB")
            return True
        else:
            print(f"❌ 导出失败: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ 未找到 llama-quantize 命令")
        print("请安装 llama.cpp: git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp && make")
        return False
    except ImportError:
        print("❌ 缺少 llama-cpp-python")
        print("请运行: pip install llama-cpp-python")
        return False
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_report(args):
    """生成 Adapter 报告"""
    print(f"\n{'='*60}")
    print("Adapter 分析报告")
    print(f"{'='*60}\n")
    
    adapter_path = Path(args.adapter)
    
    if not adapter_path.exists():
        print(f"❌ Adapter 不存在: {adapter_path}")
        return False
    
    try:
        config_path = adapter_path / "adapter_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("Adapter 配置:")
        print(f"  基座模型: {config.get('base_model_name_or_path', 'N/A')}")
        print(f"  LoRA Rank: {config.get('r', 'N/A')}")
        print(f"  LoRA Alpha: {config.get('lora_alpha', 'N/A')}")
        print(f"  Target Modules: {config.get('target_modules', 'N/A')}")
        
        total_size = sum(f.stat().st_size for f in adapter_path.glob("**/*") if f.is_file())
        size_mb = total_size / 1024 / 1024
        
        print(f"\n  总大小: {size_mb:.1f} MB")
        
        print(f"\n  文件列表:")
        for f in adapter_path.iterdir():
            if f.is_file():
                fsize = f.stat().st_size / 1024
                print(f"    - {f.name}: {fsize:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Hex64 Adapter 后处理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    merge_parser = subparsers.add_parser("merge", help="合并 LoRA adapter")
    merge_parser.add_argument("--base-model", required=True, help="基座模型路径")
    merge_parser.add_argument("--adapter", required=True, help="Adapter 路径")
    merge_parser.add_argument("--output", required=True, help="输出路径")
    
    gguf_parser = subparsers.add_parser("gguf", help="导出 GGUF 格式")
    gguf_parser.add_argument("--model", required=True, help="模型路径")
    gguf_parser.add_argument("--output", required=True, help="GGUF 输出路径")
    gguf_parser.add_argument("--quantize", default="Q4_K_M", 
                            choices=["Q4_0", "Q4_K_M", "Q5_K_M", "Q8_0"])
    
    report_parser = subparsers.add_parser("report", help="生成 Adapter 报告")
    report_parser.add_argument("--adapter", required=True, help="Adapter 路径")
    
    args = parser.parse_args()
    
    if args.command == "merge":
        success = merge_adapter(args)
    elif args.command == "gguf":
        success = export_gguf(args)
    elif args.command == "report":
        success = generate_report(args)
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
