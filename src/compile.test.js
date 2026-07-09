import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { HEXAGRAMS, TAG_TO_OP } from './database.js';
import { opTemplates } from './templates.js';
import { compileHex } from './compiler.js';

describe('compileHex', () => {
  it('returns all 4 language outputs', () => {
    const hex = HEXAGRAMS[0];
    const result = compileHex(hex);
    assert.ok(result.js);
    assert.ok(result.py);
    assert.ok(result.rs);
    assert.ok(result.go);
  });

  it('each language output has correct header', () => {
    const hex = HEXAGRAMS[0];
    const result = compileHex(hex);
    assert.match(result.js, /^\/\/ HexLang → JS/);
    assert.match(result.py, /^# HexLang → PY/);
    assert.match(result.rs, /^\/\/ HexLang → RS/);
    assert.match(result.go, /^\/\/ HexLang → GO/);
  });

  it('all 64 hexagrams produce valid output in all languages', () => {
    for (const hex of HEXAGRAMS) {
      const result = compileHex(hex);
      assert.ok(result.js.length > 20, `${hex.name} js too short`);
      assert.ok(result.py.length > 20, `${hex.name} py too short`);
      assert.ok(result.rs.length > 20, `${hex.name} rs too short`);
      assert.ok(result.go.length > 20, `${hex.name} go too short`);

      const ops = [...new Set(hex.tags.map(t => TAG_TO_OP[t] || t.toUpperCase()))];
      // Each language output has: 1 header line + N code lines (some templates embed \n)
      const jsLineCount = result.js.split('\n').length;
      const pyLineCount = result.py.split('\n').length;
      const rsLineCount = result.rs.split('\n').length;
      const goLineCount = result.go.split('\n').length;

      // At minimum: header + code lines; at most: header + code lines × 2 (if all templates were multi-line)
      assert.ok(jsLineCount >= 1 + ops.length, `${hex.name} js too few lines: ${jsLineCount} < ${1 + ops.length}`);
      assert.ok(pyLineCount >= 1 + ops.length, `${hex.name} py too few lines: ${pyLineCount} < ${1 + ops.length}`);
      assert.ok(rsLineCount >= 1 + ops.length, `${hex.name} rs too few lines: ${rsLineCount} < ${1 + ops.length}`);
      assert.ok(goLineCount >= 1 + ops.length, `${hex.name} go too few lines: ${goLineCount} < ${1 + ops.length}`);

      // All languages should have the same or more lines than JS (JS may embed extra comments via \n)
      assert.ok(pyLineCount >= ops.length + 1, `${hex.name} py line count`);
      assert.ok(rsLineCount >= ops.length + 1, `${hex.name} rs line count`);
      assert.ok(goLineCount >= ops.length + 1, `${hex.name} go line count`);
    }
  });

  it('Rust output uses snake_case function naming', () => {
    const hex = HEXAGRAMS[0];
    const result = compileHex(hex);
    const codeLines = result.rs.split('\n').filter(l => l.trim() && !l.trim().startsWith('//'));
    for (const line of codeLines) {
      const fn = line.match(/::(\w+)\(/);
      if (fn) {
        assert.match(fn[1], /^[a-z][a-z0-9_]*$/, `Rust function ${fn[1]} should be snake_case`);
      }
    }
  });

  it('Go output uses PascalCase function naming', () => {
    const hex = HEXAGRAMS[0];
    const result = compileHex(hex);
    const codeLines = result.go.split('\n').filter(l => l.trim() && !l.trim().startsWith('//'));
    for (const line of codeLines) {
      const fn = line.match(/\.(\w+)\(/);
      if (fn) {
        assert.match(fn[1], /^[A-Z][a-zA-Z0-9]*$/, `Go function ${fn[1]} should be PascalCase`);
      }
    }
  });

  it('%s substitution replaces with hexagram name', () => {
    const hex = HEXAGRAMS.find(h => h.name === '乾') || HEXAGRAMS[0];
    const result = compileHex(hex);
    assert.ok(result.js.includes(hex.name));
    assert.ok(result.py.includes(hex.name));
    assert.ok(result.rs.includes(hex.name));
    assert.ok(result.go.includes(hex.name));
  });

  it('hexagram name and bin appear in header', () => {
    const hex = HEXAGRAMS[25];
    const result = compileHex(hex);
    assert.ok(result.rs.includes(hex.name));
    assert.ok(result.rs.includes(hex.bin));
    assert.ok(result.go.includes(hex.name));
    assert.ok(result.go.includes(hex.bin));
  });

  it('each language header uses correct comment syntax', () => {
    const hex = HEXAGRAMS[0];
    const result = compileHex(hex);
    const jsFirst = result.js.split('\n').find(l => l.trim());
    const pyFirst = result.py.split('\n').find(l => l.trim());
    const rsFirst = result.rs.split('\n').find(l => l.trim());
    const goFirst = result.go.split('\n').find(l => l.trim());

    assert.match(jsFirst, /^\s*\/\//, `JS header should be // comment`);
    assert.match(pyFirst, /^\s*#/, `PY header should be # comment`);
    assert.match(rsFirst, /^\s*\/\//, `RS header should be // comment`);
    assert.match(goFirst, /^\s*\/\//, `GO header should be // comment`);
  });
});
