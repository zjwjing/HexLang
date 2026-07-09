# Hex64 通用符号引擎 v1.2

> ⚠️ **项目声明**：本项目为计算机科学与符号学研究项目，探讨《易经》符号系统与二进制逻辑的工程化映射。项目不涉及任何形式的彩票预测、命理算命或金融投资建议，所有输出均为确定性算法生成的模拟数据，请勿用于非法用途。

**定位：** 基于邵雍先天六十四卦与莱布尼茨二进制映射关系的通用符号编码基础设施  
**场景：** AI 特征编码 · 领域特定语言 (HexLang) · IoT 硬件控制 · 数字资产标识 · 规则引擎  
**协议：** MIT  
**AI 集成：** Qwen3.5-9B + 反馈自修正 + LoRA 微调

---

## 八经卦 · 二进制映射表

```
┌─────────────────────────────────────┐
│  乾☰   兑☱   离☲   震☳   巽☴   坎☵   艮☶   坤☷  │
│  ███   ██░   █░█   █░░   ░█░   ░░█   ░░█   ░░░  │
│  ███   ██░   ░█░   ███   ░░█   ███   ░░█   ░░░  │
│  ███   ░░█   █░█   ███   ░█░   ░░█   ███   ░░░  │
│  111   110   101   100   011   010   001   000  │
│  7     6     5     4     3     2     1     0    │
└─────────────────────────────────────┘
        Hex64 · 八经卦二进制映射表
「3位二进制=1卦=1个八进制位 · 8卦=24位=3字节」
```

> **设计逻辑：** 爻字符 █=阳爻=1，░=阴爻=0，顺序严格遵循邵雍先天卦序（乾→兑→离→震→巽→坎→艮→坤），与莱布尼茨1701年发现的二进制映射完全一致。8卦对应八进制0-7，和 Hex64 的64卦（6位二进制）形成「基础单元→整体系统」的层级呼应。

---

## 项目结构

```
HexLang/
├── README.md               # 本文件
├── CONTRIBUTING.md         # 协作规范
├── CODEOWNERS              # 模块负责人
├── TASKS.md                # 任务看板
├── LICENSE                 # MIT 开源协议
├── package.json            # Node.js 包定义
├── requirements.txt        # Python 依赖
├── models/                 # AI 模型目录
│   └── README.md           # 模型版本说明
├── data/
│   ├── hex64_full.json     # 全量64卦结构化数据
│   ├── hexagrams.json      # 备用数据（已同步）
│   ├── feedback.json       # 用户反馈记录
│   ├── rules.json          # 归纳规则
│   └── train_hex64.json    # 训练数据
├── src/
│   ├── core.js             # Node.js 核心引擎
│   ├── database.js         # 64卦数据库加载器
│   ├── engine.html         # 浏览器演示 + HexLang编译器
│   ├── ai-integration.js   # AI 集成模块（JS）
│   ├── ai-integration.test.js # AI 集成测试
│   ├── cli.py              # Python CLI 入口
│   ├── core/               # Python 核心模块
│   │   ├── __init__.py
│   │   ├── encoder.py      # Hex64 编码器
│   │   ├── feedback.py     # 反馈管理
│   │   └── calibrate.py    # 校准脚本
│   └── models/             # AI 模型模块
│       ├── __init__.py
│       └── qwen_loader.py  # Qwen 模型加载器
├── rules/                  # 规则归纳模块
│   ├── __init__.py
│   └── induce_rules.py     # 规则归纳引擎
├── examples/               # 使用示例
│   ├── basic-usage.js      # JS 基础用法
│   ├── engine-api.js       # JS 高级 API
│   ├── logo-demo.js        # ASCII 艺术展示
│   ├── api-server.js       # HTTP API 服务
│   ├── api-client-demo.js  # API 客户端示例
│   ├── openai-hex64-client.js # OpenAI 兼容客户端
│   └── qwen-hex64-integration.py # Qwen 集成示例
└── train_lora.py           # LoRA 微调脚本
```

## 核心架构

```
┌─────────────────────────────────────────────┐
│         AI 扩展接口层 (AI Plugin API)         │
│   Qwen3.5-9B · Function Calling · LoRA 微调  │
├─────────────────────────────────────────────┤
│         运算内核层 (Rule Engine)              │
│   变爻(XOR) · 错卦(NOT) · 综卦(REV) · 叠加   │
├─────────────────────────────────────────────┤
│         转码总线层 (Transcoding Bus)          │
│   任意输入 → 卦编码 → 特征向量/伪代码/控制信号│
├─────────────────────────────────────────────┤
│         数据底盘层 (Data Foundation)          │
│   全量64卦结构化数据库（二进制/语义标签/权重）│
└─────────────────────────────────────────────┘
```

