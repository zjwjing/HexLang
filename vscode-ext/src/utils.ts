/**
 * HexLang VSCode 扩展 - 工具函数
 */

// DJB2 哈希（与 encoder.py 一致）
export function djb2Hash(input: string): number {
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = ((h << 5) + h + input.charCodeAt(i)) & 0xFFFFFFFF;
  }
  return h >>> 0;
}

// 互卦计算
export function computeInterHex(bits: number[]): string {
  const interBits = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]];
  return interBits.join('');
}

// 根据二进制码获取卦象名称
export function getHexNameFromBin(bin: string): string {
  const binToName: Record<string, string> = {
    '000000': '坤为地', '000001': '山地剥', '000010': '水地比', '000011': '风地观',
    '000100': '地雷复', '000101': '山水蒙', '000110': '风水涣', '000111': '天地否',
    '001000': '地山谦', '001001': '雷山小过', '001010': '水山蹇', '001011': '天山遁',
    '001100': '火泽睽', '001101': '天泽履', '001110': '风泽中孚', '001111': '雷泽归妹',
    '010000': '地火明夷', '010001': '火火大有', '010010': '水火既济', '010011': '火水未济',
    '010100': '雷水解', '010101': '雷火丰', '010110': '泽风大过', '010111': '泽雷随',
    '011000': '地风升', '011001': '山风蛊', '011010': '水风井', '011011': '巽为风',
    '011100': '火风鼎', '011101': '火雷噬嗑', '011110': '泽山咸', '011111': '天山夬',
    '100000': '地雷复', '100001': '山雷颐', '100010': '水雷屯', '100011': '风雷益',
    '100100': '震为雷', '100101': '火雷噬嗑', '100110': '泽雷随', '100111': '天雷无妄',
    '101000': '地泽临', '101001': '山泽损', '101010': '水泽节', '101011': '风泽中孚',
    '101100': '火泽睽', '101101': '天泽履', '101110': '兑为泽', '101111': '天夬',
    '110000': '地天泰', '110001': '天山遁', '110010': '水天需', '110011': '风天小畜',
    '110100': '雷天大壮', '110101': '火天大有', '110110': '泽天夬', '110111': '乾为天',
    '111000': '天地否', '111001': '山天大畜', '111010': '水天需', '111011': '风天小畜',
    '111100': '雷天大壮', '111101': '火天大有', '111110': '泽天夬', '111111': '乾为天',
  };
  return binToName[bin] || '未知';
}

// 格式化爻权重显示
export function formatYaoWeights(weights: number[]): string {
  const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
  return weights.map((w, i) => `${yaoNames[i]}=${w.toFixed(2)}`).join(', ');
}

// 生成 Markdown 格式的卦象信息
export function generateHexMarkdown(hex: any, interHex?: any): string {
  let md = `**[Hex64] ${hex.name || '未知'}** \`${hex.binary || ''}\`\n\n`;
  
  if (hex.english) {
    md += `*${hex.english}*\n\n`;
  }
  
  md += `标签: ${(hex.tags || []).join(', ')}\n\n`;
  md += `权重: ${hex.weight ?? 'N/A'}\n\n`;
  
  if (hex.yao_weights) {
    md += `爻权重: ${formatYaoWeights(hex.yao_weights)}\n\n`;
  }
  
  if (interHex && interHex.name !== hex.name) {
    md += `互卦: ${interHex.name} (\`${interHex.binary || ''}\`)\n\n`;
  }
  
  md += `---\n*确定性编码，非玄学*`;
  return md;
}
