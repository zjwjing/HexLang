# TASKS.md — HexLang 任务看板

> 详细任务卡存放在个人助理工作区：
> `C:/Users/zjwji/.bitfun/personal_assistant/workspace/.tasks/`
>
> 本文件为高层任务总览，快速了解项目当前状态。

---

## 活跃任务

| 编号 | 任务 | 状态 | 优先级 | 负责人 | 来源 | 关联任务卡 |
|------|------|------|--------|--------|------|-----------|
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

## 模块健康度

| 模块 | 状态 | 备注 |
|------|------|------|
| `src/core.js` | 🟢 正常 | 引擎核心：O(1) binIndex、encodeSeeded、7种运算 + 方图/爻辰/禹步 |
| `src/compiler.js` | 🟢 正常 | 共享编译逻辑（compileHex），4语言输出 |
| `src/templates.js` | 🟢 正常 | 384条模板（单一数据源，build script 生成）|
| `src/database.js` | 🟢 正常 | 数据层（HEXAGRAMS + TAG_TO_OP）|
| `src/taixuan.js` | 🟢 正常 | 太玄三进制编码（81首+729赞）|
| `src/yuanhui.js` | 🟢 正常 | 元会运世四层嵌套计数器 |
| `src/compile.test.js` | 🟢 正常 | 8个编译测试（4语言覆盖）|
| `src/core.test.js` | 🟢 正常 | 48个引擎测试（含方图/爻辰/禹步/encodeSeeded）|
| `src/engine.html` | 🟢 正常 | 浏览器 Demo：2×2编译器网格、7种运算、暗色模式 |
| `data/hex64_full.json` | 🟢 正常 | v1.2.0，64卦 + 443 tagToOp + yao_weights + hex_font + english |
| `bin/hex64.js` | 🟢 正常 | CLI：先天八卦 LOGO、4语言彩色输出、JSON 模式 |
| `scripts/rebuild-templates.mjs` | 🟢 正常 | 构建脚本：从 templates.js 读取，生成 rs/go |
| `.github/workflows/ci.yml` | 🟢 正常 | CI (Node 18/20/22) |
| `README.md` | 🟢 正常 | 含 Related Work 生态定位、运算规则表（含互卦）|

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
