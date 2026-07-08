# Hex64 通用符号引擎 v1.0

**定位：** 基于邵雍先天六十四卦与莱布尼茨二进制映射关系的通用符号编码基础设施  
**场景：** AI 特征编码 · 领域特定语言 (HexLang) · IoT 硬件控制 · 数字资产标识 · 规则引擎  
**协议：** MIT

---

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

打开 `src/engine.html` 即可在浏览器中体验完整转码流程。

### Node.js

```bash
node src/core.js
```

输出示例：

```
输入: "Hello OpenCode"
  卦索引: 22
  二进制: 010110
  卦名: 泽水困
  权重: 0.2
  特征向量: [0, 1, 0, 1, 1, 0]
  伪代码: HEX(泽水困) { 困境; 困顿; 穷困; }
  GPIO: OFF | ON | OFF | ON | ON | OFF
```

### 程序调用

```js
import { Hex64Engine } from './src/core.js';

const engine = new Hex64Engine();
const result = engine.tranceive("AI_training_data");

console.log(result.hexCode);     // { index, bin, name, weight }
console.log(result.featureVec);  // [0, 1, 0, 1, 1, 0]
console.log(result.pseudoCode);  // HEX(泽火革) { UPDATE; }
console.log(result.controlSignal); // ["OFF","ON","OFF","ON","ON","OFF"]
```

## 数据结构

每卦包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `bin` | string | 6位二进制编码（阴=0，阳=1） |
| `name` | string | 卦名（如"乾为天"） |
| `tags` | string[] | 语义标签（可扩展） |
| `weight` | number | 数值权重 0.0-1.0 |

## 运算规则

| 易经概念 | 计算机指令 | 技术含义 |
|----------|-----------|----------|
| 变爻 | XOR | 权重翻转、规则条件变更 |
| 错卦 | NOT | 逻辑非、状态反转 |
| 综卦 | BIT_REVERSE | 数据归一化、视角切换 |
| 卦叠加 | AND/OR | 规则引擎多条件判断 |

## Roadmap

- **v1.1** Python/Node.js SDK 完善
- **v1.2** HexLang 基础编译器
- **v1.3** Arduino/Raspberry Pi 硬件适配
- **v2.0** 自定义符号系统映射

---

*非玄学工具，所有运算逻辑完全 deterministic（确定性）*
