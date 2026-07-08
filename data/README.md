# data/ — 数据层

Hex64 项目的唯一数据源，只读模块。

---

## 数据文件

| 文件 | 版本 | 说明 | 负责人 |
|------|------|------|--------|
| `hex64_full.json` | 1.2.0 | 64卦完整数据 + tagToOp 映射表 | @zjwjing |
| `hexagrams.json` | - | 备用数据 | @zjwjing |

---

## hex64_full.json 结构

```json
{
  "description": "...",
  "version": "1.2.0",
  "notes": "64个唯一分类标签...",
  "tagToOp": { ... },     // 166条标签→操作码映射
  "hexagrams": [ ... ]    // 64卦完整数据
}
```

### hexagrams 数组每项

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `bin` | string | 6位二进制（阴=0，阳=1） | `"010110"` |
| `name` | string | 中文卦名 | `"泽水困"` |
| `pinyin` | string | 拼音 | `"zé shuǐ kùn"` |
| `en` | string | 英文翻译 | `"Oppression"` |
| `category` | string | 功能分类 | `"风险/困境"` |
| `tags` | string[] | 语义标签 | `["困境", "困顿", "穷困", "死锁"]` |
| `weight` | number | 数值权重 0.0-1.0 | `0.2` |

### tagToOp 映射表

标签到操作码的字典映射，用于生成伪代码和 HexLang 编译器输出。

当前共 **166条** 映射，覆盖：
- 系统操作（INIT/RUN/STOP/REBOOT）
- 数据处理（LOAD/SAVE/CACHE/ENCODE）
- 并发控制（LOCK/UNLOCK/SUSPEND/SYNC）
- 网络通信（CONNECT/DISCONNECT/BROADCAST）
- AI/ML（TRAIN/LEARN/EVAL/RECURSE）
- 运维（MONITOR/DEPLOY/MIGRATE/BACKUP）

---

## 数据变更规则

修改 `hex64_full.json` 后需要同步更新：

1. ✅ 递增 `version` 字段
2. ✅ 检查 `bin` 字段与先天六十四卦顺序一致
3. ✅ 通知 `src/database.js` 维护者（如有接口变化）
4. ✅ 更新 `TASKS.md` 模块健康度
5. ✅ 如有新增 tag，检查 `tagToOp` 是否覆盖

---

## 数据完整性校验

64卦必须覆盖以下范围：

- `bin` 值：`000000` ~ `111111`（无重复）
- `category` 值：63+ 个唯一分类
- `weight` 范围：0.0 ~ 1.0
- `tags` 非空
