# TASKS.md — HexLang 任务看板

> 详细任务卡存放在个人助理工作区：
> `C:/Users/zjwji/.bitfun/personal_assistant/workspace/.tasks/`
>
> 本文件为高层任务总览，快速了解项目当前状态。

---

## 活跃任务

| 编号 | 任务 | 状态 | 优先级 | 负责人 | 来源 | 关联任务卡 |
|------|------|------|--------|--------|------|-----------|
| 024 | LoRA 微调训练（Qwen3-8B + 2002 条数据）| ✅ **完成** | P0 | 朵朵 | 训练计划 | adapters/hex64-v1/ (loss=0.0484) |
| 027 | Qwen3.5-9B 升级训练（unsloth/Qwen3.5-9B 已下载）| 🔴 阻塞 | P1 | 朵朵 | 训练计划 | Unsloth + triton 版本兼容问题 |
| 025 | Feedback 闭环管理系统 | ✅ **完成** | P0 | 朵朵 | 用户建议 | src/training/feedback_manager.py |
| 026 | 合规防护落地（MIT 版权头 + 数据源标注 + CC BY-NC 4.0）| ✅ **完成** | P0 | 朵朵 | 用户建议 | LICENSE + _sources.json + hex_tags_registry.json |
| 027 | 文档体系完善（UNIQUENESS.md + ARCHITECTURE.md + SECURITY.md）| ✅ **完成** | P1 | 朵朵 | 用户建议 | 3 个核心文档 |
| 016 | QLoRA 训练目标加"文本→64维卦分布"辅助损失 | 📋 待做 | P2 | 朵朵 | bagau-llm 思路吸收 | — |

## 已完成任务

| 编号 | 任务 | 完成时间 | 负责人 | 来源 |
|------|------|---------|--------|------|
| 007 | Hex64 代码审计与修缮 | 2026-07-08 | 朵朵 | ClaudeCode |
| 008 | 添加 Rust/Go 编译目标 + 2×2 Demo 网格 | 2026-07-09 | 朵朵 | OpenCode |
| 009 | DOMINATE 卦语义修复（depth.probe→leader.dominate）| 2026-07-09 | 朵朵 | OpenCode |
| 010 | 审计修复：17个 JS/Py 语义错误 + BLOCK Go PascalCase | 2026-07-09 | 朵朵 | OpenCode |
| 011 | 优化：6个错误 JS 模板 + O(1) bin 查找 + 去重 hash | 2026-07-09 | 朵朵 | OpenCode |
| 012 | 架构重构：抽取共享编译器模块，消除重复存储（-264行）| 2026-07-09 | 朵朵 | OpenCode |
| 013 | 先天八卦圆形 LOGO 排列 | 2026-07-09 | 朵朵 | OpenCode |
| 014 | 整合 Wilhelm 数据集（Unicode 符号 + 英文名）| 2026-07-09 | 朵朵 | adamblvck/iching-wilhelm-dataset |
| 015 | 添加 Related Work 生态定位文档 | 2026-07-09 | 朵朵 | OpenCode |
| 016 | 互卦运算（中爻滑窗）| 2026-07-09 | 朵朵 | OpenCode |
| 017 | 爻级权重 yao_weights + 确定性 seed 模式 | 2026-07-09 | 朵朵 | OpenCode |
| 018 | Wilhelm 注释 + 中文原文 + Base64 映射整合 | 2026-07-09 | 朵朵 | 3 个开源数据源 |
| 019 | 方图 Cartesian 积模式（邵雍先天方图）| 2026-07-09 | 朵朵 | OpenCode |
| 020 | 爻辰 mod384 计数器（京房纳甲）| 2026-07-09 | 朵朵 | OpenCode |
| 021 | 禹步 PRNG（洛书 3×3 网格）| 2026-07-09 | 朵朵 | OpenCode |
| 022 | 太玄三进制编码 + 元会运世嵌套计数器 | 2026-07-09 | 朵朵 | OpenCode |
| 023 | **Python Encoder 架构升级：爻权重 + 互卦 + CoT Prompt** | **2026-07-xx** | **朵朵** | **用户建议** | **Encoder 从"标签系统"升级为"特征生成器"** |
| 024 | **Rule Mapper：业务规则 → 卦象映射器** | **2026-07-xx** | **朵朵** | **用户建议** | **实现 if-else → 卦象确定性编码** |
| 025 | **QwenLoader System Prompt：强制思维链推理** | **2026-07-xx** | **朵朵** | **用户建议** | **CoT 爻位分析 + 互卦推演** |
| 026 | **Semantic Cache：基于爻权重的推理缓存** | **2026-07-xx** | **朵朵** | **qwen_loader.py** | **避免重复推理相同卦象** |

