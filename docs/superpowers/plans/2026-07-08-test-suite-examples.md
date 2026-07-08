# 测试套件 + 示例修复 实施计划

> **对于代理工人：** 一步步实施此计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** 为 Hex64 核心引擎添加全面的 Node.js 测试套件，修复 examples/ 中的 bug，完善 package.json。

**技术栈：** Node.js 内置 `node:test` + `node:assert`

---

### 任务 1：核心引擎单元测试

**文件：**
- 创建：`src/core.test.js`

**接口：**
- 消耗：`Hex64Engine` 类（`src/core.js`），`HEXAGRAMS`（`src/database.js`）
- 产生：完整的测试覆盖 lookup/tranceive/featureVector/pseudoCode/controlSignal/operate

- [ ] **步骤1：创建测试文件**

`src/core.test.js`：

```js
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { Hex64Engine } from './core.js';

describe('Hex64Engine', () => {
  const engine = new Hex64Engine();

  describe('lookup()', () => {
    it('returns deterministic results for same input', () => {
      const a = engine.lookup('hello');
      const b = engine.lookup('hello');
      assert.equal(a.index, b.index);
      assert.equal(a.bin, b.bin);
    });

    it('returns different hexagrams for different inputs', () => {
      const a = engine.lookup('hello');
      const b = engine.lookup('world');
      assert.notEqual(a.index, b.index);
    });

    it('returns a valid hexagram object', () => {
      const r = engine.lookup('test');
      assert.ok(r.index >= 0 && r.index < 64);
      assert.equal(r.bin.length, 6);
      assert.ok(/^[01]{6}$/.test(r.bin));
      assert.ok(typeof r.name === 'string');
      assert.ok(r.name.length > 0);
      assert.ok(Array.isArray(r.tags));
      assert.equal(r.tags.length, 6);
    });

    it('handles empty string', () => {
      const r = engine.lookup('');
      assert.ok(r.index >= 0 && r.index < 64);
    });

    it('handles non-string input', () => {
      const r = engine.lookup(123);
      assert.ok(r.index >= 0 && r.index < 64);
    });
  });

  describe('tranceive()', () => {
    it('returns all expected fields', () => {
      const r = engine.tranceive('hello');
      assert.ok(r.input);
      assert.ok(r.hexCode);
      assert.ok(r.featureVec);
      assert.ok(r.pseudoCode);
      assert.ok(r.controlSignal);
    });

    it('featureVec is an array of 6 bits', () => {
      const r = engine.tranceive('hello');
      assert.equal(r.featureVec.length, 6);
      r.featureVec.forEach(b => assert.ok(b === 0 || b === 1));
    });

    it('controlSignal matches featureVec', () => {
      const r = engine.tranceive('hello');
      r.featureVec.forEach((b, i) => {
        assert.equal(r.controlSignal[i], b ? 'ON' : 'OFF');
      });
    });

    it('pseudoCode contains the hexagram name', () => {
      const r = engine.tranceive('hello');
      assert.ok(r.pseudoCode.includes(r.hexCode.name));
    });
  });

  describe('operate()', () => {
    it('cuo flips all bits', () => {
      const r = engine.operate('cuo', 'hello');
      const bits = engine.lookup('hello').bin;
      const expected = bits.split('').map(b => b === '0' ? '1' : '0').join('');
      assert.equal(r.resultBin, expected);
    });

    it('zong reverses bit order', () => {
      const r = engine.operate('zong', 'hello');
      const bits = engine.lookup('hello').bin;
      const expected = bits.split('').reverse().join('');
      assert.equal(r.resultBin, expected);
    });

    it('bian with single input flips all bits', () => {
      const r = engine.operate('bian', 'hello');
      const bits = engine.lookup('hello').bin;
      const expected = bits.split('').map(b => b === '0' ? '1' : '0').join('');
      assert.equal(r.resultBin, expected);
    });

    it('bian with secondInput XORs', () => {
      const r = engine.operate('bian', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b ^ w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('AND works correctly', () => {
      const r = engine.operate('AND', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b & w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('AND throws without secondInput', () => {
      assert.throws(() => engine.operate('AND', 'hello'), /needs secondInput/);
    });

    it('OR works correctly', () => {
      const r = engine.operate('OR', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b | w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('OR throws without secondInput', () => {
      assert.throws(() => engine.operate('OR', 'hello'), /needs secondInput/);
    });

    it('XOR works correctly', () => {
      const r = engine.operate('XOR', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b ^ w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('XOR throws without secondInput', () => {
      assert.throws(() => engine.operate('XOR', 'hello'), /needs secondInput/);
    });

    it('unknown op throws', () => {
      assert.throws(() => engine.operate('INVALID', 'hello'), /Unknown op/);
    });
  });

  describe('controlSignal()', () => {
    it('returns array of 6 ON/OFF strings', () => {
      const sig = engine.controlSignal('hello');
      assert.equal(sig.length, 6);
      sig.forEach(s => assert.ok(s === 'ON' || s === 'OFF'));
    });
  });

  describe('hash distribution', () => {
    it('distributes 1000 inputs across all 64 hexagrams', () => {
      const counts = new Array(64).fill(0);
      for (let i = 0; i < 1000; i++) {
        const r = engine.lookup(`input_${i}`);
        counts[r.index]++;
      }
      const empty = counts.filter(c => c === 0).length;
      assert.ok(empty <= 5, `${empty} hexagrams have zero hits — distribution may be skewed`);
    });
  });
});
```

