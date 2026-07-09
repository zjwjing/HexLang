import * as vscode from 'vscode';

// DJB2 哈希（与 encoder.py 一致）
function djb2Hash(input: string): number {
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = ((h << 5) + h + input.charCodeAt(i)) & 0xFFFFFFFF;
  }
  return h >>> 0;
}

export class HexHoverProvider implements vscode.HoverProvider {
  private hexDb: Map<string, any> = new Map();
  private initialized = false;

  constructor() {
    this.init();
  }

  private init() {
    try {
      const { readFileSync } = require('fs');
      const { join } = require('path');
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders) return;

      const dataPath = join(workspaceFolders[0].uri.fsPath, 'data', 'hex64_full.json');
      const data = JSON.parse(readFileSync(dataPath, 'utf-8'));
      const hexagrams = data.hexagrams || [];
      for (const hex of hexagrams) {
        this.hexDb.set(hex.bin, hex);
      }
      this.initialized = true;
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
    md.appendMarkdown(`**[Hex64] ${hex.name}** (${bin})\n\n`);
    md.appendMarkdown(`标签: ${hex.tags?.join(', ') || '无'}\n\n`);
    md.appendMarkdown(`权重: ${hex.weight}\n\n`);
    md.appendMarkdown(`爻权重: ${weightStr}\n\n`);
    md.appendMarkdown(`*确定性编码，非玄学*`);
    md.isTrusted = true;

    return new vscode.Hover(md);
  }
}
