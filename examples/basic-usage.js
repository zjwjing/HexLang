/**
 * Hex64 基础使用示例
 * 
 * 演示 Hex64Engine 的核心 API 用法：
 * - 基本转码（tranceive）
 * - 特征向量提取
 * - 伪代码生成
 * - GPIO 控制信号
 * - 易经运算（错卦/综卦/变爻/叠加）
 */

import { Hex64Engine } from '../src/core.js';

// 创建引擎实例
const engine = new Hex64Engine();

// ============================================
// 1. 基本转码 — 将任意字符串映射到六十四卦
// ============================================
console.log('=== 1. 基本转码 ===\n');

const input = 'hello_world';
const result = engine.tranceive(input);

console.log(`输入: "${input}"`);
console.log(`卦名: ${result.hexCode.name} (${result.hexCode.en})`);
console.log(`二进制: ${result.hexCode.bin}`);
console.log(`分类: ${result.hexCode.category}`);
console.log(`权重: ${result.hexCode.weight}`);
console.log(`拼音: ${result.hexCode.pinyin}\n`);

// ============================================
// 2. 特征向量 — 6维二进制表示
// ============================================
console.log('=== 2. 特征向量 ===\n');

const vec = engine.featureVector(input);
console.log(`输入: "${input}"`);
console.log(`特征向量: [${vec.join(', ')}]`);
console.log(`GPIO 信号: ${engine.controlSignal(input).join(' | ')}`);
console.log();

// ============================================
// 3. 伪代码生成 — 从卦标签映射为操作码
// ============================================
console.log('=== 3. 伪代码生成 ===\n');

const code = engine.pseudoCode(input);
console.log(`HEX 伪代码: ${code}\n`);

// ============================================
// 4. 易经运算
// ============================================
console.log('=== 4. 易经运算 ===\n');

// 错卦（NOT）— 6位全部取反
const cuoResult = engine.operate('cuo', input);
console.log('错卦 (NOT):');
console.log(`  ${cuoResult.input.name} (${cuoResult.input.bin})`);
console.log(`  → ${cuoResult.result.name} (${cuoResult.resultBin})`);
console.log();

// 综卦（REV）— 爻序反转
const zongResult = engine.operate('zong', input);
console.log('综卦 (REV):');
console.log(`  ${zongResult.input.name} (${zongResult.input.bin})`);
console.log(`  → ${zongResult.result.name} (${zongResult.resultBin})`);
console.log();

// 变爻（XOR）— 与另一个输入异或
const secondInput = 'system_init';
const bianResult = engine.operate('bian', input, secondInput);
const secondHex = engine.lookup(secondInput);
console.log('变爻 (XOR):');
console.log(`  ${bianResult.input.name} (${bianResult.input.bin})`);
console.log(`  XOR ${secondHex?.name || '未知'} (${secondHex?.bin || 'N/A'})`);
console.log(`  → ${bianResult.result.name} (${bianResult.resultBin})`);
console.log();

// 叠加运算（AND/OR/XOR）
console.log('叠加运算:');

const andResult = engine.operate('AND', input, secondInput);
console.log(`  AND: ${andResult.input.bin} & ... = ${andResult.resultBin}`);

const orResult = engine.operate('OR', input, secondInput);
console.log(`  OR:  ${orResult.input.bin} | ... = ${orResult.resultBin}`);

const xorResult = engine.operate('XOR', input, secondInput);
console.log(`  XOR: ${xorResult.input.bin} ^ ... = ${xorResult.resultBin}`);
console.log();

// ============================================
// 5. 批量转码 — 多个输入的快速映射
// ============================================
console.log('=== 5. 批量转码 ===\n');

const inputs = ['init', 'error', 'success', 'deploy', 'rollback'];
inputs.forEach(text => {
  const r = engine.tranceive(text);
  console.log(`${text.padEnd(12)} → ${r.hexCode.name.padEnd(8)} [${r.hexCode.bin}] ${r.hexCode.category}`);
});