- [ ] **步骤2：运行测试验证它们失败（此时文件不存在 → 不同步骤）**

实际上测试文件还不存在，创建后直接运行：

```bash
node --test src/core.test.js
```

期望：所有测试通过

- [ ] **步骤3：提交**

```bash
git add src/core.test.js
git commit -m "test: add comprehensive test suite for Hex64Engine"
```

### 任务 2：修复 examples 中的 bug

**文件：**
- 修改：`examples/engine-api.js:75`

**问题：** 第 75 行 `bianResult.lookup(secondInput)` — `operate()` 返回的 `bianResult` 是普通对象，没有 `.lookup()` 方法。需要用 `engine.lookup()` 代替。

- [ ] **步骤1：修复 bug**

将第 73-77 行从：
```js
const bianResult = engine.operate('bian', input, secondInput);
console.log('变爻 (XOR):');
console.log(`  ${bianResult.input.name} (${bianResult.input.bin})`);
console.log(`  XOR ${bianResult.lookup(secondInput)?.name || '未知'} (${bianResult.lookup(secondInput)?.bin || 'N/A'})`);
console.log(`  → ${bianResult.result.name} (${bianResult.resultBin})`);
```
改为：
```js
const bianResult = engine.operate('bian', input, secondInput);
const secondHex = engine.lookup(secondInput);
console.log('变爻 (XOR):');
console.log(`  ${bianResult.input.name} (${bianResult.input.bin})`);
console.log(`  XOR ${secondHex.name} (${secondHex.bin})`);
console.log(`  → ${bianResult.result.name} (${bianResult.resultBin})`);
```

- [ ] **步骤2：验证示例可运行**

```bash
node examples/engine-api.js
```

期望：无报错，正常输出所有结果

- [ ] **步骤3：提交**

```bash
git add examples/engine-api.js
git commit -m "fix: examples/engine-api.js — operate() result has no .lookup() method"
```

### 任务 3：完善 package.json

**文件：**
- 修改：`package.json`

- [ ] **步骤1：添加缺失字段**

```json
{
  "engines": {
    "node": ">=18"
  },
  "files": [
    "src/",
    "data/",
    "examples/",
    "bin/",
    "README.md",
    "LICENSE"
  ]
}
```

- [ ] **步骤2：提交**

```bash
git add package.json
git commit -m "chore: add engines field, expand files array"
```

---

## 执行顺序

1. 任务 3（package.json）— 快速配置
2. 任务 2（examples 修复）— 确保示例可运行
3. 任务 1（测试）— 最重要的质量保障
