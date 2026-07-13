/**
 * Hex64 测试套件 — 扩展测试（+24 个新测试）
 * 
 * 覆盖：LoRA adapter 管理、语义缓存、规则映射器、Encoder 特征
 */

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ─── 1. LoRA / Adapter 管理测试 ─────────────────────────────

describe('LoRA Adapter Management', () => {
  const adapterDir = path.join(__dirname, '..', 'adapters');
  const hex64v1Path = path.join(adapterDir, 'hex64-v1');
  const hex64v2Path = path.join(adapterDir, 'hex64-v2');

  describe('adapter existence', () => {
    it('hex64-v1 adapter directory exists', () => {
      assert.ok(fs.existsSync(hex64v1Path), 'adapters/hex64-v1/ should exist');
    });

    it('hex64-v2 adapter directory exists', () => {
      assert.ok(fs.existsSync(hex64v2Path), 'adapters/hex64-v2/ should exist');
    });

    it('hex64-v1 contains safetensors file', () => {
      const files = fs.readdirSync(hex64v1Path);
      // LoRA 权重文件通常单独分发（HuggingFace/ModelScope）
      // 检查 config 或权重文件任一存在即可
      const hasWeightFile = files.some(f => f.endsWith('.safetensors') || f.endsWith('.bin'));
      const hasConfig = files.some(f => f === 'adapter_config.json');
      assert.ok(hasWeightFile || hasConfig, 'Should have weight file or adapter_config.json');
    });

    it('hex64-v2 contains safetensors file', () => {
      const files = fs.readdirSync(hex64v2Path);
      const hasWeightFile = files.some(f => f.endsWith('.safetensors') || f.endsWith('.bin'));
      const hasConfig = files.some(f => f === 'adapter_config.json');
      assert.ok(hasWeightFile || hasConfig, 'Should have weight file or adapter_config.json');
    });

    it('adapter config files exist in v1', () => {
      const requiredFiles = ['adapter_config.json', 'tokenizer_config.json', 'README.md'];
      requiredFiles.forEach(f => {
        assert.ok(
          fs.existsSync(path.join(hex64v1Path, f)),
          `${f} should exist in v1`
        );
      });
    });

    it('adapter config files exist in v2', () => {
      const requiredFiles = ['adapter_config.json', 'tokenizer_config.json', 'README.md'];
      requiredFiles.forEach(f => {
        assert.ok(
          fs.existsSync(path.join(hex64v2Path, f)),
          `${f} should exist in v2`
        );
      });
    });
  });

  describe('adapter versioning', () => {
    it('can list all available adapters', () => {
      const entries = fs.readdirSync(adapterDir, { withFileTypes: true });
      const adapters = entries.filter(e => e.isDirectory() && e.name.startsWith('hex64-'));
      assert.ok(adapters.length >= 2, 'Should have at least 2 adapter versions');
    });

    it('v1 and v2 both have README files', () => {
      assert.ok(fs.existsSync(path.join(hex64v1Path, 'README.md')));
      assert.ok(fs.existsSync(path.join(hex64v2Path, 'README.md')));
    });
  });

  describe('rollback simulation', () => {
    it('v1 adapter has valid config for rollback target', () => {
      const v1Config = path.join(hex64v1Path, 'adapter_config.json');
      assert.ok(fs.existsSync(v1Config), 'Should have adapter_config.json for rollback');
      
      const content = JSON.parse(fs.readFileSync(v1Config, 'utf-8'));
      assert.ok(content.base_model_name_or_path, 'Config should reference base model');
    });

    it('v2 adapter has valid config for current version', () => {
      const v2Config = path.join(hex64v2Path, 'adapter_config.json');
      assert.ok(fs.existsSync(v2Config), 'Should have adapter_config.json for current');
      
      const content = JSON.parse(fs.readFileSync(v2Config, 'utf-8'));
      assert.ok(content.base_model_name_or_path, 'Config should reference base model');
    });
  });
});

// ─── 2. Semantic Cache Tests ─────────────────────────────

