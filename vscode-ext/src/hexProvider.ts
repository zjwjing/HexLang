import * as vscode from 'vscode';
import { djb2Hash, computeInterHex } from './utils';

export interface HexResult {
  hex: {
    name: string;
    binary: string;
    tags: string[];
    weight: number;
    yao_weights: number[];
    english: string;
    pinyin: string;
  };
  inter_hex: {
    name: string;
    binary: string;
  };
  note: string;
}

export class HexProvider {
  private hexDb: Map<string, any> = new Map();
  private binToIndex: Map<string, number> = new Map();
  private tagToOp: Map<string, string> = new Map();
  private initialized = false;
  private dataPath: string | null = null;
  private extensionContext: vscode.ExtensionContext | null = null;

  constructor() {
    // init 由 setExtensionContext 调用后触发
  }

  /**
   * 设置扩展上下文（由 extension.ts 在 activate 中调用）
   */
  setExtensionContext(ctx: vscode.ExtensionContext) {
    this.extensionContext = ctx;
    this.init();
  }

  /**
   * 智能数据加载策略：
   * 1. 优先从扩展内置数据 (media/)
   * 2. 其次从工作区加载（开发模式）
   */
  private async init() {
    // 1. 尝试从扩展内置目录加载
    if (this.extensionContext) {
      const builtInUri = vscode.Uri.joinPath(
        this.extensionContext.extensionUri,
        'media',
        'hex64_full.json'
      );
      if (await this.tryLoad(builtInUri, 'extension media')) {
        return;
      }
    }

    // 2. 尝试从工作区加载
    try {
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (workspaceFolders) {
        const candidates = [
          vscode.Uri.joinPath(workspaceFolders[0].uri, 'data', 'hex64_full.json'),
          vscode.Uri.joinPath(workspaceFolders[0].uri, 'data', 'hexagrams.json'),
        ];
        for (const uri of candidates) {
          if (await this.tryLoad(uri, 'workspace')) {
            return;
          }
        }
      }
    } catch {
      // 忽略
    }

    console.warn('[HexLang] No data source found. HexProvider is not initialized.');
  }

  private async tryLoad(uri: vscode.Uri, source: string): Promise<boolean> {
    try {
      const bytes = await vscode.workspace.fs.readFile(uri);
      const text = new TextDecoder().decode(bytes);
      const data = JSON.parse(text);
      this.dataPath = uri.toString();
      this.loadFromData(data);
      if (this.initialized) {
        console.log(`[HexLang] Loaded ${this.hexDb.size} hexagrams from ${source}`);
      }
      return this.initialized;
    } catch {
      return false;
    }
  }

  private loadFromData(data: any) {
    const hexagrams = Array.isArray(data) ? data : (data.hexagrams || []);

    for (const hex of hexagrams) {
      if (hex.bin && hex.name) {
        this.hexDb.set(hex.bin, {
          ...hex,
          tags: hex.tags || [],
          yao_weights: hex.yao_weights || [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
          english: hex.english || '',
          pinyin: hex.pinyin || '',
          weight: hex.weight ?? 0.5,
        });
        this.binToIndex.set(hex.bin, hexagrams.indexOf(hex));
      }
    }

    const tagToOp = data.tagToOp || {};
    for (const [tag, op] of Object.entries(tagToOp)) {
      this.tagToOp.set(tag, op as string);
    }

    this.initialized = true;
  }

  encode(input: string): HexResult {
    if (!this.initialized) {
      throw new Error('HexLang 数据未加载');
    }

    const hash = djb2Hash(input);
    const idx = hash % 64;
    const bin = idx.toString(2).padStart(6, '0');
    const hex = this.hexDb.get(bin);

    const bits = bin.split('').map(Number);
    const interBin = computeInterHex(bits);
    const interHex = this.hexDb.get(interBin);

    return {
      hex: {
        name: hex?.name || '未知',
        binary: bin,
        tags: hex?.tags || [],
        weight: hex?.weight ?? 0.5,
        yao_weights: hex?.yao_weights || [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        english: hex?.english || '',
        pinyin: hex?.pinyin || '',
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

  getAllHexagrams(): any[] {
    return Array.from(this.hexDb.values());
  }

  findByHexName(name: string): any | null {
    for (const hex of this.hexDb.values()) {
      if (hex.name === name) {
        return hex;
      }
    }
    return null;
  }

  findByBinary(bin: string): any | null {
    return this.hexDb.get(bin) || null;
  }

  getStats(): { total: number; initialized: boolean; dataPath: string | null } {
    return {
      total: this.hexDb.size,
      initialized: this.initialized,
      dataPath: this.dataPath,
    };
  }
}
