import * as vscode from 'vscode';
import { HexProvider, HexResult } from './hexProvider';
import { HexHoverProvider } from './hover';
import { generateHexMarkdown } from './utils';

let provider: HexProvider;

export function activate(context: vscode.ExtensionContext) {
  provider = new HexProvider();
  provider.setExtensionContext(context);

  // ─── 命令 1：解释选中逻辑 ─────────────────────────────
  const explainCmd = vscode.commands.registerCommand('hexlang.explainSelection', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showWarningMessage('没有打开的编辑器');
      return;
    }

    const selection = editor.document.getText(editor.selection);
    if (!selection) {
      vscode.window.showInformationMessage('请先选中一段代码');
      return;
    }

    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Hex64: 分析逻辑...',
      cancellable: false,
    }, async () => {
      try {
        const result = await provider.explainCode(selection);
        showExplainPanel(result);
      } catch (err: any) {
        vscode.window.showErrorMessage(`Hex64 分析失败: ${err.message}`);
      }
    });
  });

  // ─── 命令 2：标注当前文件 ─────────────────────────────
  const annotateCmd = vscode.commands.registerCommand('hexlang.annotateFile', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showWarningMessage('没有打开的编辑器');
      return;
    }

    const text = editor.document.getText();
    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Hex64: 标注文件...',
      cancellable: false,
    }, async () => {
      try {
        const annotated = await provider.annotateFile(text);
        
        // 创建新文档显示标注结果
        const doc = await vscode.workspace.openTextDocument({
          content: annotated,
          language: editor.document.languageId,
        });
        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        
        vscode.window.showInformationMessage(`Hex64: 已标注 ${text.split('\n').length} 行`);
      } catch (err: any) {
        vscode.window.showErrorMessage(`Hex64 标注失败: ${err.message}`);
      }
    });
  });

  // ─── 命令 3：打开健康度仪表盘 ─────────────────────────────
  const dashboardCmd = vscode.commands.registerCommand('hexlang.showDashboard', () => {
    if (!provider) {
      vscode.window.showWarningMessage('Hex64 扩展未初始化');
      return;
    }

    const stats = provider.getStats();
    const hexagrams = provider.getAllHexagrams();
    
    // 统计卦象分布
    const distribution = new Map<string, number>();
    for (const hex of hexagrams) {
      distribution.set(hex.name, (distribution.get(hex.name) || 0) + 1);
    }

    const panel = vscode.window.createWebviewPanel(
      'hexlangDashboard',
      'Hex64 系统仪表盘',
      vscode.ViewColumn.One,
      { enableScripts: true }
    );

    panel.webview.html = getDashboardHtml(stats, hexagrams.length, distribution);
  });

  // ─── 命令 4：快速查询卦象 ─────────────────────────────
  const quickQueryCmd = vscode.commands.registerCommand('hexlang.quickQuery', async () => {
    const input = await vscode.window.showInputBox({
      prompt: '输入任意文本进行 Hex64 编码',
      placeHolder: '例如: "function main() {}"',
      validateInput: (value) => value.trim().length > 0 ? null : '请输入非空文本',
    });

    if (!input) return;

    try {
      const result = provider.encode(input);
      showExplainPanel(result);
    } catch (err: any) {
      vscode.window.showErrorMessage(`Hex64 编码失败: ${err.message}`);
    }
  });

  // ─── 悬停提供器 ─────────────────────────────
  const hoverProvider = new HexHoverProvider();
  const hoverDisposable = vscode.languages.registerHoverProvider(
    ['python', 'javascript', 'typescript', 'rust', 'go', 'java', 'c'],
    hoverProvider
  );

  context.subscriptions.push(
    explainCmd,
    annotateCmd,
    dashboardCmd,
    quickQueryCmd,
    hoverDisposable
  );
}

/**
 * 显示解释面板
 */
function showExplainPanel(result: any) {
  const hex = result.hex || {};
  const inter = result.inter_hex || {};
  
  const panel = vscode.window.createWebviewPanel(
    'hexlangExplain',
    `Hex64: ${hex.name || '分析结果'}`,
    vscode.ViewColumn.Beside,
    { enableScripts: true }
  );

  panel.webview.html = getWebviewContent(result);
}

