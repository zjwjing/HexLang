# TASKS.md — HexLang 任务看板

> 详细任务卡存放在个人助理工作区：
> `C:/Users/zjwji/.bitfun/personal_assistant/workspace/.tasks/`
>
> 本文件为高层任务总览，快速了解项目当前状态。

---

## 活跃任务

| 编号 | 任务 | 状态 | 优先级 | 负责人 | 来源 | 关联任务卡 |
|------|------|------|--------|--------|------|-----------|
| 007 | Hex64 代码审计与修缮 | 🟡 pending | 中 | 朵朵 | ClaudeCode | [task-20260708-007.md](.tasks/task-20260708-007.md) |

## 已完成任务

| 编号 | 任务 | 完成时间 | 负责人 | 来源 |
|------|------|---------|--------|------|
| 001 | 建立跨会话任务追踪系统 | 2026-07-04 | 朵朵 | WorkBuddy |
| 002 | PDF族谱OCR识别与数据表格生成 | 2026-07-05 | 朵朵 | WorkBuddy |
| 003 | 股票模拟操盘系统 | 🟠 in-progress | 朵朵 | WorkBuddy |
| 004 | 朱氏族谱 OCR 搜索库与权限页面 | 2026-07-07 | Codex | Codex |
| 005 | 朱氏族谱网站（浏览+搜索+管理后台） | 2026-07-07 | 朵朵 | QoderWork |
| 006 | ComfyUI MCP 安装配置 + 抖音视频制作 | 🟠 in-progress | 意好/朵朵 | WorkBuddy |

## 待办任务

| 优先级 | 任务 | 所属模块 | 预估工作量 |
|--------|------|---------|-----------|
| P0 | 修复 README 文档不一致 | docs | 30min |
| P0 | 创建 examples/ 目录 + 基础示例 | core | 1h |
| P1 | 修复 CLI 自执行检测路径兼容性 | core | 1h |
| P1 | 添加真实测试套件（assert） | test | 2h |
| P1 | 完善 package.json exports/files | package | 30min |
| P2 | 添加 .d.ts 类型定义 | types | 2h |
| P2 | 配置 GitHub Actions CI | ci | 1h |
| P2 | 完善 .gitignore | chore | 15min |

---

## 模块健康度

| 模块 | 状态 | 最近更新时间 | 备注 |
|------|------|-------------|------|
| `src/core.js` | 🟢 正常 | 2026-07-08 | 核心引擎稳定 |
| `src/database.js` | 🟢 正常 | 2026-07-08 | 重构完成，统一数据源 |
| `src/engine.html` | 🟢 正常 | 2026-07-08 | 新增 HexLang 编译器 |
| `data/hex64_full.json` | 🟢 正常 | 2026-07-08 | v1.2.0，166条 tagToOp |
| `README.md` | 🟡 需更新 | - | 示例过时，缺字段 |
| `package.json` | 🟡 需更新 | - | 缺 exports/files |
| `.gitignore` | 🟡 需完善 | - | 缺 package-lock.json |

---

## 任务卡索引

详细任务卡按日期命名，存放在 `.tasks/` 目录：

```
.tasks/
├── _TEMPLATE.md                 # 新任务模板
├── task-20260702-001.md         # 任务追踪系统（已完成）
├── task-20260702-002.md         # PDF族谱OCR（已完成）
├── task-20260703-003.md         # 股票模拟（进行中）
├── task-20260703-004.md         # OCR搜索库（已完成）
├── task-20260703-005.md         # 族谱网站（已完成）
├── task-20260705-006.md         # ComfyUI视频（进行中）
├── task-20260708-007.md         # HexLang审计（待启动）← 当前任务
```
