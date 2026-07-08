# src/ — 源代码模块

HexLang 核心引擎和浏览器前端。

---

## 模块文件

| 文件 | 职责 | 负责人 | 导出 |
|------|------|--------|------|
| `core.js` | Hex64Engine 类，核心转码/运算逻辑 | @zjwjing | `Hex64Engine` |
| `database.js` | 数据加载器，从 JSON 读取卦数据和映射表 | @zjwjing | `HEXAGRAMS`, `TAG_TO_OP` |
| `engine.html` | 浏览器演示 + HexLang 编译器 | @zjwjing | N/A（独立页面） |

---

## core.js — 核心引擎

### 公共 API

```js
import { Hex64Engine } from './core.js';

const engine = new Hex64Engine();
```

### 方法列表

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `lookup(input)` | string | `{...hexagram, index, hash}` | 输入映射到卦 |
| `featureVector(input)` | string | `number[]` | 6位二进制特征向量 |
| `pseudoCode(input)` | string | string | HexLang 伪代码 |
| `controlSignal(input)` | string | `string[]` | GPIO 控制信号 |
| `tranceive(input)` | string | `result` | 完整转码（含所有输出） |
| `operate(op, input, second?)` | string, string, string? | `{op, input, result, resultBin}` | 易经运算 |

### operate() 支持的运算

| op 值 | 易经概念 | 位运算 | 说明 |
|-------|---------|--------|------|
| `'cuo'` | 错卦 | NOT | 6位全部取反 |
| `'zong'` | 综卦 | REV | 爻序反转 |
| `'bian'` | 变爻 | XOR | 与第二输入异或，或全部取反 |
| `'AND'` | 叠加与 | AND | 需要 secondInput |
| `'OR'` | 叠加或 | OR | 需要 secondInput |
| `'XOR'` | 叠加异或 | XOR | 需要 secondInput |

### 数据流

```
输入字符串
  ↓ hash() (DJB2)
卦索引 (0-63)
  ↓ 查表 HEXAGRAMS[index]
卦数据 {bin, name, pinyin, en, category, tags, weight}
  ↓ 并行输出
featureVec  pseudoCode  controlSignal
```

---

## database.js — 数据加载器

唯一数据源：`../data/hex64_full.json`

```js
import { HEXAGRAMS, TAG_TO_OP } from './database.js';
```

- `HEXAGRAMS` — 64卦完整数据数组
- `TAG_TO_OP` — 语义标签到操作码的映射表（166条）

---

## engine.html — 浏览器前端

独立运行的单页应用，无需服务器。

### 功能

- 转码引擎交互界面
- HexLang 编译器（JS/Python 代码生成）
- 易经运算演示
- 转码历史记录

### 数据加载

通过 `fetch('../data/hex64_full.json')` 动态加载数据，不内联副本。

---

## 模块依赖关系

```
engine.html ──fetch──→ data/hex64_full.json
core.js ──import──→ database.js ──import──→ data/hex64_full.json
```

**规则：** 所有数据必须来自 `data/hex64_full.json`，禁止在其他地方硬编码卦数据。
