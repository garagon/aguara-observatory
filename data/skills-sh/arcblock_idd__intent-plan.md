---
name: intent-plan
description: Transform approved Intent into executable phased plan with strict TDD. Each step requires tests first (happy/bad/edge/security cases), then implementation. Use after /intent-review when ready to start development.
---

# Intent Plan

Transform an approved Intent into a structured, executable development plan with strict TDD discipline.

**Output is TaskSwarm-compatible**: The generated plan.md can be directly executed by `/swarm run`.

## Core Principles

1. **Test First, Always**: Every implementation step starts with writing tests
2. **Phased Execution**: Break work into phases with clear deliverables (0-indexed)
3. **Verification Gates**: Each phase ends with e2e validation
4. **Automation Priority**: Prefer CLI/script testing over manual/browser testing
5. **Checkbox Tracking**: All tests use `- [ ]` format for progress tracking

## Plan Structure

```
## Phase 0: [Phase Name]
├── ### Description
├── ### Tests
│   ├── #### Happy Path
│   │   └── - [ ] test case 1
│   ├── #### Bad Path (详尽列举)
│   │   └── - [ ] error case 1
│   ├── #### Edge Cases
│   │   └── - [ ] boundary case 1
│   ├── #### Security
│   │   └── - [ ] vulnerability test 1
│   ├── #### Data Leak
│   │   └── - [ ] leak prevention test 1
│   └── #### Data Damage
│       └── - [ ] integrity test 1
├── ### E2E Gate
│   └── CLI/Script 验证命令
└── ### Acceptance Criteria
    └── - [ ] criterion 1

## Phase 1: [Phase Name]
└── ...
```

## Test Categories (6 Required)

**Every phase MUST include tests from ALL 6 categories:**

| Category | Description | Examples |
|----------|-------------|----------|
| **Happy Path** | Normal expected usage | Valid inputs, correct sequences |
| **Bad Path** | Invalid inputs, error conditions | Wrong types, missing required fields, invalid states |
| **Edge Cases** | Boundary conditions | Empty inputs, max values, concurrent access |
| **Security** | Vulnerability prevention | Injection attacks, auth bypass, privilege escalation |
| **Data Leak** | Information exposure | Sensitive data in logs, error messages, API responses |
| **Data Damage** | Data integrity protection | Partial writes, corruption, race conditions |

**Bad cases must be detailed and comprehensive.** A good test suite has more failure tests than success tests.

### Test Writing Discipline

1. **Tests First**: Write ALL tests before any implementation
2. **Red-Green-Refactor**: Run tests expecting failure, implement, verify pass
3. **No Skip**: Every category must have at least one test case

## Phase Gates: E2E Verification (Required)

**Each phase MUST end with E2E verification.** This is the gate that proves the phase is truly complete.

### E2E Gate Requirements

1. **Automatable**: Must be runnable via CLI/script, no manual steps
2. **Independent**: Can run without human intervention
3. **Reproducible**: Same inputs produce same outputs
4. **Fast Feedback**: Fails quickly when something is wrong

### Preferred: CLI/Script Testing
```bash
# Example: API verification
curl -X POST http://localhost:3000/api/resource \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}' | jq .

# Example: Database state check
psql -c "SELECT * FROM table WHERE condition"

# Example: File system verification
diff expected_output.json actual_output.json

# Example: Unit test suite
pnpm test -- --coverage
```

### For Web Projects: Automation-Friendly Design

```
DO:
- Provide health check endpoints
- Return machine-parseable responses (JSON)
- Include test mode / seed data endpoints
- Design idempotent operations

DON'T:
- Require browser interaction for verification
- Depend on visual inspection
- Need manual clicking through UI
```

### When Browser Testing is Unavoidable

If browser/headless testing is truly necessary:
- Use Playwright/Puppeteer with script automation
- Create dedicated test endpoints
- Prefer API calls over UI interaction

## Pre-Plan Gates (Mandatory)

**Before generating any plan, ALL gates must pass. No exceptions.**

