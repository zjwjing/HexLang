/**
 * Hex64 AI 集成模块测试
 * 
 * 测试 Hex64AITool 和 quickEncode 功能
 * 
 * 运行方式：
 *   node src/ai-integration.test.js
 */

import { strict as assert } from 'node:assert';
import { describe, it } from 'node:test';
import { Hex64AITool, createHex64Assistant, hex64QuickEncode } from './ai-integration.js';

describe('Hex64AITool', () => {
  it('应该返回正确的工具 Schema', (t) => {
    const tool = new Hex64AITool();
    const schema = tool.getSchema();
    
    assert.equal(schema.type, 'function');
    assert.equal(schema.function.name, 'hex64_encode');
    assert.ok(schema.function.description.length > 0);
    assert.ok(schema.function.parameters.required.includes('input'));
  });

  it('应该正确编码输入字符串', (t) => {
    const tool = new Hex64AITool();
    const result = tool.execute({ input: 'test' });
    
    assert.equal(result.success, true);
    assert.ok(result.hexagram.name);
    assert.ok(result.hexagram.binary);
    assert.ok(Array.isArray(result.hexagram.tags));
    assert.ok(Array.isArray(result.features.vector));
    assert.equal(result.features.vector.length, 6);
  });

  it('应该拒绝空输入', (t) => {
    const tool = new Hex64AITool();
    const result = tool.execute({ input: '' });
    
    assert.equal(result.success, false);
    assert.ok(result.error);
  });

  it('应该拒绝非字符串输入', (t) => {
    const tool = new Hex64AITool();
    const result = tool.execute({ input: 123 });
    
    assert.equal(result.success, false);
  });

  it('应该包含特征向量和 GPIO 信号', (t) => {
    const tool = new Hex64AITool();
    const result = tool.execute({ input: 'hello', include_features: true });
    
    assert.ok(result.features);
    assert.ok(result.features.vector);
    assert.ok(result.features.controlSignal);
    assert.ok(result.features.interpretation);
  });

  it('应该支持关闭特征输出', (t) => {
    const tool = new Hex64AITool();
    const result = tool.execute({ input: 'hello', include_features: false });
    
    assert.ok(!result.features);
  });
});

describe('createHex64Assistant', () => {
  it('应该返回包含 getTools 方法的对象', (t) => {
    const assistant = createHex64Assistant();
    
    assert.ok(typeof assistant.getTools === 'function');
    assert.ok(Array.isArray(assistant.getTools()));
  });

  it('应该返回包含 executeTool 方法的对象', (t) => {
    const assistant = createHex64Assistant();
    
    assert.ok(typeof assistant.executeTool === 'function');
  });

  it('应该返回包含 encode 方法的对象', (t) => {
    const assistant = createHex64Assistant();
    
    assert.ok(typeof assistant.encode === 'function');
    const result = assistant.encode('test');
    assert.equal(result.success, true);
  });
});

describe('hex64QuickEncode', () => {
  it('应该返回简化的编码结果', (t) => {
    const result = hex64QuickEncode('quick_test');
    
    assert.ok(result.hex_name);
    assert.ok(result.hex_en);
    assert.ok(result.binary);
    assert.ok(Array.isArray(result.tags));
    assert.ok(Array.isArray(result.feature_vector));
    assert.ok(result.pseudo_code);
  });

  it('应该对相同输入返回一致结果', (t) => {
    const result1 = hex64QuickEncode('consistent_test');
    const result2 = hex64QuickEncode('consistent_test');
    
    assert.equal(result1.hex_name, result2.hex_name);
    assert.equal(result1.binary, result2.binary);
  });
});

console.log('运行 AI 集成模块测试...\n');
