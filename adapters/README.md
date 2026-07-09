# HexLang LoRA 适配器

训练好的 LoRA 适配器存放目录。

## 目录结构

```
adapters/
├── hex64-v1/          # Hex64 符号编码适配器 v1
│   ├── adapter_model.json
│   ├── adapter.bin
│   ├── adapter_config.json
│   └── README.md      # 版本说明
└── README.md          # 本文件
```

## 适配器说明

### hex64-v1

**训练数据**:
- feedback.json: 用户修正记录（高质量）
- rules.json: 自动归纳规则（中等质量）
- hexagrams.json 增强数据（低质量，用于泛化）

**训练参数**:
- 基座模型: Qwen3.5-9B (GPTQ-Int4)
- LoRA rank: 16
- 学习率: 2e-4
- 训练步数: 100 (可调整至 300-500)
- batch size: 2 (显存不足时降至 1)
- 量化: 4-bit QLoRA

**使用方法**:

```bash
# 加载进化后的模型
python src/cli.py --adapter adapters/hex64-v1

# 单次对话
python src/cli.py --input "系统CPU过载了" --adapter adapters/hex64-v1
```

## 持续进化

1. **收集反馈**: 通过 CLI 的 `feedback` 命令积累修正记录
2. **重新生成数据**: `python src/training/prepare_data.py`
3. **重新训练**: `python src/training/train_lora.py`
4. **保存新适配器**: 输出目录会自动递增版本号 (hex64-v2, hex64-v3...)

## 注意事项

- 适配器文件仅几十 MB，远小于基座模型的 ~6GB
- 不同基座模型版本不兼容，确保使用相同的基座加载适配器
- 训练步数越多，记忆越强，但可能过拟合
