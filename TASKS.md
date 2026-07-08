# TASKS.md — HexLang 任务看板

> 详细任务卡存放在个人助理工作区：
> `C:/Users/zjwji/.bitfun/personal_assistant/workspace/.tasks/`
>
> 本文件为高层任务总览，快速了解项目当前状态。

---

## 活跃任务

无活跃任务。

## 已完成任务

| 编号 | 任务 | 完成时间 | 负责人 | 来源 |
|------|------|---------|--------|------|
| 007 | Hex64 代码审计与修缮 | 2026-07-08 | 朵朵 | ClaudeCode |

## 模块健康度

| 模块 | 状态 | 备注 |
|------|------|------|
| `src/core.js` + `core.d.ts` | 🟢 正常 | 引擎 + TS 类型定义 |
| `src/database.js` + `database.d.ts` | 🟢 正常 | 数据层 + TS 类型定义 |
| `src/engine.html` | 🟢 正常 | 浏览器 demo（暗色模式、复制、分享URL、编译器） |
| `src/core.test.js` | 🟢 正常 | 22 个测试覆盖全部引擎 API |
| `data/hex64_full.json` | 🟢 正常 | v1.2.0，64 卦 + 443 tagToOp |
| `bin/hex64.js` | 🟢 正常 | CLI 工具（ANSI 输出、JSON 模式、--op） |
| `bin/audit.mjs` | 🟢 正常 | 审计脚本（8 项检查） |
| `package.json` | 🟢 正常 | exports/types/engines/bin 完善 |
| `.gitignore` | 🟢 正常 | 完善（IDE/OS/build/log） |
| `.github/workflows/ci.yml` | 🟢 正常 | CI (Node 18/20/22) |
| `examples/` | 🟢 正常 | basic-usage.js, engine-api.js |
| `README.md` | 🟢 正常 | 已更新到最新数据结构 |

## 审计摘要 (2026-07-08)

| 检查项 | 结果 |
|--------|------|
| tagToOp 覆盖率 | ✅ 343/343（100%） |
| 数据一致性 | ✅ hex64_full.json = hexagrams.json |
| 每卦标签数 | ✅ 全部 6 个 |
| 重复检测 | ✅ 无重复 bin/卦名 |
| 引擎功能测试 | ✅ 6/6 通过 |
| engine.html 特性 | ✅ 全部 7 项 |
| CLI 工具 | ✅ 存在 + shebang |
| opTemplates 自定义模板 | ⚠️ 229/381 opcodes 有自定义模板，其余使用通用 fallback |
