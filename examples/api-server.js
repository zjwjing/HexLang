/**
 * Hex64 HTTP API 服务
 * 
 * 提供 RESTful API 接口，方便外部系统调用 Hex64 转码功能
 * 
 * 启动方式：
 *   node examples/api-server.js
 * 
 * API 端点：
 *   POST /api/hex64/encode     - 单次转码
 *   POST /api/hex64/batch      - 批量转码
 *   GET  /api/hex64/schema     - 获取工具 Schema
 *   GET  /health               - 健康检查
 */

import { Hex64Engine } from '../src/core.js';
import { HEXAGRAMS, TAG_TO_OP } from '../src/database.js';
import { HEX64_TOOL } from './openai-hex64-client.js';

const engine = new Hex64Engine();

/**
 * 解析 JSON 请求体
 */
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on('error', reject);
  });
}

/**
 * 发送 JSON 响应
 */
function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data, null, 2));
}

/**
 * 单次转码处理
 */
async function handleEncode(req, res) {
  try {
    const { input, include_features = true, include_compiled = false } = await parseBody(req);
    
    if (!input || typeof input !== 'string') {
      return sendJSON(res, 400, {
        success: false,
        error: '输入必须是非空字符串'
      });
    }

    const result = engine.tranceive(input);
    
    const response = {
      success: true,
      input,
      hexagram: {
        index: result.hexCode.index,
        name: result.hexCode.name,
        pinyin: result.hexCode.pinyin,
        english: result.hexCode.en,
        category: result.hexCode.category,
        tags: result.hexCode.tags,
        weight: result.hexCode.weight,
        binary: result.hexCode.bin
      },
      pseudoCode: result.pseudoCode
    };

    if (include_features) {
      response.features = {
        vector: result.featureVec,
        controlSignal: result.controlSignal
      };
    }

    sendJSON(res, 200, response);
  } catch (error) {
    sendJSON(res, 500, {
      success: false,
      error: error.message
    });
  }
}

/**
 * 批量转码处理
 */
async function handleBatch(req, res) {
  try {
    const { inputs } = await parseBody(req);
    
    if (!Array.isArray(inputs) || inputs.length === 0) {
      return sendJSON(res, 400, {
        success: false,
        error: 'inputs 必须是非空数组'
      });
    }

    const results = inputs.map(input => {
      try {
        const result = engine.tranceive(input);
        return {
          input,
          success: true,
          hex_name: result.hexCode.name,
          binary: result.hexCode.bin,
          tags: result.hexCode.tags
        };
      } catch (error) {
        return {
          input,
          success: false,
          error: error.message
        };
      }
    });

    sendJSON(res, 200, {
      success: true,
      count: results.length,
      results
    });
  } catch (error) {
    sendJSON(res, 500, {
      success: false,
      error: error.message
    });
  }
}

/**
 * 获取工具 Schema
 */
function handleSchema(req, res) {
  sendJSON(res, 200, {
    success: true,
    tool: HEX64_TOOL
  });
}

/**
 * 健康检查
 */
function handleHealth(req, res) {
  sendJSON(res, 200, {
    status: 'ok',
    version: '1.2.0',
    hexagrams: HEXAGRAMS.length,
    tagToOp: Object.keys(TAG_TO_OP).length
  });
}

/**
 * 路由处理
 */
function route(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  if (req.method === 'POST' && path === '/api/hex64/encode') {
    handleEncode(req, res);
  } else if (req.method === 'POST' && path === '/api/hex64/batch') {
    handleBatch(req, res);
  } else if (req.method === 'GET' && path === '/api/hex64/schema') {
    handleSchema(req, res);
  } else if (req.method === 'GET' && path === '/health') {
    handleHealth(req, res);
  } else {
    sendJSON(res, 404, {
      success: false,
      error: '接口不存在'
    });
  }
}

/**
 * 启动 API 服务器
 * @param {number} port - 端口号
 * @returns {Promise<import('http').Server>}
 */
export async function startServer(port = 3456) {
  const http = await import('node:http');
  
  const server = http.createServer(route);
  
  return new Promise((resolve) => {
    server.listen(port, () => {
      console.log(`Hex64 API 服务已启动`);
      console.log(`本地地址: http://localhost:${port}`);
      console.log(`API 端点:`);
      console.log(`  POST /api/hex64/encode  - 单次转码`);
      console.log(`  POST /api/hex64/batch   - 批量转码`);
      console.log(`  GET  /api/hex64/schema  - 获取工具 Schema`);
      console.log(`  GET  /health            - 健康检查`);
      resolve(server);
    });
  });
}

// 直接运行时启动服务器
if (import.meta.url === `file://${process.argv[1]}`) {
  startServer();
}

export { HEX64_TOOL };
export default { startServer, HEX64_TOOL };
