# HexLang Security & Compliance

> **Version: 1.0.0 | Last Updated: 2026-07-09**

---

## 1. License Framework

HexLang uses a **dual-license approach**:

| Component | License | Permissions | Restrictions |
|-----------|---------|-------------|--------------|
| **Code** (src/, bin/, scripts/) | MIT | Use, copy, modify, distribute, sell | Must include copyright notice |
| **Semantic Definitions** (hex_tags_registry.json, tagToOp) | CC BY-NC 4.0 | Attribution required | No commercial use without permission |
| **Base Data** (hexagrams.json) | Varies by source | See [data/_sources.json](data/_sources.json) | Respect original licenses |
| **LoRA Adapters** (adapters/) | MIT | Same as code | Derived works must retain attribution |

### 1.1 MIT License (Code)

```
Copyright (c) 2026 zjwjing / HexLang project

Permission is hereby granted, free of charge...
[Full text in LICENSE file]
```

### 1.2 CC BY-NC 4.0 (Semantic Definitions)

```
Attribution-NonCommercial 4.0 International

You are free to:
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon

Under the following terms:
- Attribution — You must give appropriate credit
- NonCommercial — You may not use the material for commercial purposes
```

**Commercial Use:** Contact the project owner for licensing.

---

## 2. Data Provenance

All third-party data sources are documented in [data/_sources.json](data/_sources.json):

| Source | Content | License | Attribution Required |
|--------|---------|---------|---------------------|
| adamblvck/iching-wilhelm-dataset | Unicode symbols, English names, Wilhelm judgments | CC BY-NC 4.0 | ✅ Yes |
| qntm/hexagram-encode | Base64 ↔ hexagram mapping | Public Domain | ❌ No |
| chengjun/iching | Chinese original text, modern explanations | MIT | ✅ Yes |

### 2.1 Attribution Template

When redistributing derived works that include Hex64 semantic mappings:

```
Hex64 data adapted from:
- adamblvck/iching-wilhelm-dataset (CC BY-NC 4.0)
- chengjun/iching (MIT)
- qntm/hexagram-encode (Public Domain)

Engineering semantic mappings © 2026 HexLang project (CC BY-NC 4.0)
```

---

## 3. Hex64 Definition Rights

### 3.1 What Is Protected?

The following are **original intellectual contributions** of the HexLang project:

1. **Engineering Semantic Mapping** — How each of the 64 hexagrams maps to software engineering concepts (e.g., "承载" → storage, "决断" → branching)
2. **Yao-weighted Feature Calculation** — The 6-dimensional weight vector per hexagram
3. **Inter-hexagram Context Computation** — Deriving contextual features from middle 4 lines
4. **Rule-based Embedding Scheme** — Distance-decay sparse embedding for hexagram similarity
5. **Tag-to-Operation Registry** — The `tagToOp` mapping table (443 entries)

### 3.2 What Is NOT Protected?

The following are **public domain** or **freely usable**:

1. I Ching hexagram names and binary representations (historical knowledge)
2. Shao Yong's先天序 (1629 AD, public domain)
3. DJB2 hash algorithm (public domain)
4. Basic I Ching philosophy and traditional interpretations

### 3.3 Enforcement Policy

| Violation | Response |
|-----------|----------|
| Fork with attribution, non-commercial | Allowed (per CC BY-NC 4.0) |
| Fork removing attribution | DMCA takedown + community report |
| Commercial product using Hex64 definitions | Cease & desist → legal action |
| Competing "I Ching × Engineering" product | Patent/trademark enforcement |

---

## 4. Model Safety

### 4.1 Qwen3-8B Usage

The fine-tuned model is loaded with safety constraints:

```python
SYSTEM_PROMPT = """你是 HexLang Assistant...
## 禁止词库
禁止使用：预测、运势、吉凶、算命、风水、五行、八字、命理、星座、塔罗...
"""
```

### 4.2 Prohibited Words Filter

The system prompt explicitly blocks fortune-telling terminology:

| Category | Blocked Terms |
|----------|--------------|
| Fortune-telling | 预测、运势、吉凶、算命 |
| Fengshui | 风水、五行、八字 |
| Astrology | 命理、星座、塔罗 |
| Mysticism | 老天爷、天机、命中注定 |

If any blocked term is detected, the model returns:
```
Hex64 为工程符号系统，不支持玄学查询。请输入工程/技术/运维相关问题。
```

### 4.3 Output Validation

All model outputs follow a structured format:

```
[Hex64] 本卦: XXX | 互卦: XXX
[爻位] 初爻=X(w=w.xx), ...
[思考] 步骤 1→步骤 5 的结构化推理链
[建议] 具体的工程化建议（仅一条，可执行）
```

This ensures consistency and prevents hallucination.

---

## 5. Training Data Privacy

### 5.1 Feedback Data

User feedback is stored locally in `data/feedback.json`:

```json
{
  "timestamp": "2026-07-09T08:02:01.342232",
  "user_input": "timeout_error",
  "target_hex": "泽雷随",
  "scene": "ops",
  "confidence": 1.0
}
```

**No personal data is collected.** User inputs are anonymized technical descriptions.

### 5.2 Semantic Cache

Cached responses are stored in `data/semantic_cache.json`:

```json
{
  "bin_code|yao_weights": {
    "response": "...",
    "hex_name": "...",
    "timestamp": "..."
  }
}
```

Cache entries are automatically evicted when exceeding `max_size=1000`.

### 5.3 Model Weights

LoRA adapters (`adapters/hex64-v1/`) are trained on local data only. No user data leaves the machine.

---

## 6. Dependency Security

### 6.1 Python Dependencies

| Package | Version | Purpose | Risk Level |
|---------|---------|---------|------------|
| transformers | 4.57.6 | Model loading | Low (HuggingFace) |
| peft | 0.19.1 | LoRA support | Low (HuggingFace) |
| trl | 0.29.1 | SFT trainer | Low (HuggingFace) |
| torch | 2.6.0+cu124 | Deep learning | Low (PyTorch) |
| bitsandbytes | Latest | INT4 quantization | Low |
| datasets | 4.8.5 | Data handling | Low (HuggingFace) |
| accelerate | 1.14.0 | Multi-GPU support | Low (HuggingFace) |

### 6.2 Node.js Dependencies

| Package | Purpose |
|---------|---------|
| None required | All core JS modules are vanilla Node.js |

### 6.3 Supply Chain Protection

- All Python packages installed from PyPI (verified publishers)
- All JS code is vanilla, no external npm dependencies for core
- Model weights downloaded from ModelScope (verified HuggingFace mirror)

---

## 7. Compliance Checklist

| Requirement | Status | Notes |
|------------|--------|-------|
| MIT license in all source files | ✅ | 14 Python files updated |
| Third-party data attribution | ✅ | [data/_sources.json](data/_sources.json) |
| CC BY-NC 4.0 for semantic definitions | ✅ | [hex_tags_registry.json](data/hex_tags_registry.json) |
| No personal data collection | ✅ | Local-only processing |
| Model safety filters | ✅ | Prohibited words in system prompt |
| Structured output validation | ✅ | Fixed format enforced |
| Open source dependency audit | ✅ | All packages from trusted sources |

---

## 8. Reporting Vulnerabilities

If you discover a security issue:

1. **Do not** open a public GitHub issue
2. Email: [security@hexlang.dev](mailto:security@hexlang.dev) *(placeholder)*
3. Include steps to reproduce and potential impact
4. Expect response within 7 business days

---

*This document is maintained by the HexLang project.*  
*For questions about compliance, contact the project owner.*
