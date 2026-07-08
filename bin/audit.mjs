import { HEXAGRAMS, TAG_TO_OP } from '../src/database.js';
import { readFileSync, existsSync } from 'node:fs';
import { Hex64Engine } from '../src/core.js';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

console.log('=== 审计 1: tagToOp 覆盖率 ===');
const allTags = new Set();
const tagToHexMap = {};
HEXAGRAMS.forEach((h, i) => {
  h.tags.forEach(t => {
    allTags.add(t);
    if (!tagToHexMap[t]) tagToHexMap[t] = [];
    tagToHexMap[t].push({ idx: i, name: h.name });
  });
});
const unmappedTags = [...allTags].filter(t => !TAG_TO_OP[t]);
const coveredTags = [...allTags].filter(t => TAG_TO_OP[t]);
console.log('总标签数:', allTags.size);
console.log('已映射:', coveredTags.length);
console.log('未映射:', unmappedTags.length);
if (unmappedTags.length > 0) {
  unmappedTags.forEach(t => {
    const sources = tagToHexMap[t].map(s => s.name).join(', ');
    console.log('  "' + t + '" -> 出现在: ' + sources);
  });
}

console.log('\n=== 审计 2: opTemplates 完整性 ===');
const engineHtml = readFileSync(ROOT + '/src/engine.html', 'utf-8');
const tmpl = engineHtml.match(/const opTemplates = \{(.+?)\};/s);
const templateKeys = tmpl ? [...tmpl[1].matchAll(/'(\w+)':\s*\{/g)].map(m => m[1]) : [];
const uniqueOpcodes = [...new Set(Object.values(TAG_TO_OP))].sort();
const missingTemplates = uniqueOpcodes.filter(op => !templateKeys.includes(op));
console.log('TAG_TO_OP 唯一 opcode 数:', uniqueOpcodes.length);
console.log('opTemplates 模板数:', templateKeys.length);
console.log('缺失模板:', missingTemplates.length);
if (missingTemplates.length > 0) {
  missingTemplates.forEach(op => {
    const mappedTags = Object.entries(TAG_TO_OP).filter(([,v]) => v === op).map(([k]) => k);
    console.log('  ' + op + ' <- ' + mappedTags.join(', '));
  });
}

console.log('\n=== 审计 3: 数据一致性 ===');
const hf = JSON.parse(readFileSync(ROOT + '/data/hex64_full.json', 'utf-8'));
const hq = JSON.parse(readFileSync(ROOT + '/data/hexagrams.json', 'utf-8'));
const hfNames = hf.hexagrams.map(h => h.bin + ' ' + h.name);
const hqNames = hq.map(h => h.bin + ' ' + h.name);
const hfOnly = hfNames.filter(n => !hqNames.includes(n));
const hqOnly = hqNames.filter(n => !hfNames.includes(n));
if (hfOnly.length === 0 && hqOnly.length === 0) {
  console.log('hex64_full.json 和 hexagrams.json 完全一致 [OK]');
} else {
  if (hfOnly.length > 0) console.log('hex64_full.json 独有:', hfOnly);
  if (hqOnly.length > 0) console.log('hexagrams.json 独有:', hqOnly);
}
console.log('hex64_full.json: ' + Object.keys(hf.tagToOp || {}).length + ' tagToOp, ' + (hf.hexagrams||[]).length + ' hexagrams');
console.log('hexagrams.json: ' + hq.length + ' hexagrams');

console.log('\n=== 审计 4: 每卦标签数 ===');
const low = HEXAGRAMS.map((h,i) => ({i,n:h.name,c:h.tags.length})).filter(x => x.c < 6);
if (low.length > 0) {
  low.forEach(t => console.log('  [' + t.i + '] ' + t.n + ': ' + t.c + ' 个标签 (应6)'));
} else {
  console.log('所有卦都有6个标签 [OK]');
}

console.log('\n=== 审计 5: 重复检查 ===');
const binSet = new Set(), nameSet = new Set();
const dupBins = [], dupNames = [];
HEXAGRAMS.forEach(h => {
  if (binSet.has(h.bin)) dupBins.push(h.bin); binSet.add(h.bin);
  if (nameSet.has(h.name)) dupNames.push(h.name); nameSet.add(h.name);
});
console.log(dupBins.length === 0 ? '无重复 binary [OK]' : '重复 binary: ' + dupBins.join(','));
console.log(dupNames.length === 0 ? '无重复 卦名 [OK]' : '重复 卦名: ' + dupNames.join(','));

console.log('\n=== 审计 6: Hex64Engine operate() 功能测试 ===');
const e = new Hex64Engine();
const tests = [
  ['lookup', () => { const r = e.lookup('hello'); return r && r.name ? 'OK' : 'FAIL'; }],
  ['tranceive', () => { const r = e.tranceive('hello'); return r.pseudoCode ? 'OK' : 'FAIL'; }],
  ['operate cuo', () => { const r = e.operate('cuo', 'hello'); return r.resultBin ? 'OK' : 'FAIL'; }],
  ['operate zong', () => { const r = e.operate('zong', 'hello'); return r.resultBin ? 'OK' : 'FAIL'; }],
  ['operate bian', () => { const r = e.operate('bian', 'hello'); return r.resultBin ? 'OK' : 'FAIL'; }],
  ['operate XOR', () => { const r = e.operate('XOR', 'hello', 'world'); return r.resultBin ? 'OK' : 'FAIL'; }],
  ['controlSignal', () => { const s = e.controlSignal('hello'); return s.length === 6 ? 'OK' : 'FAIL'; }],
];
tests.forEach(([name, fn]) => console.log('  ' + name + ': ' + fn()));

console.log('\n=== 审计 7: engine.html 特性检查 ===');
const html = readFileSync(ROOT + '/src/engine.html', 'utf-8');
const hasDarkMode = html.includes('data-theme');
const hasCopyBtn = html.includes('copy-btn');
const hasShareUrl = html.includes('shareLink');
const hasCompiler = html.includes('compileHex');
const hasOpTemplates = html.includes('opTemplates');
const hasAutoTrigger = html.includes('oninput');
const hasHistory = html.includes('addHistory');
console.log('  Dark mode: ' + (hasDarkMode ? 'YES' : 'NO'));
console.log('  Copy buttons: ' + (hasCopyBtn ? 'YES' : 'NO'));
console.log('  Share URL: ' + (hasShareUrl ? 'YES' : 'NO'));
console.log('  Compiler: ' + (hasCompiler ? 'YES' : 'NO'));
console.log('  OpTemplates: ' + (hasOpTemplates ? 'YES' : 'NO'));
console.log('  Auto-trigger ops: ' + (hasAutoTrigger ? 'YES' : 'NO'));
console.log('  History: ' + (hasHistory ? 'YES' : 'NO'));
console.log('  行数: ' + html.split('\n').length);

console.log('\n=== 审计 8: CLI 工具 ===');
console.log('  bin/hex64.js 存在: ' + (existsSync(ROOT + '/bin/hex64.js') ? 'YES' : 'NO'));
console.log('  Shebang: ' + (readFileSync(ROOT + '/bin/hex64.js','utf-8').startsWith('#!/usr/bin/env node') ? 'YES' : 'NO'));

// Summary
console.log('\n========================================');
console.log('  审计摘要');
console.log('========================================');
let issues = [];
if (unmappedTags.length > 0) issues.push(unmappedTags.length + ' 个未映射标签');
if (missingTemplates.length > 0) issues.push(missingTemplates.length + ' 个 opcode 使用通用回退模板（无自定义模板）');
if (low.length > 0) issues.push(low.length + ' 卦标签不足');
if (!hasDarkMode) issues.push('缺少暗色模式');
if (!hasCopyBtn) issues.push('缺少复制按钮');
if (!hasShareUrl) issues.push('缺少分享URL');
if (issues.length === 0) {
  console.log('  无问题 - 所有检查通过 [OK]');
} else {
  console.log('  发现 ' + issues.length + ' 个问题:');
  issues.forEach((s, i) => console.log('    ' + (i+1) + '. ' + s));
}
