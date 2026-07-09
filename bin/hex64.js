#!/usr/bin/env node

import { Hex64Engine } from '../src/core.js';
import { HEXAGRAMS, TAG_TO_OP } from '../src/database.js';
import { compileHex } from '../src/compiler.js';
import { opTemplates } from '../src/templates.js';

const B = s => `\x1b[1m${s}\x1b[22m`;
const D = s => `\x1b[2m${s}\x1b[22m`;
const CYAN = s => `\x1b[36m${s}\x1b[39m`;
const GREEN = s => `\x1b[32m${s}\x1b[39m`;
const YELLOW = s => `\x1b[33m${s}\x1b[39m`;
const MAGENTA = s => `\x1b[35m${s}\x1b[39m`;
const RED = s => `\x1b[31m${s}\x1b[39m`;
const BLUE = s => `\x1b[34m${s}\x1b[39m`;
const DIM = s => `\x1b[2m${s}\x1b[22m`;
const GRAY = s => `\x1b[90m${s}\x1b[39m`;
const RESET = '\x1b[0m';

const LOGO = `
${CYAN}┌─────────────────────────────────────┐${RESET}
${CYAN}│${RESET}  ${GREEN}乾☰${RESET}  ${GREEN}兑☱${RESET}  ${GREEN}离☲${RESET}  ${GREEN}震☳${RESET}  ${GREEN}巽☴${RESET}  ${GREEN}坎☵${RESET}  ${GREEN}艮☶${RESET}  ${GRAY}坤☷${RESET}  ${CYAN}│${RESET}
${CYAN}│${RESET}  ${GREEN}███${RESET} ${GREEN}██░${RESET} ${GREEN}█░█${RESET} ${GREEN}█░░${RESET} ${GRAY}░█░${RESET} ${GRAY}░░█${RESET} ${GRAY}░░█${RESET} ${GRAY}░░░${RESET}  ${CYAN}│${RESET}
${CYAN}│${RESET}  ${GREEN}███${RESET} ${GREEN}██░${RESET} ${GRAY}░░█${RESET} ${GREEN}███${RESET} ${GRAY}░░█${RESET} ${GREEN}███${RESET} ${GRAY}░░█${RESET} ${GRAY}░░░${RESET}  ${CYAN}│${RESET}
${CYAN}│${RESET}  ${GREEN}███${RESET} ${GRAY}░░█${RESET} ${GREEN}█░█${RESET} ${GREEN}███${RESET} ${GRAY}░█░${RESET} ${GRAY}░░█${RESET} ${GREEN}███${RESET} ${GRAY}░░░${RESET}  ${CYAN}│${RESET}
${CYAN}│${RESET}  ${YELLOW}111${RESET} ${YELLOW}110${RESET} ${YELLOW}101${RESET} ${YELLOW}100${RESET} ${YELLOW}011${RESET} ${YELLOW}010${RESET} ${YELLOW}001${RESET} ${YELLOW}000${RESET}  ${CYAN}│${RESET}
${CYAN}└─────────────────────────────────────┘${RESET}
${YELLOW}        Hex64 Engine v1.0${RESET}
${DIM}  八经卦 · 先天卦序 · 莱布尼茨二进制${RESET}
`;








