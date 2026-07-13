import { HEXAGRAMS, TAG_TO_OP } from './database.js';

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

  encodeSeeded(idempotencyKey) {
    const h = hash(idempotencyKey);
    const idx = h % 64;
    const hex = this.db[idx];
    return {
      index: idx,
      hash: h,
      bin: hex?.bin ?? '000000',
      hexFont: hex?.hex_font || '',
      name: hex?.name ?? '未知',
      pinyin: hex?.pinyin ?? '',
      en: hex?.en ?? 'Unknown',
      english: hex?.english || '',
      category: hex?.category ?? '',
      tags: hex?.tags ?? [],
      weight: hex?.weight ?? 0,
      yaoWeights: hex?.yao_weights ?? [0, 0, 0, 0, 0, 0],
    };
  }

  encodeFangtu(input) {
    const h = hash(input);
    const high32 = (h >>> 0) % 8;
    const low32 = (h >>> 0) % 8;
    const outerBin = high32.toString(2).padStart(3, '0');
    const innerBin = low32.toString(2).padStart(3, '0');
    const fullBin = outerBin + innerBin;
    const idx = this.binIndex.get(fullBin);
    const hex = idx !== undefined ? this.db[idx] : null;
    return {
      input,
      mode: 'fangtu',
      index: idx ?? -1,
      hash: h,
      bin: fullBin,
      hexFont: hex?.hex_font || '',
      name: hex?.name ?? '未知',
      pinyin: hex?.pinyin ?? '',
      en: hex?.en ?? 'Unknown',
      english: hex?.english || '',
      category: hex?.category ?? '',
      tags: hex?.tags ?? [],
      weight: hex?.weight ?? 0,
      yaoWeights: hex?.yao_weights ?? [0, 0, 0, 0, 0, 0],
      meta: {
        outer3bit: outerBin,
        inner3bit: innerBin,
      },
      note: '8×8 Cartesian积方阵模式，源自邵雍先天方图',
    };
  }

  encodeYaochen(input, timestamp) {
    if (timestamp === undefined) timestamp = Math.floor(Date.now() / 1000);
    const h = hash(input);
    const hexIdx = h % 64;
    const hex = this.db[hexIdx];
    const yaochen = Math.floor(timestamp) % 384;
    const hexInnerIdx = Math.floor(yaochen / 6);
    const yaoIdx = yaochen % 6;
    const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
    return {
      input,
      mode: 'yaochen',
      index: hexIdx,
      hash: h,
      bin: hex?.bin ?? '000000',
      hexFont: hex?.hex_font || '',
      name: hex?.name ?? '未知',
      pinyin: hex?.pinyin ?? '',
      en: hex?.en ?? 'Unknown',
      english: hex?.english || '',
      category: hex?.category ?? '',
      tags: hex?.tags ?? [],
      weight: hex?.weight ?? 0,
      yaoWeights: hex?.yao_weights ?? [0, 0, 0, 0, 0, 0],
      meta: {
        timestamp: Math.floor(timestamp),
        yaochen,
        hexInnerIdx,
        yaoIdx,
        yaoName: yaoNames[yaoIdx],
      },
      note: 'mod384循环计数器原型，源自京房纳甲',
    };
  }

  encodeYubu(seed) {
    const luoshu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]];
    const seedHash = hash(seed);
    const bytes = [];
    let h = seedHash;
    for (let i = 0; i < 9; i++) {
      bytes.push(h & 0xff);
      h = (h * 1103515245 + 12345) >>> 0;
    }
    const sortedIndices = [...Array(9).keys()].sort((a, b) => bytes[a] - bytes[b]);
    const positions = [];
    const values = [];
    for (const idx of sortedIndices) {
      const row = Math.floor(idx / 3);
      const col = idx % 3;
      positions.push([row, col]);
      values.push(luoshu[row][col]);
    }
    const vector = values.map(v => v / 9.0);
    // map seed to hex for consistent return shape
    const hexIdx = seedHash % 64;
    const hex = this.db[hexIdx];
    return {
      seed,
      mode: 'yubu_prng',
      index: hexIdx,
      hash: seedHash,
      bin: hex?.bin ?? '000000',
      hexFont: hex?.hex_font || '',
      name: hex?.name ?? '未知',
      pinyin: hex?.pinyin ?? '',
      en: hex?.en ?? 'Unknown',
      english: hex?.english || '',
      category: hex?.category ?? '',
      tags: hex?.tags ?? [],
      weight: hex?.weight ?? 0,
      yaoWeights: hex?.yao_weights ?? [0, 0, 0, 0, 0, 0],
      luoshuMatrix: luoshu,
      sortedIndices,
      positions,
      values,
      vector,
      note: '3×3网格Hamiltonian游走确定性PRNG原型，源自道门禹步',
    };
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
        yaoWeights: hex.yao_weights || [0, 0, 0, 0, 0, 0],
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
      case 'hu':
        // 互卦：取二三四五爻，二三四为下卦、三四五为上卦
        resultBits = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]];
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
