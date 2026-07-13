import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { YuanHuiEncoder } from './yuanhui.js';

describe('YuanHuiEncoder', () => {
  const yh = new YuanHuiEncoder();

  describe('encode()', () => {
    it('returns deterministic results for same timestamp', () => {
      const a = yh.encode(1000000);
      const b = yh.encode(1000000);
      assert.equal(a.yuan, b.yuan);
      assert.equal(a.hui, b.hui);
      assert.equal(a.yun, b.yun);
      assert.equal(a.shi, b.shi);
    });

    it('yuan is in [0, 11]', () => {
      const r = yh.encode(1000000);
      assert.ok(r.yuan >= 0 && r.yuan < 12);
    });

    it('hui is in [0, 29]', () => {
      const r = yh.encode(1000000);
      assert.ok(r.hui >= 0 && r.hui < 30);
    });

    it('yun is in [0, 11]', () => {
      const r = yh.encode(1000000);
      assert.ok(r.yun >= 0 && r.yun < 12);
    });

    it('shi is in [0, 29]', () => {
      const r = yh.encode(1000000);
      assert.ok(r.shi >= 0 && r.shi < 30);
    });

    it('vector has 4 normalized values', () => {
      const r = yh.encode(1000000);
      assert.equal(r.vector.length, 4);
      r.vector.forEach(v => assert.ok(v >= 0 && v <= 1));
    });

    it('different timestamps produce different results', () => {
      const a = yh.encode(0);
      const b = yh.encode(999999999);
      const allSame = a.yuan === b.yuan && a.hui === b.hui && a.yun === b.yun && a.shi === b.shi;
      assert.ok(!allSame);
    });

    it('defaults to current time when no arg', () => {
      const r = yh.encode();
      assert.ok(typeof r.timestamp === 'number');
      assert.ok(r.timestamp > 0);
    });
  });
});
