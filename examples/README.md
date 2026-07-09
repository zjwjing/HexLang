# examples/ — HexLang 使用示例

本目录包含 Hex64 引擎的使用示例和代码模板。

---

## 示例列表

| 文件 | 说明 | 运行方式 |
|------|------|---------|
| `basic-usage.js` | 基础 API 用法（转码/特征向量/伪代码/GPIO/运算） | `node basic-usage.js` |
| `engine-api.js` | 高级用法（自定义数据库/链式调用/哈希分布/可视化） | `node engine-api.js` |
| `logo-demo.js` | 八经卦 ASCII 艺术展示（5个版本） | `node logo-demo.js` |

---

## 快速开始

```bash
# 基础示例
node examples/basic-usage.js

# 高级示例
node examples/engine-api.js

# 启动画面示例（5个版本的八经卦 ASCII 艺术）
node examples/logo-demo.js
```

---

## 代码模板

### 基本导入

```js
import { Hex64Engine } from '../src/core.js';

const engine = new Hex64Engine();
const result = engine.tranceive('your_input');

console.log(result.hexCode.name);    // 卦名
console.log(result.featureVec);      // 特征向量
console.log(result.pseudoCode);      // 伪代码
console.log(result.controlSignal);   // GPIO 信号
```

### 自定义数据库

```js
const customDb = [
  { bin: '000000', name: 'MyHex', tags: ['custom'], weight: 0.5 },
  // ... 更多自定义卦
];

const engine = new Hex64Engine(customDb);
```

### 运算链

```js
const step1 = engine.operate('cuo', 'input1');
const step2 = engine.operate('zong', step1.resultBin);
const step3 = engine.operate('bian', 'input1', step2.resultBin);
```

---

## 扩展指南

如果你要添加新的示例，请遵循：

1. **单一职责** — 每个示例只演示一个主题
2. **自包含** — 不依赖外部文件或网络请求
3. **可运行** — 确保 `node 示例文件.js` 能直接运行
4. **有注释** — 代码中包含清晰的说明
