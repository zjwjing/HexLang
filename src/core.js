import { HEXAGRAMS, TAG_TO_OP } from './database.js';
import { fileURLToPath } from 'node:url';
import { argv } from 'node:process';

function hash(input) {
  if (typeof input !== 'string') input = String(input);
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = (h << 5) + h + input.charCodeAt(i);
  }
  return h >>> 0;
}

export class Hex64Engine {
  constructor(database = HEXAGRAMS) {
    this.db = database;
    // O(1) bin -> entry index, built once
    this.binIndex = new Map(database.map((e, i) => [e.bin, i]));
  }

  lookup(input) {
    const h = hash(input);
    const idx = h % 64;
    const entry = this.db[idx];
    return {
      index: idx,
      hash: h,
      bin: entry?.bin ?? '000000',
      name: entry?.name ?? '未知',
      pinyin: entry?.pinyin ?? '',
      en: entry?.en ?? 'Unknown',
      category: entry?.category ?? '',
      tags: entry?.tags ?? [],
      weight: entry?.weight ?? 0,
    };
  }

  featureVector(input) {
    const hex = this.lookup(input);
    return hex.bin.split('').map(Number);
  }

  pseudoCode(input) {
    const hex = this.lookup(input);
    const ops = [...new Set(hex.tags.map(t => TAG_TO_OP[t] || t.toUpperCase()))];
    const body = ops.length ? ` { ${ops.join('; ')}; }` : ' { NOP; }';
    return `HEX(${hex.name})${body}`;
  }

  controlSignal(input) {
    return this.featureVector(input).map(b => b ? 'ON' : 'OFF');
  }

  tranceive(input) {
    const hex = this.lookup(input);
    const vec = hex.bin.split('').map(Number);
    const code = this.pseudoCode(input);
    const gpio = vec.map(b => b ? 'ON' : 'OFF');
    return {
      input,
      hexCode: {
        index: hex.index,
        bin: hex.bin,
        hexFont: hex.hex_font || '',
        name: hex.name,
        pinyin: hex.pinyin,
        en: hex.en,
        english: hex.english || '',
        category: hex.category,
        tags: hex.tags,
        weight: hex.weight,
      },
      featureVec: vec,
      pseudoCode: code,
      controlSignal: gpio,
    };
  }

  operate(op, input, secondInput) {
    const hex = this.lookup(input);
    const bits = hex.bin.split('').map(Number);
    let resultBits;

    // lookup second input once, outside the per-bit map
    const secondBits = secondInput
      ? this.lookup(secondInput).bin.split('').map(Number)
      : null;

    switch (op) {
      case 'cuo':
        resultBits = bits.map(b => b ^ 1);
        break;
      case 'zong':
        resultBits = [...bits].reverse();
        break;
      case 'bian':
        if (secondBits) {
          resultBits = bits.map((b, i) => b ^ secondBits[i]);
        } else {
          resultBits = bits.map(b => b ^ 1);
        }
        break;
      case 'AND':
        if (!secondBits) throw new Error('AND needs secondInput');
        resultBits = bits.map((b, i) => b & secondBits[i]);
        break;
      case 'OR':
        if (!secondBits) throw new Error('OR needs secondInput');
        resultBits = bits.map((b, i) => b | secondBits[i]);
        break;
      case 'XOR':
        if (!secondBits) throw new Error('XOR needs secondInput');
        resultBits = bits.map((b, i) => b ^ secondBits[i]);
        break;
      default:
        throw new Error(`Unknown op: ${op}`);
    }

    const resultBin = resultBits.join('');
    // O(1) lookup via prebuilt index instead of linear scan
    const resultIdx = this.binIndex.get(resultBin);
    const resultHex = resultIdx !== undefined ? this.db[resultIdx] : null;
    return {
      op,
      input: hex,
      result: resultHex || { bin: resultBin, name: '自定义卦', tags: [], weight: 0 },
      resultBin,
    };
  }
}

// CLI 自执行检测（跨平台兼容）
const isCLI = (() => {
  try {
    const current = fileURLToPath(import.meta.url);
    const script = argv[1];
    if (!script) return false;
    // 规范化路径分隔符后比较
    return current.replace(/\\/g, '/') === script.replace(/\\/g, '/');
  } catch {
    return false;
  }
})();

if (isCLI) {
  const engine = new Hex64Engine();
  const tests = ['Hello OpenCode', 'test', 'AI', '', 'hex64'];
  for (const t of tests) {
    const r = engine.tranceive(t);
    console.log(`\n输入: "${r.input}"`);
    console.log(`  卦索引: ${r.hexCode.index}`);
    console.log(`  二进制: ${r.hexCode.bin}`);
    console.log(`  卦名: ${r.hexCode.name}（${r.hexCode.en}）`);
    console.log(`  拼音: ${r.hexCode.pinyin}`);
    console.log(`  分类: ${r.hexCode.category}`);
    console.log(`  标签: ${r.hexCode.tags.join(', ')}`);
    console.log(`  权重: ${r.hexCode.weight}`);
    console.log(`  特征向量: [${r.featureVec.join(', ')}]`);
    console.log(`  伪代码: ${r.pseudoCode}`);
    console.log(`  GPIO: ${r.controlSignal.join(' | ')}`);
  }
}
