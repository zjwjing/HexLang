import { HEXAGRAMS } from './database.js';

function hash(input) {
  if (typeof input !== 'string') input = String(input);
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = (h << 5) + h + input.charCodeAt(i);
  }
  return h >>> 0;
}

function xor(a, b) {
  return a ^ b;
}

export class Hex64Engine {
  constructor(database = HEXAGRAMS) {
    this.db = database;
  }

  lookup(input) {
    const h = hash(input);
    const idx = h % 64;
    return { ...this.db[idx], index: idx, hash: h };
  }

  featureVector(input) {
    const hex = this.lookup(input);
    return hex.bin.split('').map(c => parseFloat(c));
  }

  pseudoCode(input) {
    const hex = this.lookup(input);
    const mapping = {
      '初始化': 'LOAD',
      '启动': 'RUN',
      '停止': 'STOP',
      '存储': 'SAVE',
      '等待': 'WAIT',
      '更新': 'UPDATE',
      '对比': 'CMP',
      '翻转': 'FLIP',
    };
    const ops = hex.tags.map(t => mapping[t] || t.toUpperCase());
    const unique = [...new Set(ops)];
    const body = unique.length ? ` { ${unique.join('; ')}; }` : ' { NOP; }';
    return `HEX(${hex.name})${body}`;
  }

  controlSignal(input) {
    return this.featureVector(input).map(b => b ? 'ON' : 'OFF');
  }

  tranceive(input) {
    const hex = this.lookup(input);
    const vec = this.featureVector(input);
    const code = this.pseudoCode(input);
    const gpio = this.controlSignal(input);
    return {
      input,
      hexCode: {
        index: hex.index,
        bin: hex.bin,
        name: hex.name,
        weight: hex.weight,
      },
      featureVec: vec,
      pseudoCode: code,
      controlSignal: gpio,
    };
  }

  operate(op, input) {
    const hex = this.lookup(input);
    const bits = hex.bin.split('').map(Number);
    switch (op) {
      case 'bian':     return bits.map(b => b ^ 1);
      case 'cuo':      return bits.map(b => b ^ 1);
      case 'zong':     return bits.reverse();
      case 'AND':      return bits.map(b => b & 1);
      case 'OR':       return bits.map(b => b | 1);
      case 'XOR':      return bits.map(b => b ^ 1);
      case 'NOT':      return bits.map(b => b ^ 1);
      default:         return bits;
    }
  }
}

if (typeof process !== 'undefined' && process.argv[1] && import.meta.url.replace('file:///', '').replace(/\\/g, '/').endsWith(process.argv[1].replace(/\\/g, '/'))) {
  const engine = new Hex64Engine();
  const tests = ['Hello OpenCode', 'test', 'AI', '', 'hex64'];
  for (const t of tests) {
    const r = engine.tranceive(t);
    console.log(`\n输入: "${r.input}"`);
    console.log(`  卦索引: ${r.hexCode.index}`);
    console.log(`  二进制: ${r.hexCode.bin}`);
    console.log(`  卦名: ${r.hexCode.name}`);
    console.log(`  权重: ${r.hexCode.weight}`);
    console.log(`  特征向量: [${r.featureVec.join(', ')}]`);
    console.log(`  伪代码: ${r.pseudoCode}`);
    console.log(`  GPIO: ${r.controlSignal.join(' | ')}`);
  }
}
