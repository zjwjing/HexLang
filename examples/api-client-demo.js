/**
 * Hex64 API 客户端示例
 * 
 * 演示如何通过 HTTP API 调用 Hex64 转码功能
 * 
 * 使用方式：
 *   1. 先启动 API 服务: node examples/api-server.js
 *   2. 运行此示例: node examples/api-client-demo.js
 */

/**
 * 封装 API 调用
 */
class Hex64APIClient {
  constructor(baseURL = 'http://localhost:3456') {
    this.baseURL = baseURL;
  }

  /**
   * 单次转码
   * @param {string} input - 输入文本
   * @param {object} options - 可选参数
   * @returns {Promise<object>}
   */
  async encode(input, options = {}) {
    const response = await fetch(`${this.baseURL}/api/hex64/encode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input,
        include_features: options.includeFeatures !== false,
        include_compiled: options.includeCompiled || false
      })
    });

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error);
    }

    return data;
  }

  /**
   * 批量转码
   * @param {string[]} inputs - 输入文本数组
   * @returns {Promise<object>}
   */
  async batchEncode(inputs) {
    const response = await fetch(`${this.baseURL}/api/hex64/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ inputs })
    });

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error);
    }

    return data;
  }

  /**
   * 健康检查
   * @returns {Promise<object>}
   */
  async health() {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }
}

/**
 * 主演示函数
 */
async function main() {
  const client = new Hex64APIClient();

  console.log('=== Hex64 API 客户端演示 ===\n');

  try {
    // 1. 健康检查
    console.log('1. 健康检查:');
    const health = await client.health();
    console.log(`   状态: ${health.status}`);
    console.log(`   版本: ${health.version}`);
    console.log(`   卦数: ${health.hexagrams}`);
    console.log(`   标签数: ${health.tagToOp}\n`);

    // 2. 单次转码
    console.log('2. 单次转码:');
    const testInputs = ['timeout_error', 'deploy_production', 'system_init'];
    
    for (const input of testInputs) {
      const result = await client.encode(input);
      console.log(`   输入: ${input}`);
      console.log(`   卦象: ${result.hexagram.name} (${result.hexagram.english})`);
      console.log(`   二进制: ${result.hexagram.binary}`);
      console.log(`   标签: ${result.hexagram.tags.join(', ')}`);
      console.log();
    }

    // 3. 批量转码
    console.log('3. 批量转码:');
    const batchResult = await client.batchEncode(['alpha', 'beta', 'gamma']);
    console.log(`   处理数量: ${batchResult.count}`);
    
    for (const item of batchResult.results) {
      console.log(`   ${item.input.padEnd(8)} → ${item.hex_name} [${item.binary}]`);
    }

    console.log('\n=== 演示完成 ===');
  } catch (error) {
    console.error('错误:', error.message);
    console.log('\n请先启动 API 服务: node examples/api-server.js');
  }
}

// 运行演示
main();
