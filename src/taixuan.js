// TaiXuan Ternary Encoder — 扬雄《太玄经》三进制编码原型
// 定位：三进制符号编码原型，与二进制 Hex64 并列，无任何玄学效力宣称
// 计算点：81首（3^4）+ 729赞（3^6），比苏联 SETUN 三进制计算机早 1900 年

function hash(input) {
  if (typeof input !== 'string') input = String(input);
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = (h << 5) + h + input.charCodeAt(i);
  }
  return h >>> 0;
}

const STATE_MAP = { yang: 0, yin: 1, cou: 2 };
const INV_STATE = { 0: 'yang', 1: 'yin', 2: 'cou' };

export class TaiXuanEncoder {
  encodeShou(text) {
    const h = hash(text);
    const shouIdx = h % 81;
    const ternary = [];
    let v = shouIdx;
    for (let i = 0; i < 4; i++) {
      ternary.push(v % 3);
      v = Math.floor(v / 3);
    }
    ternary.reverse();
    const ternStr = ternary.join('');
    const states = ternary.map(c => INV_STATE[c]);
    const vector = ternary.map(c => c / 2.0);
    return {
      input: text,
      mode: 'taixuan_shou',
      shouIdx,
      ternaryStr: ternStr,
      states,
      vector,
      note: '4位三进制编码原型，源自扬雄《太玄经》81首',
    };
  }

  encodeZan(text) {
    const h = hash(text);
    const zanIdx = h % 729;
    const ternary = [];
    let v = zanIdx;
    for (let i = 0; i < 6; i++) {
      ternary.push(v % 3);
      v = Math.floor(v / 3);
    }
    ternary.reverse();
    const ternStr = ternary.join('');
    const states = ternary.map(c => INV_STATE[c]);
    const vector = ternary.map(c => c / 2.0);
    return {
      input: text,
      mode: 'taixuan_zan',
      zanIdx,
      ternaryStr: ternStr,
      states,
      vector,
      note: '6位三进制编码原型，源自扬雄《太玄经》729赞',
    };
  }
}
