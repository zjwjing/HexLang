import * as vscode from 'vscode';
import { HexProvider } from './hexProvider';
import { HexHoverProvider } from './hover';

export function activate(context: vscode.ExtensionContext) {
  const provider = new HexProvider();

  // 命令：解释选中逻辑
  const explainCmd = vscode.commands.registerCommand('hexlang.explainSelection', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const selection = editor.document.getText(editor.selection);
    if (!selection) {
      vscode.window.showInformationMessage('请先选中一段代码');
      return;
    }

    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Hex64: 分析逻辑...',
      cancellable: false
    }, async () => {
      try {
        const result = await provider.explainCode(selection);
        // 在新面板显示结果
        const panel = vscode.window.createWebviewPanel(
          'hexlangExplain',
          'Hex64 逻辑分析',
          vscode.ViewColumn.Beside,
          {}
        );
        panel.webview.html = getWebviewContent(result);
      } catch (err: any) {
        vscode.window.showErrorMessage(`Hex64 分析失败: ${err.message}`);
      }
    });
  });

  // 命令：标注当前文件
  const annotateCmd = vscode.commands.registerCommand('hexlang.annotateFile', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const text = editor.document.getText();
    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Hex64: 标注文件...',
      cancellable: false
    }, async () => {
      try {
        const result = await provider.annotateFile(text);
        // 在输出面板显示
        const output = vscode.window.createOutputChannel('Hex64');
        output.clear();
        output.appendLine(result);
        output.show();
      } catch (err: any) {
        vscode.window.showErrorMessage(`Hex64 标注失败: ${err.message}`);
      }
    });
  });

  // 悬停提供器
  const hoverProvider = new HexHoverProvider();
  const hoverDisposable = vscode.languages.registerHoverProvider(
    ['python', 'javascript', 'typescript'],
    hoverProvider
  );

  context.subscriptions.push(explainCmd, annotateCmd, hoverDisposable);
}

function getWebviewContent(result: any): string {
  const hex = result.hex || {};
  const inter = result.inter_hex || {};
  return `<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, sans-serif; padding: 16px; background: #0a0a1a; color: #e4e4e4; }
    .card { background: #111128; border: 1px solid #2a2a4a; border-radius: 8px; padding: 16px; margin: 8px 0; }
    .hex-name { font-size: 1.5rem; color: #00ff88; }
    .label { color: #888; font-size: 0.85rem; }
    .tag { display: inline-block; background: #1a1a2e; padding: 2px 8px; border-radius: 4px; margin: 2px; font-size: 0.8rem; }
    .note { color: #666; font-size: 0.75rem; margin-top: 12px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="hex-name">${hex.name || '未知'} <span class="label">${hex.binary || ''}</span></div>
    <div class="label">标签</div>
    <div>${(hex.tags || []).map((t: string) => `<span class="tag">${t}</span>`).join('')}</div>
  </div>
  <div class="card">
    <div class="label">互卦</div>
    <div>${inter.name || '无'} (${inter.binary || '-'})</div>
  </div>
  <div class="card">
    <div class="label">爻权重</div>
    <div>${(hex.yao_weights || []).map((w: number, i: number) => {
      const names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
      return `${names[i]}=${w.toFixed(2)}`;
    }).join(', ')}</div>
  </div>
  <div class="note">${result.note || '确定性编码，非玄学'}</div>
</body>
</html>`;
}

export function deactivate() {}
