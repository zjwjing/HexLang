/**
 * Hex64 + OpenAI Compatible API 集成
 * 
 * 兼容任何 OpenAI API 格式的模型（包括 Qwen、ChatGLM、LocalLLM 等）
 * 支持 Function Calling（工具调用）
 * 
 * 使用方式：
 *   1. 本地部署：Ollama / vLLM / LM Studio
 *   2. 云端 API：阿里云 DashScope / OpenAI
 *   3. 直接转码：不需要 AI 模型
 */

import { Hex64Engine } from '../src/core.js';
import { TAG_TO_OP } from '../src/database.js';

/**
 * Hex64 工具定义（OpenAI Function Calling 格式）
 */
export const HEX64_TOOL = {
  type: 'function',
  function: {
    name: 'hex64_encode',
    description: '将任意输入转为Hex64卦编码特征，用于增强AI推理的可解释性。不涉及任何玄学预测功能。',
    parameters: {
      type: 'object',
      properties: {
        input: {
          type: 'string',
          description: '需要转码的输入内容（文本、日志、指令等）'
        },
        include_features: {
          type: 'boolean',
          description: '是否包含特征向量和GPIO信号',
          default: true
        },
        include_compiled: {
          type: 'boolean',
          description: '是否包含多语言代码模板',
          default: false
        }
      },
      required: ['input']
    }
  }
};

/**
 * Hex64 AI 客户端
 * 封装与 OpenAI 兼容 API 的交互
 */
export class Hex64AIClient {
  /**
   * @param {object} options
   * @param {string} options.apiBase - API 基础地址（如 http://localhost:11434/v1）
   * @param {string} options.apiKey - API 密钥（可选）
   * @param {string} options.model - 模型名称
   * @param {number} options.maxTokens - 最大生成长度
   * @param {number} options.temperature - 采样温度
   */
  constructor(options = {}) {
    this.apiBase = options.apiBase || 'http://localhost:11434/v1';
    this.apiKey = options.apiKey || '';
    this.model = options.model || 'qwen3.5-9b';
    this.maxTokens = options.maxTokens || 2048;
    this.temperature = options.temperature || 0.7;
    this.engine = new Hex64Engine();
  }

  /**
   * 发送聊天请求（支持工具调用）
   * @param {Array} messages - 消息历史
   * @param {boolean} useTool - 是否启用 Hex64 工具
   * @returns {Promise<object>}
   */
  async chat(messages, useTool = true) {
    const url = `${this.apiBase}/chat/completions`;
    
    const body = {
      model: this.model,
      messages: messages,
      max_tokens: this.maxTokens,
      temperature: this.temperature,
      stream: false
    };

    // 如果启用工具调用，添加工具定义
    if (useTool) {
      body.tools = [HEX64_TOOL];
      body.tool_choice = 'auto';
    }

    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        throw new Error(`API 请求失败: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Hex64 AI 调用错误:', error.message);
      throw error;
    }
  }

  /**
   * 处理工具调用响应
   * @param {object} aiResponse - AI 返回的响应
   * @returns {Array} 工具调用结果消息
   */
  processToolCalls(aiResponse) {
    const message = aiResponse.choices?.[0]?.message;
    if (!message) return [];

    const toolResults = [];
    
    if (message.tool_calls) {
      for (const toolCall of message.tool_calls) {
        if (toolCall.function.name === 'hex64_encode') {
          const args = JSON.parse(toolCall.function.arguments);
          const result = this.engine.tranceive(args.input);
          
          toolResults.push({
            tool_call_id: toolCall.id,
            role: 'tool',
            content: JSON.stringify({
              success: true,
              hex_name: result.hexCode.name,
              binary: result.hexCode.bin,
              tags: result.hexCode.tags,
              feature_vector: result.featureVec,
              control_signal: result.controlSignal
            }, null, 2)
          });
        }
      }
    }

    return toolResults;
  }

  /**
   * 简化的转码接口（不依赖 AI 模型）
   * @param {string} input - 输入文本
   * @returns {object} 结构化转码结果
   */
  encode(input) {
    const result = this.engine.tranceive(input);
    
    return {
      input,
      hexagram: {
        name: result.hexCode.name,
        english: result.hexCode.en,
        binary: result.hexCode.bin,
        tags: result.hexCode.tags,
        category: result.hexCode.category
      },
      features: {
        vector: result.featureVec,
        gpio: result.controlSignal
      }
    };
  }
}

/**
 * 创建带 System Prompt 的对话
 * @param {string} userInput - 用户输入
 * @param {Hex64AIClient} client - AI 客户端实例
 * @param {string} systemPrompt - 系统提示词
 * @returns {Promise<object>}
 */
export async function chatWithHex64(userInput, client, systemPrompt = null) {
  const defaultPrompt = `你是一个专业的软件工程助手。你使用 Hex64 符号编码系统将输入文本映射到六十四卦特征，
从而增强代码生成的可解释性。

## 约束
- Hex64 是确定性编码基础设施，不涉及任何玄学预测
- 卦象标签映射到工程概念：如"订阅"、"监听"、"重构"、"告警"等
- 不要进行算命、预测、风水等解读

## 工作流程
1. 分析用户输入的文本/日志/指令
2. 调用 hex64_encode 工具获取特征编码
3. 根据编码结果提供工程建议或代码模板`;

  const messages = [
    { role: 'system', content: systemPrompt || defaultPrompt },
    { role: 'user', content: userInput }
  ];

  // 第一步：发送请求（可能包含工具调用）
  const response = await client.chat(messages, true);
  const message = response.choices?.[0]?.message;

  // 如果有工具调用，执行并返回结果
  if (message?.tool_calls?.length > 0) {
    const toolResults = client.processToolCalls(response);
    
    // 第二步：携带工具结果再次请求
    messages.push(message);
    messages.push(...toolResults);
    
    return await client.chat(messages, false);
  }

  return response;
}

/**
 * 快速编码（不依赖 AI 模型）
 * @param {string} input - 输入文本
 * @returns {object}
 */
export function quickEncode(input) {
  const engine = new Hex64Engine();
  const result = engine.tranceive(input);
  
  return {
    input,
    hex_name: result.hexCode.name,
    hex_en: result.hexCode.en,
    binary: result.hexCode.bin,
    tags: result.hexCode.tags,
    category: result.hexCode.category,
    feature_vector: result.featureVec,
    control_signal: result.controlSignal,
    pseudo_code: result.pseudoCode
  };
}

export { HEX64_TOOL };
export default Hex64AIClient;