---

## 快速开始

### 浏览器

```bash
# 直接双击打开
src/engine.html
```

### Node.js

```bash
node src/core.js
```

输出示例：

```
输入: "Hello OpenCode"
  卦索引: 38
  二进制: 100110
  卦名: 泽雷随（Following）
  拼音: zé léi suí
  分类: 跟随/适应
  标签: 跟随, 顺从, 适应, 订阅, 监听, 代理
  权重: 0.5
  特征向量: [1, 0, 0, 1, 1, 0]
  伪代码: HEX(泽雷随) { FOLLOW; COMPLY; ADAPT; SUBSCRIBE; LISTEN; PROXY; }
  GPIO: ON | OFF | OFF | ON | ON | OFF
```

### Python - 快速转码

```python
from examples.qwen-hex64-integration import quick_encode

result = quick_encode("timeout_error")
print(f"卦象: {result['hex_name']}")
print(f"二进制: {result['binary']}")
print(f"标签: {', '.join(result['tags'])}")
```

### Python - 交互式对话（需要下载模型）

```bash
# 1. 安装依赖
pip install transformers accelerate torch

# 2. 下载模型（约 6GB）
modelscope download --model qwen/Qwen3.5-9B-Instruct-GPTQ-Int4 \
    --local_dir ./models/qwen3.5-9b-gptq-int4

# 3. 运行 CLI
python src/cli.py
```

### 程序调用

```js
import { Hex64Engine } from './src/core.js';

const engine = new Hex64Engine();
const result = engine.tranceive("AI_training_data");

console.log(result.hexCode);      // { index, bin, name, pinyin, en, category, tags, weight }
console.log(result.featureVec);   // [0, 1, 0, 1, 1, 0]
console.log(result.pseudoCode);   // HEX(天水需) { WAIT; REQUIRE; EXPECT; DELAY; ASYNC; POLL; }
console.log(result.controlSignal);// ["OFF","ON","OFF","ON","ON","OFF"]
```

---

## AI 集成方案：Qwen3.5-9B + Hex64

### 为什么选择 Qwen3.5-9B？

| Qwen 特性 | Hex64 需求匹配点 |
|----------|-----------------|
| 中文工程语义理解 SOTA | 卦标签（订阅/监听/重构/告警）都是中文工程术语 |
| 原生支持 System Prompt 约束 | 严格限制模型不瞎编卦义，符合确定性要求 |
| 支持工具调用（Function Calling） | 将 Hex64 转码封装为工具，让 Qwen 自动调用 |
| 低资源友好 | 9B 版本 INT4 量化后仅需 6GB 显存，RTX3060 可跑 |
| 开源可商用 | 符合 HexLang 的 MIT 开源协议要求 |

### 三阶段进化路线

#### 📅 Day 1：启动（能对话）

```bash
# 1. 整理模型目录
mkdir -p models
# 下载 Qwen3.5-9B-GPTQ-Int4（~6GB）

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 CLI
python src/cli.py
```

验收标准：
- ✅ Qwen 模型加载成功
- ✅ 输入"CPU 过载"能输出卦象和溯源
- ✅ 输出格式：`[回复]` + `[Hex64 溯源]`

#### 📅 Week 1：进化（能学习）

```bash
# 1. 提交反馈
python src/cli.py
# 在对话中输入：feedback 天水讼→泽雷随 场景：ops

# 2. 运行规则归纳
python rules/induce_rules.py

# 3. 校准权重
python src/core/calibrate.py --apply
```

功能：
- ✅ 反馈自修正（累积 3 次同输入修正 → 更新权重）
- ✅ 规则归纳（关键词→卦象高频关联）
- ✅ 手动校准（更新 hexagrams.json）

#### 📅 Month 1：微调（能进化）

```bash
# 1. 安装 unsloth（需要 8GB+ 显存）
pip install unsloth trl datasets

# 2. 生成训练数据（从 feedback.json + rules.json）
python src/training/prepare_data.py

# 3. 运行 LoRA 微调
python src/training/train_lora.py \
    --output adapters/hex64-v1 \
    --steps 100 \
    --rank 16 \
    --lr 2e-4

# 4. 加载进化后的模型推理
python src/cli.py --adapter adapters/hex64-v1
```

效果：
- ✅ 模型学会 Hex64 专属输出格式
- ✅ 减少 System Prompt 依赖
- ✅ 适配器仅 ~50MB，方便分发
- ✅ 持续进化：积累反馈 → 重新训练 → 新版本适配器

### 模型版本选择