## 模块健康度

| 模块 | 状态 | 备注 |
|------|------|------|
| `src/core.js` | 🟢 正常 | 引擎核心：O(1) binIndex、encodeSeeded、7种运算（含互卦）|
| `src/compiler.js` | 🟢 正常 | 共享编译逻辑（compileHex），4语言输出 |
| `src/templates.js` | 🟢 正常 | 384条模板（单一数据源，build script 生成）|
| `src/database.js` | 🟢 正常 | 数据层（HEXAGRAMS + TAG_TO_OP）|
| `src/taixuan.js` | 🟢 正常 | 太玄三进制编码（81首+729赞）|
| `src/yuanhui.js` | 🟢 正常 | 元会运世四层嵌套计数器 |
| `src/compile.test.js` | 🟢 正常 | 8个编译测试（4语言覆盖）|
| `src/core.test.js` | 🟢 正常 | 56/56 通过（含方图/爻辰/禹步/encodeSeeded）|
| `src/engine.html` | 🟢 正常 | 浏览器 Demo：2×2编译器网格、7种运算、暗色模式 |
| `data/hex64_full.json` | 🟢 正常 | v1.2.0，64卦 + 443 tagToOp + yao_weights + hex_font + english |
| `bin/hex64.js` | 🟢 正常 | CLI：先天八卦 LOGO、4语言彩色输出、JSON 模式 |
| `scripts/rebuild-templates.mjs` | 🟢 正常 | 构建脚本：从 templates.js 读取，生成 rs/go |
| `.github/workflows/ci.yml` | 🟢 正常 | CI (Node 18/20/22) |
| `README.md` | 🟢 正常 | 含 Related Work 生态定位、运算规则表（含互卦）|
| **`src/core/encoder.py`** | **🟢 升级** | **爻级加权特征 + 互卦计算 + 12维组合向量** |
| **`src/models/qwen_loader.py`** | **🟢 升级** | **CoT System Prompt + 语义缓存 + 防幻觉约束** |
| **`src/core/rule_mapper.py`** | **🟢 新增** | **业务规则→卦象确定性映射器** |

## 审计摘要 (2026-07-09 最终)

| 检查项 | 结果 |
|--------|------|
| 数据完整性 | ✅ 64卦、64唯一二进制、0问题 |
| 字段完整性 | ✅ bin/name/pinyin/en/category/tags/weight/hex_font/english/yao_weights 全部存在 |
| 模板完整性 | ✅ 384条，0缺失，0命名违规，0占位符不匹配 |
| 模块架构 | ✅ bin/engine 均引用共享模块，无内联 opTemplates |
| 核心功能 | ✅ encodeSeeded + binIndex + 互卦 |
| 运算能力 | ✅ 7/7：错卦/综卦/变爻/AND/OR/XOR/互卦 |
| 测试 | ✅ 56/56 通过（48引擎+8编译）|
| CLI | ✅ JS/Py/Rs/Go 全部正常输出 |
| 跨文件一致性 | ✅ 0 不匹配 |
| Rust snake_case | ✅ 0 个 camelCase |
| Go PascalCase | ✅ 0 个 lowercase |

## 架构说明

```
src/templates.js    ← 唯一数据源（rebuild-templates.mjs 生成）
src/compiler.js     ← 唯一 compileHex 逻辑（4语言）
src/core.js         ← 引擎核心（Hex64Engine 类）
bin/hex64.js        ← CLI（import 共享模块）
src/engine.html     ← 浏览器 Demo（<script type="module">）
data/hex64_full.json ← 64卦数据（含 yao_weights、hex_font、english）
```

## 运算清单

| 运算 | 指令 | 说明 |
|------|------|------|
| 错卦 | cuo (NOT) | 每位取反 |
| 综卦 | zong (REV) | 爻序反转 |
| 变爻 | bian (XOR) | 与第二卦按位异或 |
| 卦叠加 AND | AND | 按位与 |
| 卦叠加 OR | OR | 按位或 |
| 卦叠加 XOR | XOR | 按位异或 |
| **互卦** | **hu** | **取二三四五爻，二三四为下卦、三四五为上卦** |

## 计算谱系模式

