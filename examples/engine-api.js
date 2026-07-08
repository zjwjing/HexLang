/**
 * Hex64Engine 高级 API 示例
 * 
 * 演示更复杂的用法：
 * - 自定义数据库注入
 * - 运算链式调用
 * - 哈希碰撞检测
 */

import { Hex64Engine } from '../src/core.js';

// ============================================
// 1. 自定义数据库
// ============================================
console.log('=== 1. 自定义数据库注入 ===\n');

// 从默认数据库克隆，替换前两卦
import { HEXAGRAMS } from '../src/database.js';
const customDb = HEXAGRAMS.map((h, i) => {
  if (i === 0) return { ...h, name: '自定义坤', tags: ['初始化'], weight: 1.0 };
  if (i === 1) return { ...h, name: '自定义乾', tags: ['执行'], weight: 0.9 };
  return h;
});

const customEngine = new Hex64Engine(customDb);
const customResult = customEngine.tranceive('test');
console.log('自定义数据库示例:');
console.log(`  卦名: ${customResult.hexCode.name}`);
console.log(`  权重: ${customResult.hexCode.weight}\n`);

// ============================================
// 2. 运算链式调用
// ============================================
console.log('=== 2. 运算链式调用 ===\n');

const input = 'chain_test';
let current = input;

console.log(`起始: ${current}`);
console.log(`  → ${new Hex64Engine().tranceive(current).hexCode.name}`);

// 错卦 → 综卦 → 变爻
const engine = new Hex64Engine();

const step1 = engine.operate('cuo', current);
console.log(`错卦: ${step1.result.name} (${step1.resultBin})`);

const step2 = engine.operate('zong', step1.resultBin);
console.log(`综卦: ${step2.result.name} (${step2.resultBin})`);

const step3 = engine.operate('bian', current, step2.resultBin);
console.log(`变爻: ${step3.result.name} (${step3.resultBin})\n`);

// ============================================
// 3. 哈希分布检测
// ============================================
console.log('=== 3. 哈希分布检测 ===\n');

const testInputs = Array.from({ length: 100 }, (_, i) => `input_${i}`);
const distribution = new Array(64).fill(0);

testInputs.forEach(text => {
  const idx = engine.lookup(text).index;
  distribution[idx]++;
});

console.log('64卦命中分布:');
distribution.forEach((count, idx) => {
  const bar = '█'.repeat(count);
  console.log(`  ${idx.toString().padStart(2)}: ${bar.padEnd(10)} (${count})`);
});

// ============================================
// 4. 特征向量可视化
// ============================================
console.log('\n=== 4. 特征向量可视化 ===\n');

const visInputs = ['alpha', 'beta', 'gamma', 'delta'];
visInputs.forEach(text => {
  const r = engine.tranceive(text);
  const vecStr = r.featureVec.map(v => v ? '█' : '·').join(' ');
  console.log(`${text.padEnd(8)} [${r.hexCode.bin}] ${vecStr} ${r.hexCode.name}`);
});
