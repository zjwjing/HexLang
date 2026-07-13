import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { TaiXuanEncoder } from './taixuan.js';

describe('TaiXuanEncoder', () => {
  const tx = new TaiXuanEncoder();

  describe('encodeShou()', () => {
    it('returns deterministic results for same input', () => {
      const a = tx.encodeShou('hello');
      const b = tx.encodeShou('hello');
      assert.equal(a.shouIdx, b.shouIdx);
      assert.equal(a.ternaryStr, b.ternaryStr);
    });

    it('shouIdx is in [0, 80]', () => {
      const r = tx.encodeShou('test');
      assert.ok(r.shouIdx >= 0 && r.shouIdx < 81);
    });

    it('ternaryStr is 4 digits of 0-2', () => {
      const r = tx.encodeShou('test');
      assert.equal(r.ternaryStr.length, 4);
      assert.ok(/^[012]{4}$/.test(r.ternaryStr));
    });

    it('vector has 4 normalized values', () => {
      const r = tx.encodeShou('test');
      assert.equal(r.vector.length, 4);
      r.vector.forEach(v => assert.ok(v >= 0 && v <= 1));
    });

    it('states are valid ternary state names', () => {
      const r = tx.encodeShou('test');
      assert.equal(r.states.length, 4);
      r.states.forEach(s => assert.ok(['yang', 'yin', 'cou'].includes(s)));
    });
  });

  describe('encodeZan()', () => {
    it('zanIdx is in [0, 728]', () => {
      const r = tx.encodeZan('test');
      assert.ok(r.zanIdx >= 0 && r.zanIdx < 729);
    });

    it('ternaryStr is 6 digits of 0-2', () => {
      const r = tx.encodeZan('test');
      assert.equal(r.ternaryStr.length, 6);
      assert.ok(/^[012]{6}$/.test(r.ternaryStr));
    });

    it('vector has 6 normalized values', () => {
      const r = tx.encodeZan('test');
      assert.equal(r.vector.length, 6);
    });
  });
});
