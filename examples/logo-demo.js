/**
 * CLI 启动画面示例
 * 
 * 演示如何在 Node.js CLI 工具中显示八经卦 ASCII 艺术
 * 运行: node examples/logo-demo.js
 */

import { HEXAGRAMS } from '../src/database.js';

// ============================================
// 版本1：标准八经卦阵列（黑白ASCII）
// ============================================
console.log('');
console.log('┌─────────────────────────────────────┐');
console.log('│  乾☰   兑☱   离☲   震☳   巽☴   坎☵   艮☶   坤☷  │');
console.log('│  ███   ██░   █░█   █░░   ░█░   ░░█   ░░█   ░░░  │');
console.log('│  ███   ██░   ░█░   ███   ░░█   ███   ░░█   ░░░  │');
console.log('│  ███   ░░█   █░█   ███   ░█░   ░░█   ███   ░░░  │');
console.log('│  111   110   101   100   011   010   001   000  │');
console.log('│  7     6     5     4     3     2     1     0    │');
console.log('└─────────────────────────────────────┘');
console.log('        Hex64 · 八经卦二进制映射表');
console.log('「3位二进制=1卦=1个八进制位 · 8卦=24位=3字节」');
console.log('');

// ============================================
// 版本2：环形八卦（文本方位布局）
// ============================================
console.log('┌── Hex64 Engine v1.0 ──────────────────┐');
console.log('│                                       │');
console.log('│          ╔═══╗                         │');
console.log('│          ║乾☰║ 111 (南)                │');
console.log('│      ╔═══╝   ╚═══╗                    │');
console.log('│      ║兑☱║       ║离☲║ 110 → 101       │');
console.log('│      ╚═══╝       ╚═══╗                │');
console.log('│  100 ← 震☳            ║巽☴║ 011        │');
console.log('│  ╔═══╗               ╚═══╝            │');
console.log('│  ║坎☵║        ╔═══╗                    │');
console.log('│  ╚═══╝        ║艮☶║ 010 → 001         │');
console.log('│      ╔═══╗     ╚═══╝                  │');
console.log('│      ║坤☷║ 000 (北)                    │');
console.log('│      ╚═══╝                         │');
console.log('│        Hex64 Engine                   │');
console.log('└───────────────────────────────────────┘');
console.log('');

// ============================================
// 版本3：单行紧凑版（适合 commit 前缀）
// ============================================
console.log('// Commit 前缀示例:');
console.log('[☰☱☲☳☴☵☶☷] feat: 添加八经卦 ASCII 艺术');
console.log('[☲] docs: 更新离卦可视化文档');
console.log('[☳] chore: 触发构建流程');
console.log('');

// ============================================
// 版本4：二进制速查表
// ============================================
console.log('八经卦二进制速查表（Hex64 核心映射）');
console.log('┌─────┬────┬──────┬──────────────────────┐');
console.log('│ 卦  │ 爻 │ 二进制 │ HexLang 语义标签      │');
console.log('├─────┼────┼──────┼──────────────────────┤');

// 从数据库获取八个经卦的数据
const baseTrigrams = [
  { name: '乾☰', bin: '111', op: '初始化、核心、调度' },
  { name: '兑☱', bin: '110', op: '订阅、监听、代理' },
  { name: '离☲', bin: '101', op: '可视化、展示、交付' },
  { name: '震☳', bin: '100', op: '启动、触发、重构' },
  { name: '巽☴', bin: '011', op: '探索、查询、同步' },
  { name: '坎☵', bin: '010', op: '存储、缓存、容错' },
  { name: '艮☶', bin: '001', op: '暂停、等待、限流' },
  { name: '坤☷', bin: '000', op: '终止、复位、归档' },
];

baseTrigrams.forEach(t => {
  const padding = ' '.repeat(22 - t.op.length);
  console.log(`│ ${t.name.padEnd(3)} │ ${t.bin}  │ ${padding}│ ${t.op} │`);
});

console.log('└─────┴────┴──────┴──────────────────────┘');
console.log('');

// ============================================
// 版本5：特征向量可视化
// ============================================
console.log('特征向量可视化示例:');
console.log('');

const sampleInputs = ['alpha', 'beta', 'gamma', 'delta', 'Hex64'];
const engine = {
  tranceive: (input) => {
    let h = 5381;
    for (let i = 0; i < input.length; i++) {
      h = (h << 5) + h + input.charCodeAt(i);
    }
    const idx = h % 64;
    const hex = HEXAGRAMS[idx];
    return {
      hexCode: hex,
      featureVec: hex.bin.split('').map(Number)
    };
  }
};

sampleInputs.forEach(text => {
  const r = engine.tranceive(text);
  const vecStr = r.featureVec.map(v => v ? '█' : '░').join('');
  console.log(`  ${text.padEnd(8)} [${r.hexCode.bin}] ${vecStr} ${r.hexCode.name}`);
});

console.log('');
console.log('  图例: █=阳爻(1)  ░=阴爻(0)');
console.log('');