```
/intent-plan
    ↓
┌─────────────────────────────────────┐
│ Gate 1: Interview Check             │
│   ✗ → "先跑 /intent-interview"       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Gate 2: Critique Check              │
│   ✗ → "先跑 /intent-critique"        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Gate 3: Dependency Check            │
│   ✗ → "前置任务未完成，无法 plan"    │
└─────────────────────────────────────┘
    ↓
✓ All gates passed → Generate plan.md
```

### Gate 1: Interview Check

Verify the Intent has been properly interviewed:

| Check | How to Verify | If Failed |
|-------|---------------|-----------|
| INTENT.md exists | File exists in intent directory | Run `/intent-interview` |
| Anchor exists | First blockquote after title starts with `>` | Add anchor statement |
| Within budget | `wc -l INTENT.md` ≤ 500 (warning at 300) | Run `/intent-critique` to reduce if > 500 |
| Structure complete | Has Responsibilities, Structure, API sections | Run `/intent-interview` |
| Not a stub | Content is substantial, not placeholder text | Run `/intent-interview` |

**Output if failed:**
```
❌ Gate 1 Failed: Interview Incomplete

INTENT.md is missing or incomplete:
- [ ] Responsibilities section missing
- [ ] Structure diagram missing

Action required: Run /intent-interview first.
```

### Gate 2: Critique Check

Verify the Intent has been critiqued for over-engineering:

| Check | How to Verify | If Failed |
|-------|---------------|-----------|
| Critique done | Look for critique markers or changelog | Run `/intent-critique` |
| Post-modification | If INTENT.md modified after last critique | Run `/intent-critique` again |
| AI assessment | Ask AI if another critique round is needed | Run `/intent-critique` if yes |

**Critique markers to look for:**
- `<!-- critique: {date} -->` comment in INTENT.md
- `critique.md` or `CRITIQUE.md` in same directory
- Changelog entry mentioning critique

**Post-modification detection:**
- Compare INTENT.md mtime with critique marker date
- If INTENT.md is newer AND has substantial changes → re-critique required

**AI Assessment prompt:**
> "Based on this Intent, is there any sign of over-engineering, premature abstraction, or YAGNI violation that warrants another critique round?"

**Output if failed:**
```
❌ Gate 2 Failed: Critique Required

Intent has not been critiqued, or was modified after critique:
- Last critique: 2026-01-15
- INTENT.md modified: 2026-01-20 (substantial changes detected)

Action required: Run /intent-critique to review for over-engineering.
```

### Gate 3: Dependency Check

Verify all prerequisites are satisfied:

| Check | How to Verify | If Failed |
|-------|---------------|-----------|
| Internal deps | Referenced intents have `status: done` in TASK.yaml | List blocking intents |
| External deps | Required packages/services exist | List missing dependencies |
| Environment | Required env vars, credentials, access | List missing setup |

**How to find dependencies:**
1. Parse `## Prerequisites` or `## Dependencies` in INTENT.md
2. Look for `depends_on:` in TASK.yaml (if exists)
3. Scan for references like `intent/other-feature/` or `@package/name`

**Dependency states:**
```
intent/auth/         → TASK.yaml status: done     ✓ OK
intent/database/     → TASK.yaml status: review   ✗ Blocked (not done)
intent/api/          → No TASK.yaml               ? Assume not started
@aigne/afs           → Check packages/ or deps    ✓/✗
```

**Output if failed:**
```
❌ Gate 3 Failed: Dependencies Not Ready

This Intent cannot be planned because prerequisites are incomplete:

Blocking Intents:
- intent/auth-module/ → status: in_progress (need: done)
- intent/database-setup/ → status: ready (need: done)

Missing External Dependencies:
- @aigne/session-protocol → not found in packages/

Action required: Complete blocking tasks first, or remove dependencies from INTENT.md if not actually needed.
```

### Gate Pass Output

When all gates pass:
```
✓ Gate 1: Interview complete
✓ Gate 2: Critique done (2026-01-20), no re-critique needed
✓ Gate 3: All 2 dependencies satisfied

Proceeding to generate plan...
```

## Workflow

