---
name: intent-critique
description: Critical review of Intent design quality. Checks for over-engineering, YAGNI violations, premature abstraction, and simplification opportunities. Uses interactive discussion to refine design decisions.
---

# Intent Critique

设计质量的批判性审查。不检查格式，只检查"是否该这么设计"。

## 核心问题

每次 critique 回答一个问题：**这个设计能更简单吗？**

## Anti-Accretion Rule: 净减

**Critique 后总行数必须 ≤ 之前。** 这是硬约束，不是建议。

Critique 只允许 4 种操作：

| 操作 | 说明 | 示例 |
|------|------|------|
| **删除** | 移除 section 或内容 | 删除未使用的插件系统设计 |
| **合并** | 多个 section 合为一个 | 将 Error Handling 合入 API Constraints |
| **拆分** | 移到独立 intent | §13-§18 从 ash 拆为 ash/agentic-patterns |
| **简化** | 用更少的行表达相同约束 | 5 行描述压缩为 2 行 |

**禁止：**
- ❌ 引入新概念或新 section
- ❌ 添加新分析框架
- ❌ 扩展现有 section 的范围

如果发现缺了什么，输出 gap flag，不直接填充：

```
Gap: intent 没有说明 failure handling。建议在下一轮 interview 中讨论。
```

如果确实需要加新内容，必须：
1. 先删等量或更多旧内容
2. 用户明确同意
3. 最终行数仍然 ≤ 初始行数

## 检查维度

| 维度 | 信号 | 问题 |
|------|------|------|
| **Over-engineering** | 复杂的配置系统、插件架构、多层抽象 | "这个复杂度是当前需求驱动的吗？" |
| **YAGNI** | "未来可能需要"、"预留扩展点"、"支持多种..." | "删掉这个，MVP 还能工作吗？" |
| **过早抽象** | 只有一个实现的接口、只用一次的工具函数 | "现在真的需要这层抽象吗？" |
| **边界问题** | 模块间大量数据传递、循环依赖、职责模糊 | "这个边界切在这里自然吗？" |
| **隐藏复杂度** | 看似简单但实现困难的描述 | "这句话背后的实现复杂度是什么？" |

## 工作流程

```
/intent-critique [path]
        ↓
┌───────────────────┐
│  读取 Intent 文件  │
│  理解设计意图      │
└─────────┬─────────┘
          ↓
┌───────────────────┐
│  逐维度分析        │
│  识别可疑设计      │
└─────────┬─────────┘
          ↓
┌───────────────────────────────────────┐
│  对每个发现，与用户讨论：              │
│                                       │
│  展示问题 + 简化建议                   │
│  AskUserQuestion:                     │
│  - 接受简化                           │
│  - 保留原设计（说明理由）              │
│  - 跳过此项                           │
└─────────┬─────────────────────────────┘
          ↓
┌───────────────────┐
│  汇总 critique     │
│  可选更新 Intent   │
└───────────────────┘
```

## 使用方法

```bash
# 审查指定 Intent
/intent-critique src/core/intent/INTENT.md

# 审查当前目录
/intent-critique

# 只分析不修改
/intent-critique --dry-run
```

## 执行步骤

### 0. 记录初始行数

**第一步必须是计数。** 在任何分析之前：

```bash
wc -l INTENT.md
# 记录为 before_lines
```

将 `before_lines` 记录下来，critique 结束时用于验证净减。

### 0.5 Convergence Check（修改 ≥ 3 次时自动触发）

检查 git log 中 INTENT.md 的提交次数。如果 ≥ 3 次，在正常 critique 之前先跑 convergence：

**4 步 convergence 检查：**

1. **Anchor trace** — 对每个 section 问：能追溯到 anchor 吗？
   - 不能 → 标记为候选删除

2. **Implementation match** — 对每个 section 问：有对应的实现吗？
   - 有实现 → 保留
   - 没实现且不在 plan 里 → 标记为候选删除

3. **Constraint vs Analysis** — 对每个 section 问：这是约束还是分析？
   - "Three Dimensions of Chat Experience" = 分析 → 精简或移到 appendix
   - "INV-1: LLM is a Pure Function" = 约束 → 保留

4. **Dedup with sub-intents** — 有 section 跟子 intent 重复吗？
   - 有 → 删掉，留一个链接

**Convergence 输出格式：**

```markdown
## Convergence Check (triggered: 5 commits since last convergence)

### Anchor trace failures
- § Agentic Pattern Zones — cannot trace to "ASH 是 shell 语言"
- § Echo Deprecation — migration plan, not core spec

### Unimplemented sections
- § Template Registry — no code, not in plan

### Analysis (not constraint)
- § AI Agent 适配性分析 — 40 lines of analysis, 0 constraints

### Duplicated in sub-intents
- § Boot Sequence — duplicates kernel/bootloader INTENT.md §2

→ Candidates for removal: 4 sections, ~280 lines
```

跑完 convergence 后，进入正常 critique 流程。

### 0.7 读取 Records 索引

如果 `records/INDEX.md` 存在，先读取索引了解完整决策上下文：

- 哪些 interview 做过哪些决策
- 其他 AI（ChatGPT、Gemini 等）给过什么 review 意见
- 之前的 critique 记录

按需深入读取相关 record 文件。这解决了 context asymmetry —— 即使原始讨论发生在其他 AI 上，这里也有完整记录。

