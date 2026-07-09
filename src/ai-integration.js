/**
 * Hex64 AI 集成模块
 * 
 * 将 Hex64 转码引擎封装为 AI 工具，支持 Qwen3.5-9B 等大模型调用
 * 提供结构化特征编码，增强 AI 推理的可解释性
 * 
 * 使用方式：
 * 1. 作为独立工具调用
 * 2. 集成到 LangChain/LlamaIndex 等框架
 * 3. 通过 HTTP API 暴露给外部服务
 */

import { Hex64Engine } from '../src/core.js';
import { HEXAGRAMS, TAG_TO_OP } from '../src/database.js';

/**
 * Hex64 AI 工具类
 * 将转码引擎封装为符合 AI 工具调用规范的接口
 */
export class Hex64AITool {
  constructor() {
    this.engine = new Hex64Engine();
    this.name = 'hex64_encode';
    this.description = '将任意输入转为Hex64卦编码特征，用于增强AI推理的可解释性。不涉及任何玄学预测功能。';
  }

  /**
   * 获取工具 Schema（符合 OpenAI/Qwen 工具调用规范）
   */
  getSchema() {
    return {
      type: 'function',
      function: {
        name: this.name,
        description: this.description,
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
  }

  /**
   * 执行转码
   * @param {object} params - 工具调用参数
   * @returns {object} 结构化转码结果
   */
  execute(params) {
    const { input, include_features = true, include_compiled = false } = params;
    
    if (!input || typeof input !== 'string') {
      return {
        success: false,
        error: '输入必须是非空字符串'
      };
    }

    try {
      const result = this.engine.tranceive(input);
      
      // 基础结果
      const response = {
        success: true,
        input: input,
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

      // 可选：特征向量
      if (include_features) {
        response.features = {
          vector: result.featureVec,
          controlSignal: result.controlSignal,
          interpretation: this._interpretFeatures(result)
        };
      }

      // 可选：编译代码
      if (include_compiled) {
        response.compiled = this._generateCompiledCode(result);
      }

      return response;
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 解释特征向量含义
   */
  _interpretFeatures(result) {
    const { featureVec, controlSignal, hexCode } = result;
    
    // 统计阴阳爻数量
    const yangCount = featureVec.filter(b => b === 1).length;
    const yinCount = featureVec.filter(b => b === 0).length;
    
    return {
      yangYinRatio: `${yangCount}阳${yinCount}阴`,
      dominantEnergy: yangCount > yinCount ? '阳性（主动/外放）' : '阴性（被动/内敛）',
      gpioState: controlSignal.join(' → '),
      semanticTheme: hexCode.tags.slice(0, 3).join('、'),
      engineeringMapping: hexCode.tags.map(tag => TAG_TO_OP[tag] || tag.toUpperCase())
    };
  }

  /**
   * 生成多语言代码模板
   */
  _generateCompiledCode(result) {
    const { hexCode, pseudoCode } = result;
    const name = hexCode.name;
    
    return {
      javascript: `// HexLang → JS  ·  ${name}  (${hexCode.bin})\n  ${this._generateFunctionCalls(name, 'js')}`,
      python: `# HexLang → PY  ·  ${name}  (${hexCode.bin})\n  ${this._generateFunctionCalls(name, 'py')}`,
      rust: `// HexLang → RS  ·  ${name}  (${hexCode.bin})\n  ${this._generateFunctionCalls(name, 'rs')}`,
      go: `// HexLang → GO  ·  ${name}  (${hexCode.bin})\n  ${this._generateFunctionCalls(name, 'go')}`
    };
  }

  /**
   * 生成函数调用（简化版）
   */
  _generateFunctionCalls(name, lang) {
    const tags = HEXAGRAMS[0].tags; // 简化：使用示例标签
    const calls = tags.slice(0, 3).map(tag => {
      const op = TAG_TO_OP[tag] || tag.toUpperCase();
      switch(lang) {
        case 'js': return `    ${op.toLowerCase()}('${name}');`;
        case 'py': return `    ${op.toLowerCase()}('${name}')`;
        case 'rs': return `    ${op.toLowerCase()}::"${name}";`;
        case 'go': return `    ${op}("${name}")`;
        default: return `    ${op}('${name}')`;
      }
    });
    return calls.join('\n');
  }
}

/**
 * 创建 AI 助手（集成 Hex64 工具）
 * 
 * 示例用法：
 * ```javascript
 * const assistant = createHex64Assistant();
 * const response = await assistant.chat('分析这段日志：timeout_error_404');
 * ```
 */
export function createHex64Assistant(options = {}) {
  const {
    systemPrompt = null,
    maxTokens = 2048,
    temperature = 0.7
  } = options;

  // 默认 System Prompt：严格约束模型行为
  const defaultSystemPrompt = `你是一个专业的软件工程助手，使用Hex64符号编码系统增强代码可解释性。

## 重要约束
1. Hex64是确定性编码基础设施，基于邵雍先天六十四卦与二进制映射
2. 所有运算逻辑完全 deterministic（确定性），不涉及任何玄学预测
3. 卦象标签映射到工程概念：如"订阅"、"监听"、"重构"、"告警"等
4. 不要对卦象进行算命、预测、风水等解读

## 使用方式
当用户输入文本时，你可以调用 hex64_encode 工具获取其特征编码，然后：
- 解释编码的语义含义
- 提供对应的代码模板
- 给出工程实践建议`;

  const hexTool = new Hex64AITool();

  return {
    /**
     * 获取可用工具列表
     */
    getTools() {
      return [hexTool.getSchema()];
    },

    /**
     * 执行工具调用
     */
    executeTool(toolCall) {
      if (toolCall.function.name === hexTool.name) {
        const args = JSON.parse(toolCall.function.arguments);
        return hexTool.execute(args);
      }
      return { success: false, error: '未知工具' };
    },

    /**
     * 简化的聊天接口（需要外部 LLM 支持）
     */
    async chat(userMessage, llmClient) {
      // 这里假设传入一个符合 OpenAI 接口的 LLM client
      // 实际使用时需要集成具体的 AI 框架
      
      const messages = [
        { role: 'system', content: systemPrompt || defaultSystemPrompt },
        { role: 'user', content: userMessage }
      ];

      return llmClient.chat({
        messages,
        tools: hexTool.getTools(),
        max_tokens: maxTokens,
        temperature
      });
    },

    /**
     * 直接转码（不经过 LLM）
     */
    encode(input, options = {}) {
      return hexTool.execute({
        input,
        include_features: true,
        include_compiled: options.compiled || false
      });
    }
  };
}

/**
 * 简化的 Hex64 转码函数（适合直接嵌入 AI 提示）
 */
export function hex64QuickEncode(input) {
  const engine = new Hex64Engine();
  const result = engine.tranceive(input);
  
  return {
    hex_name: result.hexCode.name,
    hex_en: result.hexCode.en,
    binary: result.hexCode.bin,
    tags: result.hexCode.tags,
    pseudo_code: result.pseudoCode,
    feature_vector: result.featureVec
  };
}

export default Hex64AITool;
