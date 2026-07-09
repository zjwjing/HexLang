import { TAG_TO_OP } from './database.js';
import { opTemplates } from './templates.js';

const comments = { js: '//', py: '#', rs: '//', go: '//' };

/**
 * Compile hexagram tags into code snippets for all 4 languages.
 * @param {object} hex - hexagram object with { name, tags, bin }
 * @returns {{ name: string, js: string, py: string, rs: string, go: string }}
 */
export function compileHex(hex) {
  const ops = [...new Set(hex.tags.map(t => TAG_TO_OP[t] || t.toUpperCase()))];
  const param = hex.name || 'system';
  const langs = ['js', 'py', 'rs', 'go'];
  const result = { name: hex.name };
  for (const lang of langs) {
    const lines = ops.map(op => {
      const tpl = opTemplates[op];
      if (!tpl || !tpl[lang]) {
        return lang === 'js' ? `${op.toLowerCase()}('${param}');` : `${op.toLowerCase()}('${param}')`;
      }
      let code = tpl[lang].replace(/%s/g, param).replace(/%d/g, '60').replace(/%f/g, '1.5');
      return code;
    });
    result[lang] = `${comments[lang]} HexLang → ${lang.toUpperCase()}  ·  ${hex.name}  (${hex.bin})\n${lines.map(l => '  ' + l).join('\n')}`;
  }
  return result;
}
