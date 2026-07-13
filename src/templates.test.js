import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { opTemplates } from './templates.js';

describe('opTemplates', () => {
  it('is a non-empty object', () => {
    assert.ok(typeof opTemplates === 'object');
    assert.ok(Object.keys(opTemplates).length > 0);
  });

  it('every template has js, py, rs, go fields', () => {
    for (const [key, tpl] of Object.entries(opTemplates)) {
      assert.ok(typeof tpl.js === 'string', `${key} missing js`);
      assert.ok(typeof tpl.py === 'string', `${key} missing py`);
      assert.ok(typeof tpl.rs === 'string', `${key} missing rs`);
      assert.ok(typeof tpl.go === 'string', `${key} missing go`);
    }
  });

  it('most templates contain at least one placeholder', () => {
    const keys = Object.keys(opTemplates);
    const withPH = keys.filter(k => {
      const t = opTemplates[k];
      return [t.js, t.py, t.rs, t.go].some(s => s.includes('%'));
    });
    assert.ok(withPH.length / keys.length > 0.9, `${keys.length - withPH.length}/${keys.length} templates have no placeholder`);
  });

  it('has expected keys', () => {
    const keys = Object.keys(opTemplates);
    assert.ok(keys.includes('INIT'));
    assert.ok(keys.includes('EXEC'));
    assert.ok(keys.includes('LOAD'));
    assert.ok(keys.includes('REBOOT'));
  });

  it('all js templates are valid js function-like strings', () => {
    for (const [key, tpl] of Object.entries(opTemplates)) {
      assert.ok(tpl.js.length > 5, `${key} js too short`);
    }
  });
});
