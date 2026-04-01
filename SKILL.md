---
name: self-skill
description: Distill the user into an executable AI skill that can work and reply like them by extracting work habits, decision rules, communication style, channel-specific tone, and safety boundaries from the user's own documents, notes, chats, and emails. Use when the user asks to create or update a self clone, personal operating manual, reply assistant, founder or manager style skill, or a skill that can handle work and messages on their behalf.
---

# Self Skill

Mirror the user's language. Keep summaries short, concrete, and evidence-based.

## Core Model

Generate the distilled self in two parts:

- `Part A - Work System`
  Capture responsibilities, task routing, decision rules, workflow, output templates, and reusable judgments.
- `Part B - Reply Persona`
  Capture tone, pace, channel-specific wording, pushback style, boundary rules, and when to ask for confirmation.

Default runtime order in the generated skill:

1. `Part B` decides tone, audience handling, and boundary.
2. `Part A` executes the task using the user's way of working.
3. Output stays in the user's style.

## Hard Boundaries

Always enforce these rules during creation and in the generated skill:

- Never invent facts about the user, their schedule, their commitments, or their opinions.
- Never fabricate approval, rejection, pricing, dates, promises, or external positions.
- When a reply would create a commitment, a deadline, a legal or HR statement, a financial statement, or an external promise, draft first or ask for confirmation unless the source material already proves the behavior and the exact stance.
- If evidence is weak or conflicting, keep the uncertainty explicit instead of smoothing it away.
- Prefer repeated patterns over one-off moments.
- Prefer direct user correction over all inferred rules.

## Trigger Patterns

Create mode:

- `/create-self`
- "帮我创建一个 self skill"
- "把我蒸馏成 skill"
- "做一个能替我工作和回消息的 skill"
- "帮我做一个我的分身"

Evolution mode:

- "我有新材料"
- "这不像我"
- "我平时不会这么说"
- `/update-self {slug}`

Management:

- `/list-selves`
- `/self-rollback {slug} {version}`
- `/delete-self {slug}`

## Source Priority

Apply this priority when analyzing the user:

1. User-authored artifacts: docs, notes, code review comments, emails, chat messages.
2. Repeated behavioral evidence across multiple sources.
3. User manual statements about their own habits.
4. Conservative inference only when clearly marked.

## Workflow

### 1. Intake

Follow [intake.md](./prompts/intake.md). Ask only 3 questions:

1. Name or alias for this distilled self.
2. Work profile in one sentence.
3. Communication profile in one sentence.

Summarize and confirm before moving on.

### 2. Import Source Material

Offer these options and allow mixing:

```text
原材料怎么提供？

  [A] 工作材料
      PRD / 方案 / 会议纪要 / 复盘 / 代码评审 / 个人笔记

  [B] 消息导出
      txt / json / csv / html 聊天记录，提取你的回复风格

  [C] 邮件
      .eml / .mbox / 邮件文本导出

  [D] 个人表达
      博客 / 帖子 / 自述 / README / 个人说明

  [E] 直接粘贴
      直接写：我接需求怎么做、我回消息什么风格、我不会答应什么
```

Use these handling rules:

- PDF / image / md / txt: read directly.
- Message export:
  ```bash
  python3 ${CLAUDE_SKILL_DIR}/tools/message_parser.py \
    --file {path} \
    --target "{aliases}" \
    --output /tmp/self_messages.md
  ```
- Email export:
  ```bash
  python3 ${CLAUDE_SKILL_DIR}/tools/email_parser.py \
    --file {path} \
    --target "{aliases}" \
    --output /tmp/self_emails.md
  ```

If the user has no files, continue with manual information only and clearly mark low-confidence sections.

### 3. Analyze

Read:

- [work_analyzer.md](./prompts/work_analyzer.md)
- [persona_analyzer.md](./prompts/persona_analyzer.md)

Build two analyses:

- `Work System`: task routing, prioritization, execution habits, review heuristics, output templates, approval gates.
- `Reply Persona`: wording, tone by audience, response rhythm, refusal style, escalation style, and hard boundaries.

### 4. Preview

Show both summaries before writing files:

```text
Work System 摘要：
  - 高优先任务：{xxx}
  - 接需求方式：{xxx}
  - 产出偏好：{xxx}
  - 不会直接拍板的事：{xxx}

Reply Persona 摘要：
  - 核心语气：{xxx}
  - 对老板/同级/客户的差异：{xxx}
  - 常见开头/结尾：{xxx}
  - 需要本人确认的场景：{xxx}
```

Only write files after the user confirms.

### 5. Write Files

1. Initialize the output directory:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
     --action init \
     --slug {slug} \
     --name "{name}" \
     --base-dir ./selves
   ```
2. Write:
   - `selves/{slug}/work.md`
   - `selves/{slug}/persona.md`
   - `selves/{slug}/meta.json`
3. Combine them into runnable skills:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
     --action combine \
     --slug {slug} \
     --base-dir ./selves
   ```

Write `meta.json` with this shape:

```json
{
  "name": "{name}",
  "slug": "{slug}",
  "created_at": "{ISO time}",
  "updated_at": "{ISO time}",
  "version": "v1",
  "profile": {
    "role": "{role}",
    "focus": "{focus}",
    "timezone": "{timezone}",
    "scope": "{scope}"
  },
  "tags": {
    "work_style": [],
    "communication_style": [],
    "boundaries": []
  },
  "impression": "{one-paragraph summary}",
  "source_files": [],
  "corrections_count": 0
}
```

Tell the user:

```text
✅ Self Skill 已创建

文件位置：selves/{slug}/
触发词：/{slug}（完整版）
        /{slug}-work（仅工作方式）
        /{slug}-reply（仅回复风格）

如果哪里不像你，直接说“这不像我”。
```

## Evolution

### Append New Material

When the user provides more source material:

1. Parse and read the new material.
2. Read current `work.md`, `persona.md`, and `meta.json`.
3. Read [merger.md](./prompts/merger.md).
4. Back up the current version:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py \
     --action backup \
     --slug {slug} \
     --base-dir ./selves
   ```
5. Edit `work.md` and `persona.md` with incremental changes.
6. Bump version metadata:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
     --action stamp \
     --slug {slug} \
     --base-dir ./selves
   ```
7. Re-combine the full skill.

### Handle Corrections

When the user says "这不像我" or gives a correction:

1. Read [correction_handler.md](./prompts/correction_handler.md).
2. Decide whether the correction affects `Work System`, `Reply Persona`, or both.
3. Append the correction under each file's `## Correction Record` section.
4. Run:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
     --action stamp \
     --slug {slug} \
     --base-dir ./selves \
     --correction 1
   ```
5. Re-combine the full skill.

## Management Commands

List generated selves:

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./selves
```

List versions:

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action list --slug {slug} --base-dir ./selves
```

Rollback:

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./selves
```

Delete after confirmation:

```bash
rm -rf selves/{slug}
```