/**
 * 仪表盘 HTML
 */
function getDashboardHtml(stats: any, totalHex: number, distribution: Map<string, number>): string {
  const distEntries = Array.from(distribution.entries()).slice(0, 10);
  const distHtml = distEntries.map(([name, count]) => `
    <tr>
      <td>${name}</td>
      <td>${count}</td>
      <td><div style="background:#00ff88;height:8px;width:${Math.min(count * 10, 100)}px;"></div></td>
    </tr>
  `).join('');

  return `<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, sans-serif; padding: 20px; background: #0a0a1a; color: #e4e4e4; }
    .card { background: #111128; border: 1px solid #2a2a4a; border-radius: 8px; padding: 16px; margin: 12px 0; }
    .stat { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1a1a2e; }
    .stat:last-child { border-bottom: none; }
    .label { color: #888; }
    .value { color: #00ff88; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px; text-align: left; }
    th { color: #888; border-bottom: 1px solid #2a2a4a; }
    h2 { color: #00ff88; margin-top: 0; }
  </style>
</head>
<body>
  <h2>Hex64 系统仪表盘</h2>
  
  <div class="card">
    <h2>系统状态</h2>
    <div class="stat"><span class="label">初始化状态</span><span class="value">${stats.initialized ? '✅ 就绪' : '❌ 未就绪'}</span></div>
    <div class="stat"><span class="label">卦象总数</span><span class="value">${totalHex}</span></div>
    <div class="stat"><span class="label">数据源</span><span class="value" style="font-size:0.8rem;">${stats.dataPath || '自动检测'}</span></div>
  </div>
  
  <div class="card">
    <h2>Top 10 卦象频率</h2>
    <table>
      <tr><th>卦名</th><th>计数</th><th>分布</th></tr>
      ${distHtml}
    </table>
  </div>
</body>
</html>`;
}

/**
 * 解释面板 HTML
 */
function getWebviewContent(result: any): string {
  const hex = result.hex || {};
  const inter = result.inter_hex || {};
  
  const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
  const yaoWeights = hex.yao_weights || [0.5, 0.5, 0.5, 0.5, 0.5, 0.5];
  
  const yaoHtml = yaoWeights.map((w: number, i: number) => {
    const barWidth = Math.round(w * 100);
    return `<div style="display:flex;align-items:center;margin:4px 0;">
      <span style="width:40px;color:#888;">${yaoNames[i]}</span>
      <div style="flex:1;background:#1a1a2e;border-radius:4px;height:8px;margin:0 8px;">
        <div style="background:#00ff88;height:100%;width:${barWidth}%;border-radius:4px;"></div>
      </div>
      <span style="width:40px;text-align:right;">${w.toFixed(2)}</span>
    </div>`;
  }).join('');

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
    .bin-code { font-family: monospace; color: #ff8800; font-size: 1.2rem; }
  </style>
</head>
<body>
  <div class="card">
    <div class="hex-name">${hex.name || '未知'} <span class="bin-code">[${hex.binary || '-'}]</span></div>
    <div class="label" style="margin-top:4px;">${hex.english || hex.pinyin || ''}</div>
    <div class="label" style="margin-top:4px;">拼音: ${hex.pinyin || '-'}</div>
    <div class="label" style="margin-top:8px;">标签</div>
    <div>${(hex.tags || []).map((t: string) => '<span class="tag">' + t + '</span>').join('')}</div>
  </div>
  
  <div class="card">
    <div class="label">互卦</div>
    <div style="margin-top:4px;">${inter.name || '无'} (${inter.binary || '-'})</div>
  </div>
  
  <div class="card">
    <div class="label">爻权重</div>
    <div style="margin-top:8px;">${yaoHtml}</div>
  </div>
  
  <div class="note">${result.note || '确定性编码，非玄学'}</div>
</body>
</html>`;
}

export function deactivate() {}
