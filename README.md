# Hex64 通用符号引擎 v1.0

> ⚠️ **项目声明**：本项目为计算机科学与符号学研究项目，探讨《易经》符号系统与二进制逻辑的工程化映射。项目不涉及任何形式的彩票预测、命理算命或金融投资建议，所有输出均为确定性算法生成的模拟数据，请勿用于非法用途。

**定位：** 基于邵雍先天六十四卦与莱布尼茨二进制映射关系的通用符号编码基础设施  
**场景：** AI 特征编码 · 领域特定语言 (HexLang) · IoT 硬件控制 · 数字资产标识 · 规则引擎  
**协议：** MIT

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
├── data/
│   ├── hex64_full.json     # 全量64卦结构化数据
│   └── README.md           # 数据层说明
├── src/
│   ├── core.js             # Node.js 核心引擎
│   ├── database.js         # 64卦数据库加载器
│   ├── engine.html         # 浏览器演示 + HexLang编译器
│   └── README.md           # 源代码模块说明
└── examples/               # 使用示例（规划中）
```

## 核心架构

```
┌─────────────────────────────────────────────┐
│              扩展接口层 (Plugin API)          │
│   AI适配器 · HexLang编译器 · IoT驱动 · NFT元数据 │
├─────────────────────────────────────────────┤
│              运算内核层 (Rule Engine)         │
│   变爻(XOR) · 错卦(NOT) · 综卦(REV) · 叠加(AND/OR) │
├─────────────────────────────────────────────┤
│              转码总线层 (Transcoding Bus)     │
│   任意输入 → 卦编码 → 特征向量/伪代码/控制信号 │
├─────────────────────────────────────────────┤
│              数据底盘层 (Data Foundation)     │
│   全量64卦结构化数据库（二进制/语义标签/权重）  │
└─────────────────────────────────────────────┘
```

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
| 卦叠加 | AND/OR/XOR | 规则引擎多条件判断 |

## Roadmap

- **v1.1** Python/Node.js SDK 完善
- **v1.2** HexLang 基础编译器
- **v1.3** Arduino/Raspberry Pi 硬件适配
- **v2.0** 自定义符号系统映射

---

*非玄学工具，所有运算逻辑完全 deterministic（确定性）*
