import sys
import os
import json
import shutil
from pathlib import Path

class EnvChecker:
    """环境校验器"""
    
    def __init__(self):
        self.results = []
        self.pass_count = 0
        self.fail_count = 0
    
    def check(self, name, condition, details=""):
        status = "OK" if condition else "FAIL"
        self.results.append((name, condition, details))
        if condition:
            self.pass_count += 1
        else:
            self.fail_count += 1
        print(f"  [{status}] {name}" + (f" - {details}" if details else ""))
    
    def run_all_checks(self):
        print("\n" + "="*60)
        print("Hex64 环境校验报告")
        print("="*60 + "\n")
        
        # 1. Python 版本
        print("[1] Python 环境")
        self.check("Python >= 3.10", sys.version_info >= (3, 10), f"{sys.version.split()[0]}")
        
        # 2. PyTorch
        print("\n[2] PyTorch")
        try:
            import torch
            self.check("PyTorch 已安装", True, f"v{torch.__version__}")
            cuda_available = torch.cuda.is_available()
            self.check("CUDA 可用", cuda_available, 
                      f"{torch.cuda.get_device_name(0)}" if cuda_available else "不可用")
            if cuda_available:
                mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
                self.check("显存 >= 14GB", mem >= 14, f"{mem:.1f}GB")
        except ImportError:
            self.check("PyTorch 已安装", False)
        
        # 3. 关键依赖
        print("\n[3] 关键依赖包")
        deps = ["transformers", "peft", "trl", "datasets"]
        for dep in deps:
            try:
                mod = __import__(dep.replace("-", "_"))
                version = getattr(mod, "__version__", "unknown")
                self.check(f"{dep} 已安装", True, f"v{version}")
            except ImportError:
                self.check(f"{dep} 已安装", False)
        
        # 4. 模型文件
        print("\n[4] 模型文件完整性")
        model_paths = ["models/qwen3.5-9b", "models/Qwen3-8B-Instruct-FP8"]
        model_found = False
        for mp in model_paths:
            config_path = Path(mp) / "config.json"
            if config_path.exists():
                self.check(f"模型目录存在: {mp}", True)
                self.check("config.json 存在", config_path.exists())
                
                tokenizer_path = Path(mp) / "tokenizer.json"
                self.check("tokenizer.json 存在", tokenizer_path.exists())
                
                safetensors = list(Path(mp).glob("*.safetensors"))
                self.check("model *.safetensors 存在", len(safetensors) > 0, f"{len(safetensors)} 个文件")
                model_found = True
                break
        
        if not model_found:
            self.check("模型目录存在", False, "未找到有效模型路径")
        
        # 5. 训练数据
        print("\n[5] 训练数据完整性")
        train_file = Path("data/train_hex64.jsonl")
        if train_file.exists():
            self.check("train_hex64.jsonl 存在", True)
            line_count = sum(1 for _ in open(train_file, 'r', encoding='utf-8'))
            self.check("数据量 >= 5000", line_count >= 5000, f"{line_count} 条")
            
            valid_lines = 0
            with open(train_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if 'messages' in data and len(data['messages']) >= 3:
                            valid_lines += 1
                    except:
                        pass
            self.check("JSONL 格式正确", valid_lines == line_count, f"{valid_lines}/{line_count}")
        else:
            self.check("train_hex64.jsonl 存在", False)
        
        # 6. Adapter 目录
        print("\n[6] Adapter 状态")
        adapter_dir = Path("adapters")
        if adapter_dir.exists():
            adapters = [d for d in adapter_dir.iterdir() if d.is_dir() and d.name.startswith('hex64-')]
            self.check("Adapter 目录存在", True, f"{len(adapters)} 个版本")
            for adapter in adapters:
                config = adapter / "adapter_config.json"
                self.check(f"{adapter.name}/adapter_config.json", config.exists())
        else:
            self.check("Adapter 目录存在", False)
        
        # 7. 磁盘空间
        print("\n[7] 系统资源")
        try:
            usage = shutil.disk_usage(".")
            free_gb = usage.free / 1024**3
            self.check("磁盘空闲 >= 50GB", free_gb >= 50, f"{free_gb:.1f}GB 可用")
        except:
            self.check("磁盘空间检查", False, "无法获取")
        
        # 汇总
        print("\n" + "="*60)
        total = self.pass_count + self.fail_count
        pct = self.pass_count/total*100 if total > 0 else 0
        print(f"汇总: {self.pass_count}/{total} 通过 ({pct:.0f}%)" )
        if self.fail_count > 0:
            print(f"WARNING: {self.fail_count} 项失败，请修复后重试")
        else:
            print("ALL CHECKS PASSED, ready to train")
        print("="*60 + "\n")
        
        return self.fail_count == 0


if __name__ == '__main__':
    checker = EnvChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
