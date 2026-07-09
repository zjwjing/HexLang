import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { Hex64Engine } from './core.js';

describe('Hex64Engine', () => {
  const engine = new Hex64Engine();

  describe('lookup()', () => {
    it('returns deterministic results for same input', () => {
      const a = engine.lookup('hello');
      const b = engine.lookup('hello');
      assert.equal(a.index, b.index);
      assert.equal(a.bin, b.bin);
    });

    it('returns different hexagrams for different inputs', () => {
      const a = engine.lookup('hello');
      const b = engine.lookup('world');
      assert.notEqual(a.index, b.index);
    });

    it('returns a valid hexagram object', () => {
      const r = engine.lookup('test');
      assert.ok(r.index >= 0 && r.index < 64);
      assert.equal(r.bin.length, 6);
      assert.ok(/^[01]{6}$/.test(r.bin));
      assert.ok(typeof r.name === 'string');
      assert.ok(r.name.length > 0);
      assert.ok(Array.isArray(r.tags));
      assert.equal(r.tags.length, 6);
    });

    it('handles empty string', () => {
      const r = engine.lookup('');
      assert.ok(r.index >= 0 && r.index < 64);
    });

    it('handles non-string input', () => {
      const r = engine.lookup(123);
      assert.ok(r.index >= 0 && r.index < 64);
    });
  });

  describe('tranceive()', () => {
    it('returns all expected fields', () => {
      const r = engine.tranceive('hello');
      assert.ok(r.input);
      assert.ok(r.hexCode);
      assert.ok(r.featureVec);
      assert.ok(r.pseudoCode);
      assert.ok(r.controlSignal);
    });

    it('featureVec is an array of 6 bits', () => {
      const r = engine.tranceive('hello');
      assert.equal(r.featureVec.length, 6);
      r.featureVec.forEach(b => assert.ok(b === 0 || b === 1));
    });

    it('controlSignal matches featureVec', () => {
      const r = engine.tranceive('hello');
      r.featureVec.forEach((b, i) => {
        assert.equal(r.controlSignal[i], b ? 'ON' : 'OFF');
      });
    });

    it('pseudoCode contains the hexagram name', () => {
      const r = engine.tranceive('hello');
      assert.ok(r.pseudoCode.includes(r.hexCode.name));
    });
  });

  describe('operate()', () => {
    it('cuo flips all bits', () => {
      const r = engine.operate('cuo', 'hello');
      const bits = engine.lookup('hello').bin;
      const expected = bits.split('').map(b => b === '0' ? '1' : '0').join('');
      assert.equal(r.resultBin, expected);
    });

    it('zong reverses bit order', () => {
      const r = engine.operate('zong', 'hello');
      const bits = engine.lookup('hello').bin;
      const expected = bits.split('').reverse().join('');
      assert.equal(r.resultBin, expected);
    });

    it('bian with single input flips all bits', () => {
      const r = engine.operate('bian', 'hello');
      const bits = engine.lookup('hello').bin;
      const expected = bits.split('').map(b => b === '0' ? '1' : '0').join('');
      assert.equal(r.resultBin, expected);
    });

    it('bian with secondInput XORs', () => {
      const r = engine.operate('bian', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b ^ w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('AND works correctly', () => {
      const r = engine.operate('AND', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b & w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('AND throws without secondInput', () => {
      assert.throws(() => engine.operate('AND', 'hello'), /needs secondInput/);
    });

    it('OR works correctly', () => {
      const r = engine.operate('OR', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b | w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('OR throws without secondInput', () => {
      assert.throws(() => engine.operate('OR', 'hello'), /needs secondInput/);
    });

    it('XOR works correctly', () => {
      const r = engine.operate('XOR', 'hello', 'world');
      const h = engine.lookup('hello').bin;
      const w = engine.lookup('world').bin;
      const expected = h.split('').map((b, i) => b ^ w[i]).join('');
      assert.equal(r.resultBin, expected);
    });

    it('XOR throws without secondInput', () => {
      assert.throws(() => engine.operate('XOR', 'hello'), /needs secondInput/);
    });

    it('unknown op throws', () => {
      assert.throws(() => engine.operate('INVALID', 'hello'), /Unknown op/);
    });
  });

  describe('controlSignal()', () => {
    it('returns array of 6 ON/OFF strings', () => {
      const sig = engine.controlSignal('hello');
      assert.equal(sig.length, 6);
      sig.forEach(s => assert.ok(s === 'ON' || s === 'OFF'));
    });
  });

  describe('hash distribution', () => {
    it('distributes 1000 inputs across all 64 hexagrams', () => {
      const counts = new Array(64).fill(0);
      for (let i = 0; i < 1000; i++) {
        const r = engine.lookup(`input_${i}`);
        counts[r.index]++;
      }
      const empty = counts.filter(c => c === 0).length;
      assert.ok(empty <= 5, `${empty} hexagrams have zero hits — distribution may be skewed`);
    });
  });

  describe('featureVector()', () => {
    it('returns array of 6 numbers (0 or 1)', () => {
      const vec = engine.featureVector('hello');
      assert.equal(vec.length, 6);
      vec.forEach(v => assert.ok(v === 0 || v === 1));
    });

    it('matches the binary representation of the hexagram', () => {
      const hex = engine.lookup('test');
      const vec = engine.featureVector('test');
      const expected = hex.bin.split('').map(Number);
      assert.deepEqual(vec, expected);
    });
  });

  describe('encodeSeeded()', () => {
    it('returns deterministic results for same key', () => {
      const a = engine.encodeSeeded('session-abc');
      const b = engine.encodeSeeded('session-abc');
      assert.equal(a.name, b.name);
      assert.equal(a.bin, b.bin);
      assert.equal(a.index, b.index);
    });

    it('returns different results for different keys', () => {
      const a = engine.encodeSeeded('key-1');
      const b = engine.encodeSeeded('key-2');
      assert.notEqual(a.bin, b.bin);
    });

    it('returns all expected fields', () => {
      const r = engine.encodeSeeded('test-key');
      assert.ok(r.index >= 0 && r.index < 64);
      assert.equal(r.bin.length, 6);
      assert.ok(typeof r.name === 'string');
      assert.ok(typeof r.hexFont === 'string');
      assert.ok(typeof r.english === 'string');
      assert.ok(Array.isArray(r.tags));
      assert.ok(Array.isArray(r.yaoWeights));
      assert.equal(r.yaoWeights.length, 6);
    });
  });
});