| 模式 | 方法 | 计算原型 | 来源 |
|------|------|---------|------|
| 方图 | `encodeFangtu(text)` | 8×8 Cartesian 积（邵雍先天方图）| `src/core.js` |
| 爻辰 | `encodeYaochen(text, ts)` | mod384 循环计数器（京房纳甲）| `src/core.js` |
| 禹步 | `encodeYubu(seed)` | 3×3 网格 Hamiltonian 游走 PRNG | `src/core.js` |
| 太玄首 | `TaiXuanEncoder.encodeShou(text)` | 3^4=81 首三进制编码 | `src/taixuan.js` |
| 太玄赞 | `TaiXuanEncoder.encodeZan(text)` | 3^6=729 赞三进制编码 | `src/taixuan.js` |
| 元会运世 | `YuanHuiEncoder.encode(ts)` | 四层嵌套模运算 | `src/yuanhui.js` |

## 数据来源

| 来源 | 数据 | 状态 |
|------|------|------|
| adamblvck/iching-wilhelm-dataset | Unicode 符号 + 英文名 + 威廉注释 | ✅ 已整合 |
| qntm/hexagram-encode | Base64 ↔ 卦符映射 | ✅ 已整合 |
| chengjun/iching | 中文原文/白话文解释 | ✅ 已整合 (63/64) |

## 训练计划

### 前提条件

- 硬件：NVIDIA RTX 4080 SUPER（16GB VRAM，当前可用）
- 模型：`unsloth/Qwen3.5-9B`（已下载至 `models/unsloth_Qwen3.5-9B/`，8.21B 参数，BF16 格式）
- 依赖：transformers 4.57.3 + peft 0.19.1 + trl 0.24.0 + datasets 4.3.0（均已安装）
- 训练数据：`data/train_hex64.jsonl` — **2002 条 ✅**

### 快速开始

```bash
# 模型已下载到 models/unsloth_Qwen3.5-9B/（8.21B 参数，BF16）
# 运行 LoRA 微调：
python src/training/train_lora.py

# 输出：adapters/hex64-v1/（约 50MB，LoRA 适配器权重）
```

### 参数（RTX 4080 SUPER 优化版）

| 参数 | 值 | 说明 |
|------|-----|------|
| max_steps | 300 | 2002 条数据充分收敛 |
| batch_size | 4 | 有效 Batch Size = 8 |
| gradient_accumulation_steps | 2 | |
| learning_rate | 3e-4 | 加快收敛 |
| warmup_steps | 30 | 前 30 步预热 |
| save_steps | 50 | 每 50 步存检查点 |
| save_total_limit | 3 | 保留 3 个版本 |
| use_4bit | true | INT4 量化，显存约 8GB |
| lora_rank | 16 | LoRA 秩 |

---

## 发展计划（2026.7 — 2027.12）

### 核心原则

1. **不拼人力拼定义** — 核心数据结构（卦象 Schema、工程语义标签集）的解释权握在自己手中，代码可 MIT，定义不可复制
2. **不堆功能做深度** — 只做「卦象→工程」窄赛道的唯一标准
3. **不赶风口做长期** — 不被 AI 热点带偏，所有动作围绕「可解释性 + 确定性」
4. **不闭门造车借社区** — 核心逻辑自己写，边缘功能靠社区贡献

### 第一阶段：核心闭环落地（2026.7-2026.9）

| 编号 | 任务 | 交付物 | 时间 | 优先级 |
|------|------|--------|------|--------|
| P1-1 | 跑通 Qwen3.5-9B QLoRA 训练 | adapters/hex64-v1/（50MB）、训练日志、loss 曲线 | 2026.7 下旬 | **P0** |
| P1-2 | 固化 feedback 闭环 | 自动重训脚本、adapter 版本管理+回滚、feedback 去重/衰减 | 2026.8 上旬 | **P0** |
| P1-3 | 合规防护落地 | MIT 版权头、hexagrams.json 加 _meta/origin、hex_tags_registry.json 走 CC BY-NC 4.0 | 2026.8 中旬 | **P0** |
| P1-4 | 训练数据扩容 | 从 2002 条扩到 5000 条，覆盖运维/低代码/AI 可解释性 | 2026.8 下旬 | P1 |
| P1-5 | 文档体系完善 | UNIQUENESS.md、ARCHITECTURE.md、SECURITY.md | 2026.9 上旬 | P1 |
| P1-6 | 测试覆盖度提升 | 56/56 → 80/80，新增 LoRA/adapter 回滚/语义缓存专项测试 | 2026.9 下旬 | P1 |

