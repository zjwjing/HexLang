import * as vscode from 'vscode';
import { djb2Hash, computeInterHex } from './utils';

export class HexHoverProvider implements vscode.HoverProvider {
  private hexDb: Map<string, any> = new Map();
  private initialized = false;

  constructor() {
    this.init();
  }

  private init() {
    try {
      // 尝试从工作区加载数据
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders) return;

      // 尝试多种数据文件路径
      const candidates = [
        'data/hex64_full.json',
        'data/hexagrams.json',
      ];

      for (const ws of workspaceFolders) {
        for (const candidate of candidates) {
          const dataPath = vscode.Uri.joinPath(ws.uri, candidate);
          try {
            const data = JSON.parse(vscode.workspace.fs.readFile(dataPath).toString());
            const hexagrams = Array.isArray(data) ? data : (data.hexagrams || []);
            
            for (const hex of hexagrams) {
              if (hex.bin && hex.name) {
                this.hexDb.set(hex.bin, {
                  ...hex,
                  tags: hex.tags || [],
                  yao_weights: hex.yao_weights || [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                  english: hex.english || '',
                  pinyin: hex.pinyin || '',
                });
              }
            }
            
            this.initialized = true;
            console.log(`[HexLang Hover] Loaded ${this.hexDb.size} hexagrams`);
            return;
          } catch {
            continue;
          }
        }
      }
    } catch {
      // 静默失败，悬停功能不可用
    }
  }

  provideHover(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken
  ): vscode.ProviderResult<vscode.Hover> {
    if (!this.initialized) return null;

    const config = vscode.workspace.getConfiguration('hexlang');
    if (!config.get('enableHover', true)) return null;

    // 获取光标所在行
    const line = document.lineAt(position.line).text;
    const trimmed = line.trim();

    // 只对函数定义、类定义、有意义的代码行显示悬停
    if (trimmed.length < 10) return null;
    if (trimmed.startsWith('#') || trimmed.startsWith('//') || trimmed.startsWith('*')) return null;

    const hash = djb2Hash(trimmed);
    const idx = hash % 64;
    const bin = idx.toString(2).padStart(6, '0');
    const hex = this.hexDb.get(bin);

    if (!hex) return null;

    const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
    const weights = hex.yao_weights || [0.5, 0.5, 0.5, 0.5, 0.5, 0.5];
    const weightStr = weights.map((w: number, i: number) => `${yaoNames[i]}=${w.toFixed(2)}`).join(', ');

    const md = new vscode.MarkdownString();
    md.appendMarkdown(`**[Hex64] ${hex.name}** \`${bin}\`\n\n`);
    if (hex.english) {
      md.appendMarkdown(`*${hex.english}*\n\n`);
    }
    md.appendMarkdown(`标签: ${hex.tags?.join(', ') || '无'}\n\n`);
    md.appendMarkdown(`权重: ${hex.weight ?? 'N/A'}\n\n`);
    md.appendMarkdown(`爻权重: ${weightStr}\n\n`);
    
    // 互卦
    const bits = bin.split('').map(Number);
    const interBin = computeInterHex(bits);
    const interHex = this.hexDb.get(interBin);
    if (interHex && interHex.name !== hex.name) {
      md.appendMarkdown(`互卦: ${interHex.name} (\`${interBin}\`)\n\n`);
    }
    
    md.appendMarkdown(`---\n*确定性编码，非玄学*`);
    md.isTrusted = true;

    return new vscode.Hover(md);
  }
}
