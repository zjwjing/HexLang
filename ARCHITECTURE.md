# HexLang Architecture

> **HexLang — Symbolic Encoding System for Software Engineering**  
> Version: 1.2.0 | Last Updated: 2026-07-09

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ VSCode   │  │ CLI      │  │ Dashboard│  │ Browser    │  │
│  │ Extension│  │ hex64.js │  │ (HTML)   │  │ Engine     │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
└───────┼─────────────┼─────────────┼──────────────┼──────────┘
        │             │             │              │
        ▼             ▼             ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Engine Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           src/core.js (Hex64Engine Class)            │   │
│  │  encode() | encodeFangtu() | encodeYaochen()         │   │
│  │  encodeYubu() | encodeTaiXuan() | encodeYuanHui()    │   │
│  │  Operations: cuo | zong | bian | AND | OR | XOR | hu│   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           src/compiler.js (Shared Compiler)          │   │
│  │  compileHex() → JS / Python / Rust / Go              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           src/templates.js (Template Generator)      │   │
│  │  384 templates (single source of truth)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
        │                          │
        ▼                          ▼
┌──────────────────┐    ┌──────────────────────────────────┐
│  Data Layer      │    │    AI/ML Integration Layer       │
│                  │    │                                  │
│ data/hexagrams.json │ src/core/encoder.py (Python Encoder)│
│ data/hex64_full.json│ - Yao-weighted features (6-dim)    │
│ data/rules.json   │ - Inter-hexagram context (12-dim)   │
│ data/train_hex64.jsonl│ - 64-dim rule-based embedding    │
│ data/feedback.json │ - Semantic cache                    │
│ data/_sources.json │                                  │
│ data/hex_tags_registry.json │ ┌──────────────────────┐  │
└──────────────────┘    │  │  src/models/qwen_loader.py │  │
                        │  │  - Qwen3-8B + LoRA adapter │  │
                        │  │  - CoT System Prompt       │  │
                        │  │  - SemanticCache class     │  │
                        │  └──────────────────────────┘  │
                        │  ┌──────────────────────────┐  │
                        │  │ src/training/             │  │
                        │  │ - train_lora.py           │  │
                        │  │ - feedback_manager.py     │  │
                        │  │ - prepare_data.py         │  │
                        │  └──────────────────────────┘  │
                        └──────────────────────────────────┘
```

---

## 2. Module Architecture

### 2.1 Core Engine (`src/`)

| File | Purpose | Key Exports |
|------|---------|-------------|
| `core.js` | Main engine with 7 operations | `Hex64Engine` class |
| `compiler.js` | Shared compilation logic | `compileHex()` |
| `templates.js` | Template generation | 384 templates |
| `database.js` | Data layer | `HEXAGRAMS`, `TAG_TO_OP` |
| `taixuan.js` | TaiXuan trinary encoding | `TaiXuanEncoder` |
| `yuanhui.js` | YuanHui nested counter | `YuanHuiEncoder` |
| `engine.html` | Browser demo | Standalone HTML |

### 2.2 Python Encoder (`src/core/`)

| File | Purpose | Status |
|------|---------|--------|
| `encoder.py` | Yao-weighted + inter-hex + 64d embedding | 🟢 Upgraded |
| `rule_mapper.py` | Business rules → hexagram mapping | 🟢 New |
| `calibrate.py` | Weight calibration utilities | 🟢 Normal |
| `feedback.py` | Feedback processing | 🟢 Normal |
| `__init__.py` | Package exports | 🟢 Normal |

### 2.3 AI Integration (`src/models/`)

| File | Purpose | Model |
|------|---------|-------|
| `qwen_loader.py` | Qwen3-8B loader with LoRA | INT4 quantized |
| `ollama_loader.py` | Ollama integration | Any GGUF model |
| `__init__.py` | Package exports | - |

### 2.4 Training Pipeline (`src/training/`)

| File | Purpose |
|------|---------|
| `train_lora.py` | QLoRA fine-tuning script |
| `prepare_data.py` | Training data generator |
| `feedback_manager.py` | Feedback loop manager |
| `__init__.py` | Package exports |

### 2.5 CLI & Tools (`bin/`, `scripts/`)

| File | Purpose |
|------|---------|
| `bin/hex64.js` | CLI tool (logo, 4-lang output) |
| `bin/audit.mjs` | Code audit utility |
| `bin/normalize.mjs` | Data normalization |
| `scripts/rebuild-templates.mjs` | Template rebuild script |

---

## 3. Data Flow

### 3.1 Encoding Pipeline

```
User Input ("CPU overload")
         │
         ▼