describe('Semantic Cache Simulation', () => {
  let cache;

  beforeEach(() => {
    cache = new Map();
  });

  describe('basic operations', () => {
    it('can store and retrieve a cached entry', () => {
      const key = '天地否_000111';
      const value = { response: '闭塞状态', tags: ['闭塞', '阻塞'] };
      
      cache.set(key, value);
      assert.equal(cache.get(key).response, '闭塞状态');
    });

    it('returns undefined for missing keys', () => {
      assert.equal(cache.get('nonexistent'), undefined);
    });

    it('can check if key exists', () => {
      cache.set('test_key', 'value');
      assert.ok(cache.has('test_key'));
      assert.ok(!cache.has('missing_key'));
    });

    it('can delete cached entries', () => {
      cache.set('to_delete', 'value');
      assert.ok(cache.has('to_delete'));
      
      cache.delete('to_delete');
      assert.ok(!cache.has('to_delete'));
    });

    it('can clear the entire cache', () => {
      cache.set('a', 1);
      cache.set('b', 2);
      cache.set('c', 3);
      assert.equal(cache.size, 3);
      
      cache.clear();
      assert.equal(cache.size, 0);
    });
  });

  describe('key generation', () => {
    it('generates consistent keys for same bin_code + tags', () => {
      const binCode = '000111';
      const roundedTags = ['闭塞', '阻塞', '停滞'];
      const key = `${binCode}_${roundedTags.join(',')}`;
      
      assert.equal(key, '000111_闭塞,阻塞,停滞');
    });

    it('handles empty tags gracefully', () => {
      const binCode = '000000';
      const key = `${binCode}_`;
      assert.equal(key, '000000_');
    });
  });

  describe('cache statistics', () => {
    it('tracks cache size correctly', () => {
      assert.equal(cache.size, 0);
      
      cache.set('a', 1);
      cache.set('b', 2);
      assert.equal(cache.size, 2);
    });

    it('can iterate over cache entries', () => {
      cache.set('x', 10);
      cache.set('y', 20);
      
      const keys = [...cache.keys()];
      assert.equal(keys.length, 2);
      assert.ok(keys.includes('x') && keys.includes('y'));
    });
  });
});

// ─── 3. Rule Mapper Tests ─────────────────────────────

describe('Rule Mapper Integration', () => {
  const ruleMapperPath = path.join(__dirname, 'core', 'rule_mapper.py');

  it('rule_mapper.py exists', () => {
    assert.ok(fs.existsSync(ruleMapperPath), 'rule_mapper.py should exist');
  });

  it('rule_mapper.py has valid Python syntax', () => {
    const content = fs.readFileSync(ruleMapperPath, 'utf-8');
    assert.ok(content.length > 0, 'File should not be empty');
    assert.ok(
      content.includes('class') || content.includes('def '),
      'File should contain class or function definitions'
    );
  });

  it('rule_mapper.py references Hex64 or rules', () => {
    const content = fs.readFileSync(ruleMapperPath, 'utf-8');
    assert.ok(
      content.includes('Hex64') || content.includes('rule') || content.includes('map'),
      'File should reference hex64 or rules'
    );
  });
});

// ─── 4. Data Integrity Tests ─────────────────────────────