| 版本 | 显存占用 | 适合硬件 | 推荐场景 |
|------|---------|---------|---------|
| FP16 | ~18GB | RTX 3090/4090 (24GB) | 全参数微调 |
| GPTQ-Int4 | ~6GB | RTX 3060 (12GB) | 推理 + LoRA ✅推荐 |
| AWQ-Int4 | ~6GB | RTX 3060 (12GB) | 更快推理 |
| GGUF (Q8_0) | ~10GB | 现代 CPU/GPU | llama.cpp/Ollama |

---

## 数据结构

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `bin` | string | 6位二进制编码（阴=0，阳=1） | `"100110"` |
| `name` | string | 中文卦名 | `"泽雷随"` |
| `pinyin` | string | 拼音 | `"zé léi suí"` |
| `en` | string | 英文翻译 | `"Following"` |
| `category` | string | 功能分类 | `"跟随/适应"` |
| `tags` | string[] | 语义标签（可扩展） | `["跟随", "顺从", "适应", "订阅", "监听", "代理"]` |
| `weight` | number | 数值权重 0.0-1.0 | `0.5` |

## 运算规则

| 易经概念 | 计算机指令 | 技术含义 |
|----------|-----------|----------|
| 变爻 | XOR | 权重翻转、规则条件变更 |
| 错卦 | NOT | 逻辑非、状态反转 |
| 综卦 | BIT_REVERSE | 数据归一化、视角切换 |
| 互卦 | 互 · 中爻滑窗 | 取二三四五爻，二三四为下卦、三四五为上卦 |
| 卦叠加 | AND/OR/XOR | 规则引擎多条件判断 |

## Roadmap

## Related Work

Hex64 occupies a unique position in the open-source I-Ching ecosystem. Existing projects fall into distinct layers:

**Deterministic binary encoders** — [aarzilli/iching](https://github.com/aarzilli/iching) (Go) maps 64-bit integers to/from hexagrams; [seeded-iching-engine](https://github.com/augchan42/seeded-iching-engine) (TypeScript) provides verifiable seed→hexagram computation. These share Hex64's "hexagram = 6-bit binary" foundation but stop at verifiable encoding, without engineering semantic tags or ML feature vectors.

**Divination tools** — [ichingshifa](https://github.com/kentang2017/ichingshifa) (Python, full 大衍筮法+纳甲+京房), CyberZY (numpy+GPT), and numerous CLI/HTML fortune-telling packages focus on automating traditional divination workflows. These operate in the opposite direction from Hex64: they encode human tradition into code, whereas Hex64 encodes engineering intent into hexagram semantics.

**Conceptual Bagua+AI proposals** — [bagau-llm](https://gitee.com/wrer454_admin/bagau-llm) (Gitee) proposes a hexagram-vocabulary Transformer with semantic mapping, reaching PoC stage without LoRA evolution or feedback loops. "伏羲AI"-style projects (CSDN/intelliparadigm) propose "变爻注意力" mechanisms but remain conceptual without runnable code.

**Hex64's differentiator**: the first project to combine (1) deterministic 6-bit hexagram encoding, (2) engineering-oriented semantic tagging (e.g. 泽雷随 → subscribe/listen/proxy), (3) Hex64 feature-vector augmentation for ML pipelines, and (4) LoRA-based self-evolution via feedback — all under a strict no-divination, MIT-licensed protocol.

## Computational Genealogy（计算谱系）

Hex64 的设计并非孤立创新，而是延续了前现代离散数学的探索脉络：

| 年代 | 计算原型 | 工程化实现 | 模块 |
|------|---------|-----------|------|
| 1070年 | 邵雍先天图：6-bit LUT + 8×8 Cartesian 积 | `encodeFangtu()` | `src/core.js` |
| 西汉 | 京房纳甲：mod384 循环计数器 | `encodeYaochen()` | `src/core.js` |
| 东汉前 | 道门禹步：3×3 网格 Hamiltonian 游走 PRNG | `encodeYubu()` | `src/core.js` |
| 西汉 | 扬雄太玄：3^4=81 首 + 3^6=729 赞三进制 | `TaiXuanEncoder` | `src/taixuan.js` |
| 1070年 | 邵雍皇极经世：元会运世四层嵌套模运算 | `YuanHuiEncoder` | `src/yuanhui.js` |

所有模式均为**确定性编码/计数原型**，无任何玄学效力宣称，符合 MIT 协议的非玄学要求。

## Roadmap
- **v1.2** ✅ HexLang 基础编译器 · CLI 工具完善 · 八经卦 ASCII 艺术
- **v1.3** ✅ Python SDK · Qwen3.5-9B 集成 · HTTP API 服务
- **v1.4** 🔄 Arduino/Raspberry Pi 硬件适配
- **v2.0** 📋 自定义符号系统映射 · 更多 LLM 集成

---

*非玄学工具，所有运算逻辑完全 deterministic（确定性）*