┌─────────────────────┐
│  Hex64Encoder       │
│  - DJB2 hash → bin  │
│  - bin → hex_name   │
│  - yao_weights[6]   │
│  - inter_hex()      │
│  - embedding_64d()  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Feature Vector     │
│  [6-dim weighted]   │
│  [12-dim combined]  │
│  [64-dim sparse]    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  QwenLoader         │
│  - System Prompt    │
│  - CoT reasoning    │
│  - Semantic cache   │
└─────────┬───────────┘
          │
          ▼
Structured Output:
[Hex64] 本卦：...
[爻位] 初爻=...
[思考] 步骤 1→...
[建议] 具体工程建议
```

### 3.2 Training Pipeline

```
feedback.json (user corrections)
        │
        ▼
┌─────────────────────┐
│  prepare_data.py    │
│  - From feedback    │
│  - From rules.json  │
│  - Augmented (64×3) │
└─────────┬───────────┘
          │
          ▼
train_hex64.jsonl (2002 samples)
          │
          ▼
┌─────────────────────┐
│  train_lora.py      │
│  - Qwen3-8B BF16    │
│  - bnb INT4 quant   │
│  - LoRA r=16        │
│  - 300 steps        │
└─────────┬───────────┘
          │
          ▼
adapters/hex64-v1/ (83 MB)
          │
          ▼
┌─────────────────────┐
│  feedback_manager   │
│  - Version control  │
│  - Rollback support │
│  - Auto-retrain     │
└─────────────────────┘
```

---

## 4. Key Design Decisions

### 4.1 Why Qwen3-8B over Qwen3.5-9B?

| Factor | Qwen3.5-9B | Qwen3-8B |
|--------|-----------|----------|
| Format on MS | VL (multimodal) | Pure text |
| LoRA suitability | ❌ Needs vision tower | ✅ Ready |
| ModelScope availability | No Instruct version | Available |
| VRAM (INT4) | ~6GB | ~5GB |
| Decision | Skip for now | **Selected** |

### 4.2 Why INT4 Quantization?

```
FP16 8B model:  ~16 GB VRAM (too large for 4080S with batch training)
INT4 8B model:  ~5 GB VRAM (fits comfortably, leaves room for batch)
```

### 4.3 Why 300 Training Steps?

| Dataset Size | Recommended Steps | Rationale |
|-------------|------------------|-----------|
| 2002 samples | 300 steps | ~1 epoch, sufficient convergence |
| Loss curve | 2.68 → 0.05 | Stable convergence, no overfitting |
| Token accuracy | 57% → 99% | Strong learning signal |

### 4.4 Single Source of Truth

```
src/templates.js ← rebuild-templates.mjs → rs/go/py/js
```

Templates are generated from a single JavaScript file, ensuring consistency across all 4 target languages.

---

## 5. File Dependencies

```
core.js
├── database.js (HEXAGRAMS, TAG_TO_OP)
├── templates.js (opTemplates)
└── compiler.js (compileHex)

encoder.py
├── data/hex64_full.json (yao_weights, tags)
├── core/rule_mapper.py (business rules)
└── models/qwen_loader.py (AI inference)

qwen_loader.py
├── adapters/hex64-v1/ (LoRA weights)
├── data/semantic_cache.json (cache)
└── data/hexagrams.json (fallback lookup)

train_lora.py
├── models/qwen3-8b/ (base model)
├── data/train_hex64.jsonl (training data)
└── src/training/prepare_data.py (data prep)
```

---

## 6. Deployment Targets

| Target | Technology | Status |
|--------|-----------|--------|
| Node.js CLI | `bin/hex64.js` | 🟢 Production |
| Python API | `src/core/encoder.py` | 🟢 Production |
| VSCode Extension | `vscode-ext/` | 📋 MVP planned |
| Browser Demo | `src/engine.html` | 🟢 Working |
| Enterprise Dashboard | `src/dashboard/` | 📋 Phase 2 |

---

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2026-07-09 | Yao weights, inter-hex, 64d embedding, LoRA |
| 1.1.0 | 2026-07-09 | 4-language compiler, 384 templates |
| 1.0.0 | 2026-07-08 | Initial release, 64 hexagrams |

---

*This document is maintained by the HexLang project.*  
*For contributions, see [CONTRIBUTING.md](CONTRIBUTING.md).*