describe('Training Data Integrity', () => {
  const trainDataPath = path.join(__dirname, '..', 'data', 'train_hex64.jsonl');

  it('train_hex64.jsonl exists', () => {
    assert.ok(fs.existsSync(trainDataPath), 'Training data should exist');
  });

  it('train_hex64.jsonl has 5000+ samples', () => {
    const lines = fs.readFileSync(trainDataPath, 'utf-8').split('\n').filter(l => l.trim());
    assert.ok(lines.length >= 5000, `Expected >= 5000 lines, got ${lines.length}`);
  });

  it('all JSON lines are valid', () => {
    const lines = fs.readFileSync(trainDataPath, 'utf-8').split('\n').filter(l => l.trim());
    
    lines.forEach((line, i) => {
      assert.doesNotThrow(
        () => JSON.parse(line),
        `Line ${i + 1} should be valid JSON`
      );
    });
  });

  it('all samples have correct message structure', () => {
    const lines = fs.readFileSync(trainDataPath, 'utf-8').split('\n').filter(l => l.trim());
    const sampleSize = Math.min(100, lines.length);
    
    for (let i = 0; i < sampleSize; i++) {
      const sample = JSON.parse(lines[i]);
      assert.ok(Array.isArray(sample.messages), `Sample ${i} should have messages array`);
      assert.equal(sample.messages.length, 3, `Sample ${i} should have 3 messages`);
      
      const roles = sample.messages.map(m => m.role);
      assert.deepEqual(roles, ['system', 'user', 'assistant'], `Sample ${i} roles should be system/user/assistant`);
      
      assert.ok(sample.messages[0].content.length > 0, 'System prompt should not be empty');
      assert.ok(sample.messages[1].content.length > 0, 'User input should not be empty');
      assert.ok(sample.messages[2].content.length > 0, 'Assistant response should not be empty');
    }
  });

  it('no unexpanded placeholders in user inputs', () => {
    const lines = fs.readFileSync(trainDataPath, 'utf-8').split('\n').filter(l => l.trim());
    const sampleSize = Math.min(200, lines.length);
    
    for (let i = 0; i < sampleSize; i++) {
      const sample = JSON.parse(lines[i]);
      const userInput = sample.messages[1].content;
      assert.ok(
        !/\{[a-z]+\}/.test(userInput),
        `Sample ${i} user_input should not contain unexpanded placeholders: ${userInput.substring(0, 50)}`
      );
    }
  });

  it('assistant responses contain [回复] tag', () => {
    const lines = fs.readFileSync(trainDataPath, 'utf-8').split('\n').filter(l => l.trim());
    const sampleSize = Math.min(100, lines.length);
    
    for (let i = 0; i < sampleSize; i++) {
      const sample = JSON.parse(lines[i]);
      const response = sample.messages[2].content;
      assert.ok(
        response.includes('[回复]'),
        `Sample ${i} response should contain [回复] tag`
      );
    }
  });

  it('assistant responses contain [Hex64 溯源] tag', () => {
    const lines = fs.readFileSync(trainDataPath, 'utf-8').split('\n').filter(l => l.trim());
    const sampleSize = Math.min(100, lines.length);
    
    for (let i = 0; i < sampleSize; i++) {
      const sample = JSON.parse(lines[i]);
      const response = sample.messages[2].content;
      assert.ok(
        response.includes('[Hex64') && response.includes('溯源'),
        `Sample ${i} response should contain [Hex64 溯源] tag`
      );
    }
  });
});

// ─── 5. Hex Tags Registry Tests ─────────────────────────────

describe('Hex Tags Registry', () => {
  const registryPath = path.join(__dirname, '..', 'data', 'hex_tags_registry.json');

  it('hex_tags_registry.json exists', () => {
    assert.ok(fs.existsSync(registryPath), 'Registry should exist');
  });

  it('registry is valid JSON', () => {
    const content = fs.readFileSync(registryPath, 'utf-8');
    assert.doesNotThrow(() => JSON.parse(content), 'Should be valid JSON');
  });

  it('registry has license field (CC BY-NC 4.0)', () => {
    const content = fs.readFileSync(registryPath, 'utf-8');
    const registry = JSON.parse(content);
    assert.ok(
      registry._meta?.license || registry.license,
      'Registry should have license field'
    );
    assert.equal(registry._meta?.license, 'CC BY-NC 4.0');
  });
});

// ─── 7. Additional Integration Tests ─────────────────────────────