### 第二阶段：生态工具铺量（2026.10-2027.3）

| 编号 | 任务 | 交付物 | 时间 | 优先级 |
|------|------|--------|------|--------|
| P2-1 | VSCode 插件 MVP 发布 | 解释逻辑/悬停卦象/侧边栏可视化 | 2026.11 | **P0** |
| P2-2 | HexLang Rule Studio Alpha | 拖拽式规则编排、卦象流转可视化、4 语言代码生成 | 2027.1 | **P0** |
| P2-3 | 语义缓存 API 开放 | 本地 HTTP 接口、缓存命中逻辑、Qwen 调用降 50% | 2027.2 | P1 |
| P2-4 | 仪表盘企业版 | 多集群监控、卦象流转趋势图、故障排查 Checklist | 2027.3 | P1 |
| P2-5 | 社区贡献引导 | PR 模板、Issue 标签体系、贡献者指南、2-3 名核心开发者 | 2027.3 | P2 |

### 第三阶段：商业化验证（2027.4-2027.9）

| 编号 | 任务 | 交付物 | 时间 | 优先级 |
|------|------|--------|------|--------|
| P3-1 | 第一个企业咨询订单 | 中小厂 Hex64 接入 POC、收款 3-5 万 | 2027.4 | **P0** |
| P3-2 | 企业版 License | 年费制（小团队 999/年、中企业 4999/年）| 2027.5 | **P0** |
| P3-3 | Adapter 商店上线 | 场景化预训适配器（ops/fintech/lowcode），99-199/月 | 2027.6 | P1 |
| P3-4 | 特征 API SaaS 开放 | 0.5 元/千次，免费 1 万次/月 | 2027.7 | P1 |
| P3-5 | 商标注册申请 | HexLang 文字 + Logo 商标 | 2027.8 | P2 |

### 第四阶段：长期壁垒构建（2027.10-2027.12）

| 编号 | 任务 | 交付物 | 时间 | 优先级 |
|------|------|--------|------|--------|
| P4-1 | 学术背书获取 | 技术白皮书、AI 工程化会议分享 | 2027.10 | P1 |
| P4-2 | 社区生态成熟 | 10+ 贡献者、5+ 第三方插件、100+ 模板 | 2027.11 | P1 |
| P4-3 | 大厂合作试探 | 向阿里/腾讯/字节输出方案 | 2027.12 | P2 |
| P4-4 | v2.0 发布 | 更多道门计算模式、LoRA 效率优化、适配 Qwen 下一代 | 2027.12 | P2 |

### 关键里程碑

| 时间 | 里程碑 | 意义 |
|------|--------|------|
| 2026.7 下旬 | 跑通 QLoRA 训练，产出 v1 适配器 | 核心自进化链路闭环 |
| 2026.9 下旬 | 合规防护落地，文档体系完善 | 全球唯一性确立 |
| 2026.11 | VSCode 插件发布 | 生态工具落地 |
| 2027.1 | Rule Studio Alpha 发布 | 低代码场景打通 |
| 2027.4 | 第一个企业订单 | 商业化零的突破 |
| 2027.8 | Adapter 商店上线 | 规模化变现开始 |
| 2027.12 | 商标注册完成，v2.0 发布 | 长期壁垒成型 |

### 资源需求

| 资源 | 现有情况 | 年成本 |
|------|---------|--------|
| 硬件 | RTX 4080S 16G、个人 PC | 0 |
| 软件 | Python/Node/VSCode、Ollama、GitHub | 0 |
| 数据 | 2002 条训练数据 → 5000 条（feedback 自动积累）| 0 |
| 人力 | 个人全职/兼职 | 0 |
| 资金 | 商标注册 + 服务器 | ≈ 4000 元/年 |

### 风险预案

| 风险 | 应对 |
|------|------|
| 训练不收敛 | 回滚上一版 adapter，lr 降到 1e-4，batch=2，warmup=50 |
| 被人 Fork 换皮商用 | DMCA 投诉 + 公开 Timeline 证据链 + 社区舆论 |
| 半年无企业订单 | 接零散 AI 咨询单（500-1000/单），靠免费 API 维持 |
| 大厂推出竞品 | 强调邵雍先天序 + 工程语义标签唯一性，每月迭代，社区粘性 |
| 社区贡献者流失 | 定期发进展、署名权、开放小模块维护权、建立社群 |