```
/intent-plan
    ↓
Gate 1: Interview Check ──→ ✗ → Stop, require /intent-interview
    ↓ ✓
Gate 2: Critique Check ───→ ✗ → Stop, require /intent-critique
    ↓ ✓
Gate 3: Dependency Check ─→ ✗ → Stop, list blockers
    ↓ ✓
Read Intent file
    ↓
Analyze scope and complexity
    ↓
Identify logical phases (0-indexed)
    ↓
For each phase, define:
    - Description
    - Tests (6 categories)
    - E2E Gate
    - Acceptance Criteria
    ↓
Present plan for approval
    ↓
User confirms or adjusts
    ↓
Save to plan.md (same directory as INTENT.md)
    ↓
Create TASK.yaml (status: ready)
```

## Output Files

### 1. plan.md (Required)

```markdown
# Execution Plan: {task_name}

## Overview

简要说明这个任务要做什么。

## Prerequisites

- 前置条件
- 依赖的其他任务
- 需要的权限或资源

## Phase 0: {Phase Name}

### Description

这个阶段要完成什么，交付什么。

### Tests

#### Happy Path
- [ ] 测试正常流程 1: {具体描述}
- [ ] 测试正常流程 2: {具体描述}

#### Bad Path
- [ ] 无效输入: {具体场景}
- [ ] 缺失必填字段: {具体场景}
- [ ] 错误状态: {具体场景}
- [ ] 类型错误: {具体场景}

#### Edge Cases
- [ ] 空输入处理
- [ ] 最大值边界
- [ ] 并发访问

#### Security
- [ ] 注入攻击防护: {具体场景}
- [ ] 权限绕过防护: {具体场景}
- [ ] 输入验证: {具体场景}

#### Data Leak
- [ ] 错误信息不泄露敏感数据
- [ ] 日志不包含敏感信息
- [ ] API 响应不过度暴露

#### Data Damage
- [ ] 部分写入恢复
- [ ] 竞态条件处理
- [ ] 事务完整性

### E2E Gate

```bash
# Phase 完成验证脚本
{CLI commands to verify phase completion}
```

### Acceptance Criteria

- [ ] 所有 6 类测试通过
- [ ] E2E Gate 验证通过
- [ ] 代码已提交并 push

---

## Phase 1: {Phase Name}

### Description

下一阶段要完成什么。

### Tests

#### Happy Path
- [ ] 测试正常流程

#### Bad Path
- [ ] 测试错误处理 1
- [ ] 测试错误处理 2

#### Edge Cases
- [ ] 边界条件处理

#### Security
- [ ] 安全测试

#### Data Leak
- [ ] 泄露防护测试

#### Data Damage
- [ ] 数据完整性测试

### E2E Gate

```bash
# Phase 1 验证脚本
```

### Acceptance Criteria

- [ ] 所有测试通过
- [ ] E2E Gate 验证通过

---

## Final E2E Verification

```bash
# 全系统端到端验证脚本
# 验证所有 Phase 的功能协同工作
```

## Risk Mitigation

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| [风险 1] | [预防措施] | [发生时的应对] |

## References

- [相关 Intent](./INTENT.md)
- [详细规格](./spec.md) (如果存在)
- [设计文档](./design.md) (如果存在)
```

### 2. TASK.yaml (Required)

```yaml
status: ready
owner: null
assignee: null
phase: 0/{total_phases}
updated: {UTC_ISO_TIMESTAMP}
heartbeat: null
```

**Important**: `{total_phases}` is the number of phases in plan.md (0-indexed counting).

## Integration with IDD & TaskSwarm

```
IDD Flow:
/intent-interview     # Create Intent (Gate 1 requirement)
    ↓
/intent-critique      # Review for over-engineering (Gate 2 requirement)
    ↓
/intent-review        # Approve Intent (optional but recommended)
    ↓
/intent-plan          # Gate checks → Generate plan.md + TASK.yaml (THIS SKILL)
    ↓
TaskSwarm Flow:
/swarm run            # Execute plan (TDD cycles)
    ↓
/swarm approve        # Human review
    ↓
/intent-sync          # Write back confirmed details
```

**Gate enforcement ensures quality:**
- No plan without proper interview → avoids vague/incomplete specs
- No plan without critique → avoids over-engineered designs
- No plan with missing deps → avoids unexecutable plans

## Tips for Good Plans

