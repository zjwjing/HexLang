import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// DJB2 哈希（与 encoder.py 一致）
function djb2Hash(input: string): number {
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = ((h << 5) + h + input.charCodeAt(i)) & 0xFFFFFFFF;
  }
  return h >>> 0;
}

// 互卦计算
function computeInterHex(bits: number[]): string {
  const interBits = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]];
  return interBits.join('');
}

export interface HexResult {
  hex: {
    name: string;
    binary: string;
    tags: string[];
    weight: number;
    yao_weights: number[];
  };
  inter_hex: {
    name: string;
    binary: string;
  };
  note: string;
}

export class HexProvider {
  private hexDb: any[] = [];
  private binToHex: Map<string, any> = new Map();
  private tagToOp: Map<string, string> = new Map();
  private initialized = false;

  constructor() {
    this.init();
  }

  private init() {
    try {
      // 尝试从工作区加载数据
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders) return;

      const dataPath = path.join(workspaceFolders[0].uri.fsPath, 'data', 'hex64_full.json');
      if (!fs.existsSync(dataPath)) return;

      const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
      this.hexDb = data.hexagrams || [];
      for (const hex of this.hexDb) {
        this.binToHex.set(hex.bin, hex);
      }
      const tagToOp = data.tagToOp || {};
      for (const [tag, op] of Object.entries(tagToOp)) {
        this.tagToOp.set(tag, op as string);
      }
      this.initialized = true;
    } catch (err) {
      console.error('HexLang: failed to load hex64_full.json', err);
    }
  }

  encode(input: string): HexResult {
    if (!this.initialized) {
      throw new Error('HexLang 数据未加载，请确保工作区包含 data/hex64_full.json');
    }

    const hash = djb2Hash(input);
    const idx = hash % 64;
    const bin = idx.toString(2).padStart(6, '0');
    const hex = this.binToHex.get(bin);

    const bits = bin.split('').map(Number);
    const interBin = computeInterHex(bits);
    const interHex = this.binToHex.get(interBin);

    return {
      hex: {
        name: hex?.name || '未知',
        binary: bin,
        tags: hex?.tags || [],
        weight: hex?.weight || 0.5,
        yao_weights: hex?.yao_weights || [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
      },
      inter_hex: {
        name: interHex?.name || '未知',
        binary: interBin,
      },
      note: '确定性编码，非玄学',
    };
  }

  async explainCode(code: string): Promise<any> {
    const result = this.encode(code);
    return {
      ...result,
      input: code.substring(0, 200),
    };
  }

  async annotateFile(text: string): Promise<string> {
    const lines = text.split('\n');
    const annotated: string[] = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.length > 10 && !trimmed.startsWith('#') && !trimmed.startsWith('//')) {
        const result = this.encode(trimmed);
        const comment = trimmed.startsWith('def ') || trimmed.startsWith('class ')
          ? `  # [Hex64] ${result.hex.name}(${result.hex.tags.slice(0, 2).join('/')})`
          : `  // [Hex64] ${result.hex.name}(${result.hex.binary})`;
        annotated.push(line + comment);
      } else {
        annotated.push(line);
      }
    }

    return annotated.join('\n');
  }
}