### 0.8 Devil's Advocate（独立评估）

起一个**不带当前讨论 context 的 subagent**，只给它：
- INTENT.md 全文
- Anchor 声明

让它独立回答 3 个问题：
1. 这个 intent 最大的设计风险是什么？
2. 哪些 section 看起来像分析而非约束？
3. 如果只能保留 3 个 section，你保留哪些？

将 devil's advocate 的输出作为 critique 的额外输入，不直接采纳但用于交叉验证自己的判断。

### 1. 读取并理解 Intent

先完整阅读 Intent，理解：
- 要解决什么问题
- 核心设计决策
- 主要组件和边界

### 2. 逐维度扫描

#### Over-engineering 信号

```markdown
检查是否存在：
- 可配置的部分 > 3 个
- 插件/扩展机制
- 多于 2 层的抽象
- "支持多种 X"的描述
- 复杂的状态机
```

#### YAGNI 信号

```markdown
检查是否存在：
- "未来可能..."
- "预留..."
- "方便以后..."
- 只在"高级场景"使用的功能
- 没有具体 use case 的抽象
```

#### 过早抽象信号

```markdown
检查是否存在：
- 只有一个实现的接口/协议
- 只用一次的公共函数
- 只有一个子类的基类
- 不必要的工厂/策略模式
```

#### 边界问题信号

```markdown
检查是否存在：
- 模块间传递 > 5 个参数
- A 依赖 B，B 也依赖 A
- 一个改动需要同时改多个模块
- 职责描述模糊或重叠
```

### 3. 生成发现列表

对每个发现，准备：
- **位置**：Intent 中的具体 section
- **问题**：简短描述问题
- **简化建议**：具体的替代方案
- **风险**：简化可能带来的代价

### 4. 交互式讨论

对每个发现使用 AskUserQuestion：

```
发现 1/N: Over-engineering

Section: ## 插件系统
问题: 定义了完整的插件加载、生命周期、沙箱机制，但目前只有 2 个内置功能。

简化建议: 删除插件系统，直接硬编码这 2 个功能。
未来需要时再加。

风险: 如果很快需要第三方插件，要重新设计。

---
AskUserQuestion:
- question: "是否接受这个简化？"
- options:
  - "接受简化" - 删除插件系统设计
  - "保留原设计" - 请说明具体场景
  - "跳过" - 暂不决定
```

### 5. 汇总报告

```markdown
# Intent Critique Report

## 文件: src/core/intent/INTENT.md

## 统计
- 发现问题: 5
- 接受简化: 3
- 保留原设计: 1
- 跳过: 1

## 已接受的简化

### 1. 删除插件系统
- 原设计: 完整插件架构
- 简化为: 硬编码 2 个功能
- 影响 sections: ## 插件系统, ## 架构

### 2. 合并配置层
...

## 保留的设计

### 1. 多数据源支持
- 原因: 用户明确表示 v1.1 需要
- 建议: 在 Intent 中标注具体 timeline

## 跳过的项目
...

## 下一步
- [ ] 更新 Intent 文件（如果选择自动更新）
- [ ] 运行 /intent-validate 检查格式
- [ ] 运行 /intent-review 重新审批受影响的 sections
```

### 6. 可选：更新 Intent

如果用户同意，自动更新 Intent：
- 删除被简化掉的 sections
- 添加简化说明到变更记录
- 将受影响的 sections 标记回 `draft`

### 7. 验证净减（必须）

更新 Intent 后，立即验证：

```bash
wc -l INTENT.md
# 记录为 after_lines
```

**判定规则：**

```
if after_lines > before_lines:
    ❌ 拒绝保存。回滚更改。
    报告：
      before: {before_lines} lines
      after:  {after_lines} lines
      delta:  +{after_lines - before_lines} lines
      "Critique must net-reduce. Review changes and remove additions."

if after_lines <= before_lines:
    ✅ 保存成功。
    报告：
      before: {before_lines} lines
      after:  {after_lines} lines
      reduced: {before_lines - after_lines} lines ({percentage}%)
```

### 8. 保存 Critique 记录

将完整 critique 报告保存到 `records/critique-{date}.md`，更新 `records/INDEX.md`：

```markdown
| 2026-02-06 | critique | — | Convergence + critique, removed §13-§15 (-180 lines), kept §2 |
```

记录包含：convergence 结果、devil's advocate 输出、每个发现的决策、净行数变化。

## 讨论技巧

### 提问方式

**好的提问**:
- "删掉 X，系统还能工作吗？"
- "有没有具体场景需要 X？"
- "X 的复杂度值得吗？"

**避免**:
- 预设答案
- 过于理论化的讨论
- 同时问多个不相关的问题

### 接受"保留"的时机

当用户提供：
- 具体的使用场景
- 明确的时间线（"下月就要"）
- 外部约束（"合作方要求"）

记录理由，建议在 Intent 中也注明。

## 与其他工具配合

```
intent-interview → intent-validate → intent-critique → intent-review
                                          ↑
                                     可独立调用
                                     任何时候想反思设计时
```

## 不做什么

- ❌ 不检查格式（intent-validate 的职责）
- ❌ 不检查一致性（intent-sync 的职责）
- ❌ 不标记审批状态（intent-review 的职责）
- ❌ 不自动做决定（必须与用户讨论）