function formatOutput(input, r, compiled, jsonMode) {
  if (jsonMode) {
    return JSON.stringify({ input, ...r.hexCode, featureVec: r.featureVec, pseudoCode: r.pseudoCode, controlSignal: r.controlSignal, compiledJS: compiled.js, compiledPY: compiled.py, compiledRS: compiled.rs, compiledGO: compiled.go }, null, 2);
  }
  const hc = r.hexCode;
  const sep = D('\u2500'.repeat(50));
  let out = '';
  out += `\n${B(' \u250C\u2500\u2500 Hex64 Engine')} ${D('\u2500'.repeat(35))}\n`;
  out += ` ${B('\u2502')} ${CYAN('Input:')} ${B(hc.name)} ${D(`(${input})`)}\n`;
  out += ` ${B('\u2502')} ${CYAN('Hexagram:')} ${YELLOW(hc.bin)} ${B(`\u2022 ${hc.name}`)} ${D(`(${hc.pinyin})`)}\n`;
  out += ` ${B('\u2502')} ${D(hc.en)}\n`;
  out += ` ${B('\u2502')} ${CYAN('Index:')} ${hc.index}  ${CYAN('Weight:')} ${hc.weight}  ${CYAN('Category:')} ${hc.category}\n`;
  out += ` ${B('\u2514')}${D('\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')}\n`;
  out += ` ${CYAN('Feature:')} [${r.featureVec.map(v => v ? GREEN(v) : D(v)).join(', ')}]\n`;
  out += ` ${CYAN('GPIO:')}    ${r.controlSignal.map(s => s === 'ON' ? GREEN(B('ON')) : RED('OFF')).join(' | ')}\n`;
  out += ` ${CYAN('Tags:')}    ${hc.tags.join(', ')}\n`;
  out += `\n ${MAGENTA('HexLang:')} ${r.pseudoCode}\n`;
  out += `\n ${BLUE('JavaScript:')}\n${compiled.js.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  out += `\n ${BLUE('Python:')}\n${compiled.py.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  out += `\n ${RED('Rust:')}\n${compiled.rs.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  out += `\n ${CYAN('Go:')}\n${compiled.go.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  return out;
}

function formatOpOutput(opResult, jsonMode) {
  if (jsonMode) {
    return JSON.stringify(opResult, null, 2);
  }
  const i = opResult.input;
  const r = opResult.result;
  const sep = D('\u2500'.repeat(50));
  let out = '';
  out += `\n${B(' \u250C\u2500\u2500 Hex64 Operation')} ${D('\u2500'.repeat(32))}\n`;
  out += ` ${B('\u2502')} ${CYAN('Op:')} ${B(opResult.op)}  ${D('- ')}\n`;
  out += ` ${B('\u2502')} ${CYAN('Input:')} ${YELLOW(i.bin)} ${B(i.name)} ${D(`(${i.en})`)}\n`;
  out += ` ${B('\u2502')} ${CYAN('Result:')} ${YELLOW(opResult.resultBin)} ${B(r.name)} ${D(`(${r.en})`)}\n`;
  if (r.bin) {
    const compiled = compileHex(r);
    out += ` ${B('\u2514')}${D('\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')}\n`;
    out += ` ${BLUE('JavaScript:')}\n${compiled.js.split('\n').map(l => `   ${l}`).join('\n')}\n`;
    out += `\n ${BLUE('Python:')}\n${compiled.py.split('\n').map(l => `   ${l}`).join('\n')}\n`;
    out += `\n ${RED('Rust:')}\n${compiled.rs.split('\n').map(l => `   ${l}`).join('\n')}\n`;
    out += `\n ${CYAN('Go:')}\n${compiled.go.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  }
  return out;
}

function processInput(engine, input, opFlag, jsonMode) {
  if (opFlag) {
    const opResult = engine.operate(opFlag, input);
    return formatOpOutput(opResult, jsonMode);
  }
  const r = engine.tranceive(input);
  const compiled = compileHex(r.hexCode);
  return formatOutput(input, r, compiled, jsonMode);
}

function processOpInput(engine, op, input, secondInput, jsonMode) {
  const opResult = engine.operate(op, input, secondInput);
  if (jsonMode) return JSON.stringify(opResult, null, 2);
  return formatOpOutput(opResult, jsonMode);
}

function usage() {
  console.log(`Usage:
  node bin/hex64.js <text>...
  echo <text> | node bin/hex64.js
  node bin/hex64.js --op <cuo|zong|bian|AND|OR|XOR> <text> [secondText]
  node bin/hex64.js --json <text>...
Options:
  --op <op>   Hexagram operation: cuo, zong, bian, AND, OR, XOR
  --json      JSON output (machine-readable)
  --help      Show this help`);
}

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  usage();
  process.exit(0);
}

let opFlag = null;
let jsonMode = false;
let positional = [];

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--op') {
    opFlag = args[++i];
  } else if (args[i] === '--json') {
    jsonMode = true;
  } else if (args[i] === '--help' || args[i] === '-h') {
    usage();
    process.exit(0);
  } else {
    positional.push(args[i]);
  }
}

const engine = new Hex64Engine();

console.log(LOGO);

if (positional.length > 0) {
  if (opFlag && (opFlag === 'AND' || opFlag === 'OR' || opFlag === 'XOR')) {
    const primary = positional[0];
    const secondary = positional[1];
    const output = processOpInput(engine, opFlag, primary, secondary, jsonMode);
    console.log(output);
  } else if (opFlag && opFlag === 'bian') {
    const primary = positional[0];
    const secondary = positional[1];
    const output = processOpInput(engine, opFlag, primary, secondary, jsonMode);
    console.log(output);
  } else {
    for (const input of positional) {
      if (opFlag) {
        const output = processInput(engine, input, opFlag, jsonMode);
        console.log(output);
      } else {
        const r = engine.tranceive(input);
        const compiled = compileHex(r.hexCode);
        console.log(formatOutput(input, r, compiled, jsonMode));
      }
    }
  }
} else if (!process.stdin.isTTY) {
  let buffer = '';
  process.stdin.setEncoding('utf-8');
  process.stdin.on('data', chunk => { buffer += chunk; });
  process.stdin.on('end', () => {
    const lines = buffer.split('\n').filter(l => l.trim());
    for (const line of lines) {
      const input = line.trim();
      if (!input) continue;
      if (opFlag && (opFlag === 'AND' || opFlag === 'OR' || opFlag === 'XOR')) {
        const parts = input.split(/\s+/);
        const primary = parts[0];
        const secondary = parts[1];
        console.log(processOpInput(engine, opFlag, primary, secondary, jsonMode));
      } else {
        console.log(processInput(engine, input, opFlag, jsonMode));
      }
    }
  });
} else {
  usage();
}
