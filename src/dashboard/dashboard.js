// HexLang 系统健康度仪表盘 - 核心逻辑
// 定位：确定性符号编码 · 非玄学工程工具

import { Hex64Engine } from '../core.js';

const engine = new Hex64Engine();
let config = null;
let history = [];

// 加载配置
async function loadConfig() {
  const resp = await fetch('./config.json');
  config = await resp.json();
}

// 根据指标计算 6 位二进制
function metricsToBin(metrics) {
  const bits = [];
  const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
  for (const yao of yaoNames) {
    const rule = config.mapping[yao];
    const value = metrics[rule.metric];
    const bit = value >= rule.threshold ? rule.yang : rule.yin;
    bits.push(bit);
  }
  return bits.join('');
}

// 计算互卦
function calcInterHex(bin) {
  const bits = bin.split('').map(Number);
  const interBits = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]];
  return interBits.join('');
}

// 渲染卦象输出
function renderHex(bin, label) {
  const idx = parseInt(bin, 2);
  const hexData = engine.db[idx];
  return `${label}: ${bin} ${hexData?.name ?? '未知'} (${hexData?.english ?? ''})`;
}

// 渲染爻权重条形图
function renderWeights(metrics) {
  const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
  const bars = yaoNames.map((yao, i) => {
    const rule = config.mapping[yao];
    const value = metrics[rule.metric];
    const ratio = value / rule.threshold;
    const color = ratio > 1.2 ? '#ff4444' : ratio > 0.8 ? '#ffaa00' : '#00ff00';
    const width = Math.min(ratio * 50, 100);
    return `
      <div style="display:flex;align-items:center;margin:4px 0">
        <span style="width:60px;font-size:0.8rem;color:#888">${yao}</span>
        <div style="flex:1;height:20px;background:#1a1a2e;border-radius:4px;overflow:hidden">
          <div style="width:${width}%;height:100%;background:${color};border-radius:4px;display:flex;align-items:center;padding-left:8px;font-size:0.75rem;color:#fff">
            ${value}${rule.metric === 'uptime_days' ? '天' : rule.metric === 'network_latency' ? 'ms' : '%'}
          </div>
        </div>
        <span style="width:40px;text-align:right;font-size:0.75rem;color:${color}">${ratio.toFixed(2)}</span>
      </div>`;
  }).join('');
  return bars;
}

// 渲染爻位热力图
function renderHeatmap(metrics) {
  const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
  const heatmapEl = document.getElementById('heatmap');
  heatmapEl.innerHTML = '';
  for (const yao of yaoNames) {
    const rule = config.mapping[yao];
    const value = metrics[rule.metric];
    const ratio = value / rule.threshold;
    // 渐变色：绿(0) → 黄(0.8) → 红(1.2+)
    const r = ratio > 1.0 ? 255 : Math.round(ratio * 255);
    const g = ratio < 1.0 ? 255 : Math.round((1.2 - ratio) / 0.2 * 255);
    const b = 50;
    const alpha = Math.min(0.4 + ratio * 0.5, 1.0);
    const cell = document.createElement('div');
    cell.style.cssText = `flex:1;background:rgba(${r},${Math.max(g,0)},${b},${alpha});display:flex;align-items:center;justify-content:center;font-size:0.7rem;color:#fff;border-radius:4px`;
    cell.textContent = ratio.toFixed(2);
    heatmapEl.appendChild(cell);
  }
}

// 渲染趋势图（简化版 Canvas）
function renderTrend(history) {
  const canvas = document.getElementById('trendChart');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (history.length < 2) {
    ctx.fillStyle = '#666';
    ctx.fillText('需要至少2条数据才能显示趋势', 20, 100);
    return;
  }

  const recent = history.slice(-20);
  const bins = recent.map(h => parseInt(h.bin, 2));
  const maxVal = 63;
  const w = canvas.width;
  const h = canvas.height;
  const stepX = w / (recent.length - 1);

  ctx.strokeStyle = '#00ff88';
  ctx.lineWidth = 2;
  ctx.beginPath();
  bins.forEach((val, i) => {
    const x = i * stepX;
    const y = h - (val / maxVal) * h * 0.8 - h * 0.1;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // 标注关键点
  ctx.fillStyle = '#fff';
  bins.forEach((val, i) => {
    if (i % Math.max(1, Math.floor(recent.length / 5)) === 0) {
      const x = i * stepX;
      const y = h - (val / maxVal) * h * 0.8 - h * 0.1;
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillText(recent[i].name, x - 15, y - 8);
    }
  });
}

// 主计算函数
async function calcHealth() {
  const metrics = {
    cpu_usage: parseInt(document.getElementById('cpu').value),
    mem_usage: parseInt(document.getElementById('mem').value),
    disk_io: parseInt(document.getElementById('disk').value),
    network_latency: parseInt(document.getElementById('net').value),
    error_rate: parseInt(document.getElementById('err').value),
    uptime_days: parseInt(document.getElementById('uptime').value),
  };

  // 计算本卦
  const bin = metricsToBin(metrics);
  const interBin = calcInterHex(bin);
  const idx = parseInt(bin, 2);
  const hexData = engine.db[idx];
  const interIdx = parseInt(interBin, 2);
  const interData = engine.db[interIdx];

  // 渲染
  document.getElementById('hexOutput').innerHTML =
    `<span style="color:#00ff88;font-size:1.5rem">${hexData?.name ?? '未知'}</span>
     <span style="color:#888;margin-left:8px">${bin}</span>
     <span style="color:#aaa;margin-left:8px">${hexData?.english ?? ''}</span>`;

  document.getElementById('interHexOutput').innerHTML =
    `互卦：<span style="color:#ffaa00">${interData?.name ?? '未知'}</span>
     <span style="color:#888;margin-left:8px">${interBin}</span>`;

  document.getElementById('yaoWeights').innerHTML = renderWeights(metrics);
  renderHeatmap(metrics);

  // 告警检查
  const alertEl = document.getElementById('alertMsg');
  const alerts = [];
  if (interData?.name === config.alert.inter_hex_threshold) {
    alerts.push('互卦触发告警阈值');
  }
  const yaoNames = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
  for (const yao of yaoNames) {
    const rule = config.mapping[yao];
    if (metrics[rule.metric] / rule.threshold > config.alert.yao_weight_threshold) {
      alerts.push(`${yao}(${rule.metric}) 超载`);
    }
  }
  alertEl.innerHTML = alerts.length > 0
    ? alerts.map(a => `<div style="color:#ff4444;padding:4px 0">⚠️ ${a}</div>`).join('')
    : '<div style="color:#00ff88">系统状态正常</div>';

  // 记录历史
  history.push({ bin, name: hexData?.name, inter: interData?.name, metrics, timestamp: Date.now() });
  renderTrend(history);
}

// 初始化
await loadConfig();
document.getElementById('calcBtn').addEventListener('click', calcHealth);

// 自动计算一次
calcHealth();