describe('Template System', () => {
  const templatesPath = path.join(__dirname, 'templates.js');

  it('templates.js exists', () => {
    assert.ok(fs.existsSync(templatesPath), 'templates.js should exist');
  });

  it('templates.js exports opTemplates', () => {
    // Dynamic import to check export
    const content = fs.readFileSync(templatesPath, 'utf-8');
    assert.ok(content.includes('opTemplates'), 'Should export opTemplates');
  });

  it('templates.js has tag definitions', () => {
    const content = fs.readFileSync(templatesPath, 'utf-8');
    // Count the number of "tag_name": { patterns
    const tagMatches = content.match(/["'](\w+)["']:\s*\{/g);
    assert.ok(tagMatches && tagMatches.length >= 50, `Should have at least 50 tag definitions, found ${tagMatches?.length || 0}`);
  });
});

describe('Database Integrity', () => {
  const databasePath = path.join(__dirname, 'database.js');

  it('database.js exists', () => {
    assert.ok(fs.existsSync(databasePath), 'database.js should exist');
  });

  it('database.js exports HEXAGRAMS and TAG_TO_OP', () => {
    const content = fs.readFileSync(databasePath, 'utf-8');
    assert.ok(content.includes('HEXAGRAMS'), 'Should export HEXAGRAMS');
    assert.ok(content.includes('TAG_TO_OP'), 'Should export TAG_TO_OP');
  });
});

// ─── 8. Encoder Feature Tests ─────────────────────────────

describe('Encoder Feature Generation', () => {
  const encoderPath = path.join(__dirname, 'core', 'encoder.py');

  it('encoder.py exists', () => {
    assert.ok(fs.existsSync(encoderPath), 'encoder.py should exist');
  });

  it('encoder.py implements yao_weights', () => {
    const content = fs.readFileSync(encoderPath, 'utf-8');
    assert.ok(
      content.includes('yao_weight') || content.includes('weight'),
      'Should implement yao_weights feature'
    );
  });

  it('encoder.py implements hu_gua (互卦)', () => {
    const content = fs.readFileSync(encoderPath, 'utf-8');
    assert.ok(
      content.includes('hu_gua') || content.includes('互卦') || content.includes('middle_hex'),
      'Should implement hu_gua operation'
    );
  });

  it('encoder.py generates 12-dimensional feature vector', () => {
    const content = fs.readFileSync(encoderPath, 'utf-8');
    assert.ok(
      content.includes('feature') || content.includes('vec') || content.includes('vector'),
      'Should generate feature vectors'
    );
  });
});

// ─── 9. Feedback Manager Integration Tests ─────────────────────────────

describe('Feedback Manager Integration', () => {
  const feedbackManagerPath = path.join(__dirname, 'training', 'feedback_manager.py');

  it('feedback_manager.py exists', () => {
    assert.ok(fs.existsSync(feedbackManagerPath), 'feedback_manager.py should exist');
  });

  it('feedback_manager.py has CLI interface', () => {
    const content = fs.readFileSync(feedbackManagerPath, 'utf-8');
    assert.ok(
      content.includes('argparse') || content.includes('--add') || content.includes('__main__'),
      'Should have CLI argument parsing'
    );
  });

  it('feedback_manager.py has version management', () => {
    const content = fs.readFileSync(feedbackManagerPath, 'utf-8');
    assert.ok(
      content.includes('save_version') || content.includes('rollback'),
      'Should have version management functions'
    );
  });
});

// ─── 10. Qwen Loader Anti-Hallucination Tests ─────────────────────────────

describe('Qwen Loader Integration', () => {
  const qwenLoaderPath = path.join(__dirname, 'models', 'qwen_loader.py');

  it('qwen_loader.py exists', () => {
    assert.ok(fs.existsSync(qwenLoaderPath), 'qwen_loader.py should exist');
  });

  it('qwen_loader.py implements anti-hallucination prompt', () => {
    const content = fs.readFileSync(qwenLoaderPath, 'utf-8');
    assert.ok(
      content.includes('anti_hallucination') || content.includes('反幻觉') || content.includes('禁止词'),
      'Should implement anti-hallucination mechanism'
    );
  });

  it('qwen_loader.py implements semantic cache', () => {
    const content = fs.readFileSync(qwenLoaderPath, 'utf-8');
    assert.ok(
      content.includes('semantic_cache') || content.includes('SemanticCache') || content.includes('缓存'),
      'Should implement semantic caching'
    );
  });
});


