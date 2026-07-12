#!/usr/bin/env python3
"""
Hex64 模型加载校验脚本

运行方式：
    python scripts/verify_model.py

输出：
    ✅ 模型文件完整性检查
    ✅ 推理测试
"""

import sys
import os
from pathlib import Path

# UTF-8 兼容
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def verify_model(model_path="models/qwen3-8b"):
    print(f"\n{'='*60}")
    print("模型加载校验报告")
    print(f"{'='*60}\n")
    
    model_dir = Path(model_path)
    
    # 1. 检查文件完整性
    print("[1] 文件完整性检查")
    required_files = {
        "config.json": "模型配置",
        "tokenizer.json": "分词器",
        "tokenizer_config.json": "分词器配置",
    }
    
    all_exist = True
    for file_name, desc in required_files.items():
        file_path = model_dir / file_name
        if file_path.exists():
            size_mb = file_path.stat().st_size / 1024 / 1024
            print(f"  ✅ {file_name} ({desc}): {size_mb:.1f} MB")
        else:
            print(f"  ❌ {file_name} ({desc}): 缺失")
            all_exist = False
    
    # 检查 safetensors 文件
    safetensors = list(model_dir.glob("model-*.safetensors"))
    if safetensors:
        total_size = sum(f.stat().st_size for f in safetensors)
        print(f"  ✅ model-*.safetensors: {len(safetensors)} 个文件，共 {total_size/1024**3:.1f} GB")
    else:
        print(f"  ❌ model-*.safetensors: 未找到权重文件")
        all_exist = False
    
    if not all_exist:
        print(f"\n❌ 模型文件不完整，无法继续")
        return False
    
    # 2. 加载测试
    print(f"\n[2] 模型加载测试")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        print(f"  加载 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            padding_side='left'
        )
        
        print(f"  加载模型（INT4 量化）...")
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            device_map='auto',
            trust_remote_code=True,
        )
        
        print(f"  ✅ 模型加载成功")
        
        # 3. 推理测试
        print(f"\n[3] 推理测试")
        test_inputs = [
            "CPU 过载了",
            "数据库连接池耗尽",
            "内存泄漏检测",
        ]
        
        for test_input in test_inputs:
            messages = [
                {'role': 'system', 'content': '你是 HexLang Assistant'},
                {'role': 'user', 'content': test_input}
            ]
            
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = tokenizer(text, return_tensors='pt').to(model.device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"  输入: {test_input}")
            print(f"  输出: {response[:100]}...")
            print()
        
        print(f"{'='*60}")
        print(f"✅ 模型校验通过，可以开始训练")
        print(f"{'='*60}\n")
        return True
        
    except ImportError as e:
        print(f"  ❌ 缺少依赖: {e}")
        print(f"  请运行: pip install transformers peft torch bitsandbytes")
        return False
    except Exception as e:
        print(f"  ❌ 模型加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='models/qwen3-8b', help='模型路径')
    args = parser.parse_args()
    
    success = verify_model(args.model)
    sys.exit(0 if success else 1)
