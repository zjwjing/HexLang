# CONTRIBUTING.md — HexLang 协作规范

欢迎贡献！本文档说明如何参与 HexLang 项目开发。

---

## 项目定位

Hex64 是一个**确定性符号编码基础设施**，将邵雍先天六十四卦与二进制逻辑进行工程化映射。

**核心原则：**
- 所有运算逻辑完全 deterministic（确定性）
- 非玄学工具，纯计算机科学/符号学研究
- 数据与代码严格分离

---

## 模块结构

```
HexLang/
├── src/                    # 源代码
│   ├── core.js             # 核心引擎（Hex64Engine 类）
│   ├── database.js         # 数据库加载器（从 JSON 读取）
│   └── engine.html         # 浏览器演示 + HexLang 编译器
├── data/                   # 数据层（只读，由数据负责人维护）
│   ├── hex64_full.json     # 64卦完整数据 + tagToOp 映射表
│   └── hexagrams.json      # 备用数据
├── bin/                    # CLI 工具（扩展中）
├── examples/               # 使用示例（待建设）
└── docs/                   # 技术文档（待建设）
```

---

## 贡献方式

### 1. Bug 修复

```
1. Fork 本仓库
2. 在 issue 中描述 bug 和复现步骤
3. 提交 PR，附上测试用例
4. 首席架构师 @zjwjing 审核合并
```

### 2. 新功能

新功能需要先在 issue 中讨论方案，确认后再动手。按模块提交：

| 模块 | 负责人 | 提交目标 |
|------|--------|---------|
| 核心引擎 | @zjwjing | `src/core.js` |
| 浏览器前端 | @zjwjing | `src/engine.html` |
| 数据层 | @zjwjing | `data/hex64_full.json` |
| 扩展接口 | @ExtensionOwner | `examples/` 或 `bin/` |

### 3. 文档

文档 PR 可以直接提交，格式遵循 Markdown 规范。

---

## 开发环境

### 前置条件

- **Node.js** >= 18.0.0 （推荐 20+）
- **浏览器** 任意现代浏览器（Chrome/Firefox/Edge）
- **Git** 版本控制

### 本地运行

```bash
# Node.js 环境
node src/core.js

# 浏览器环境
# 双击 src/engine.html 或直接打开
```

### 开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/your-feature-name

# 2. 修改代码（遵守模块边界）

# 3. 验证功能
node src/core.js          # 确保核心引擎仍正常运行
# 浏览器打开 src/engine.html 测试前端

# 4. 提交
git commit -m "feat: add xxx"
git push origin feature/your-feature-name

# 5. 提交 PR
```

---

## 代码规范

### 命名约定

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | kebab-case | `core.js`, `database.js` |
| 类名 | PascalCase | `Hex64Engine` |
| 函数名 | camelCase | `featureVector()`, `lookup()` |
| 常量 | UPPER_SNAKE | `HEXAGRAMS`, `TAG_TO_OP` |
| 卦名 | 中文全称 | `泽水困`, `乾为天` |

### 数据层规范

**重要：** `data/hex64_full.json` 是唯一数据源，所有模块从这里读取。

修改数据时必须同步更新：
1. `src/database.js` — 如果导出版本号变化
2. `src/engine.html` — 如果 API 变化
3. `README.md` — 如果数据结构变化

### 代码风格

- **ESM only** — 全部使用 `import/export`，不使用 `require()`
- **无框架依赖** — 前端使用 Vanilla JS
- **注释语言** — 中文为主，技术术语可用英文
- **每文件顶部** — 简短说明文件职责

---

## 任务管理

### 任务卡系统

任务卡存放在个人助理工作区：
```
C:/Users/zjwji/.bitfun/personal_assistant/workspace/.tasks/
```

命名格式：`task-YYYYMMDD-序号.md`

### 任务状态

| 状态 | 含义 |
|------|------|
| `pending` | 待启动 |
| `in-progress` | 进行中 |
| `paused` | 暂停（有明确断点） |
| `completed` | 已完成 |
| `blocked` | 阻塞（需外部介入） |

### 跨平台接力

本项目支持多 AI 平台协作：

| 平台 | 代号 | 适用场景 |
|------|------|---------|
| WorkBuddy | WB | 主要开发 |
| Codex | CX | 专项任务 |
| QoderWork | QW | 前端/UI |
| ClaudeCode | CC | 代码审查 |

接力时需在任务卡中更新：
- `🔄 最后更新` 时间
- `👤 负责人`
- `🔗 来源平台`
- `⏸️ 断点位置`

---

## Issue 模板

### Bug Report

```markdown
**描述**
清晰简洁地描述 bug

**复现步骤**
1. 运行 '...'
2. 输入 '...'
3. 看到错误 '...'

**预期行为**
应该发生什么

**环境**
- Node.js 版本: 
- 操作系统: 
- 浏览器: 
```

### Feature Request

```markdown
**功能描述**
这个功能做什么

**使用场景**
在什么情况下需要这个功能

**替代方案**
考虑过哪些替代方案
```

---

## PR 规范

### 标题格式

```
[type]: 简短描述
```

type 枚举：`feat` / `fix` / `docs` / `refactor` / `test` / `chore`

### 视觉前缀（可选）

可以使用八卦 Unicode 符号作为 commit 前缀，增加可读性：

```
[☰] feat: 添加乾卦相关功能
[☷] fix: 修复坤卦映射错误
[☲] docs: 更新离卦可视化文档
[☳] chore: 触发构建流程
```

符号说明：☰乾 ☱兑 ☲离 ☳震 ☴巽 ☵坎 ☶艮 ☷坤

### 正文要求

- 说明改了什么
- 为什么改
- 影响了哪些模块
- 是否有破坏性变更

### 合并检查清单

- [ ] 代码通过 `node src/core.js` 验证
- [ ] 浏览器测试通过
- [ ] 数据文件与代码同步更新
- [ ] README 如有变化已更新
- [ ] PR 标题符合格式规范

---

## 版本发布

```bash
# 版本号格式: MAJOR.MINOR.PATCH
# 示例: 1.0.0 → 1.1.0 → 2.0.0

# 发布流程
1. 更新 package.json version
2. 更新 README.md 版本号
3. git tag v1.x.x
4. git push origin master --tags
5. 发布到 GitHub + CNB 双仓库
```

---

## 联系方式

- **项目地址**: https://github.com/zjwjing/HexLang
- **Issues**: https://github.com/zjwjing/HexLang/issues
- **Author**: zjwjing

---

*感谢你的贡献！*