### Format (TaskSwarm Compatible)
1. **0-indexed phases**: Phase 0, Phase 1, Phase 2...
2. **Checkbox format**: All tests use `- [ ]` for progress tracking
3. **E2E Gate per phase**: Each phase must have runnable verification

### Test Quality
4. **All 6 categories required**: Happy/Bad/Edge/Security/Data Leak/Data Damage
5. **Bad Path > Happy Path**: More failure tests than success tests
6. **Specific test cases**: "Test error handling" ✗ → "returns 404 when resource not found" ✓
7. **Security by default**: Include even if not explicitly requested

### Phase Design
8. **Right-size phases**: Each phase completable in 1-3 days
9. **Clear dependencies**: Note when phases depend on previous phases
10. **Automatable gates**: E2E Gate must be runnable via CLI, no manual steps

## Example: Complete Output

For an Intent at `intent/session-protocol/INTENT.md`:

**Creates**: `intent/session-protocol/plan.md`
```markdown
# Execution Plan: session-protocol

## Overview

实现 Session Protocol 的 Frame 编解码功能。

## Prerequisites

- @aigne/afs 包已存在
- TypeScript 环境配置完成

## Phase 0: Frame Encoding

### Description

实现 Frame 的编码函数，将结构化数据转换为二进制格式。

### Tests

#### Happy Path
- [ ] encodes empty frame correctly
- [ ] encodes frame with JSON payload
- [ ] encodes frame with binary payload
- [ ] preserves ReqId across encode/decode

#### Bad Path
- [ ] throws on invalid frame type
- [ ] throws on payload exceeding max size
- [ ] throws on null payload when required
- [ ] throws on negative ReqId
- [ ] throws on non-integer frame type

#### Edge Cases
- [ ] handles empty string payload
- [ ] handles maximum allowed payload size (64KB)
- [ ] handles unicode in JSON payload
- [ ] handles zero-length binary payload

#### Security
- [ ] rejects frames with potential injection patterns
- [ ] validates frame type bounds (0-255)
- [ ] sanitizes string inputs before encoding

#### Data Leak
- [ ] error messages don't expose internal structure
- [ ] stack traces not included in thrown errors

#### Data Damage
- [ ] atomic write: partial encode doesn't corrupt buffer
- [ ] buffer overflow protection

### E2E Gate

```bash
# Verify encoding works end-to-end
pnpm test -- --grep "Frame Encoding"
pnpm test:e2e -- --grep "encode"
```

### Acceptance Criteria

- [ ] 所有 6 类测试通过
- [ ] E2E Gate 验证通过
- [ ] 100% 分支覆盖率
- [ ] 代码已提交

---

## Phase 1: Frame Decoding

### Description

实现 Frame 的解码函数，将二进制数据解析为结构化对象。

### Tests

#### Happy Path
- [ ] decodes valid frame correctly
- [ ] handles streaming decode
- [ ] decodes all frame types

#### Bad Path
- [ ] throws on truncated frame
- [ ] throws on corrupted header
- [ ] throws on invalid magic bytes
- [ ] throws on unsupported version

#### Edge Cases
- [ ] handles minimum valid frame
- [ ] handles maximum valid frame
- [ ] handles back-to-back frames in stream

#### Security
- [ ] validates frame length before allocation
- [ ] rejects oversized frames (DoS protection)

#### Data Leak
- [ ] doesn't expose raw bytes in error messages

#### Data Damage
- [ ] partial decode doesn't advance stream position
- [ ] corrupted frame doesn't affect subsequent frames

### E2E Gate

```bash
# Verify full roundtrip
pnpm test -- --grep "Frame"
echo '{"test":1}' | node scripts/encode-decode-test.js
```

### Acceptance Criteria

- [ ] 所有测试通过
- [ ] E2E roundtrip 验证通过
- [ ] 代码已提交

---

## Final E2E Verification

```bash
# Full integration test
pnpm test
pnpm test:e2e
```

## References

- [Intent](./INTENT.md)
- [Spec](./spec.md)
```

**Creates**: `intent/session-protocol/TASK.yaml`
```yaml
status: ready
owner: null
assignee: null
phase: 0/2
updated: 2026-01-27T10:00:00Z
heartbeat: null
```
