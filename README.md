<div align="center">

# 自己.skill

> *“如果总有一天你要把自己交接给未来的自己，不如先把自己蒸馏成一个可运行的 Skill。”*

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

你的消息越回越多，总有人来问同一类问题？<br>
你接需求、写方案、催进度、回老板、回客户，其实都有固定套路？<br>
你的风格很稳定，但每次都要重新打一遍？<br>
你的“工作方式”和“回复方式”都在你脑子里，没有被结构化？<br>

**把你自己蒸馏成一个能替你工作、替你起草回复、保留你边界感的 AI Skill。**

<br>

提供你自己的原材料（文档、笔记、消息、邮件、自述）<br>
生成一个**真正像你、但不会越权替你乱拍板的 AI Skill**<br>
用你的方式接任务，用你的语气回消息，知道哪些事情必须本人确认

[数据来源](#支持的数据来源) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例)

</div>

---

## 支持的数据来源

> 当前版本先聚焦“本地材料导入 + 手动蒸馏”，不做飞书/微信一键全自动采集。

| 来源 | 工作方式 | 回复风格 | 备注 |
|------|:-------:|:-------:|------|
| PRD / 方案 / 会议纪要 / 复盘 | ✅ | ⚠️ | 主要提取工作系统 |
| 代码评审 / issue / 笔记 | ✅ | ✅ | 适合提取判断规则和说话方式 |
| 聊天记录导出 `.txt/.json/.csv/.html` | ⚠️ | ✅ | 通过 `message_parser.py` 提取你的回复习惯 |
| 邮件 `.eml/.mbox/.txt` | ✅ | ✅ | 通过 `email_parser.py` 提取长文风格与决策表达 |
| README / 博客 / 自述 / 个人说明 | ✅ | ✅ | 适合补充身份和原则 |
| 直接粘贴文字 | ✅ | ✅ | 没有文件也能生成第一版 |
| 图片 / PDF / Markdown / TXT | ✅ | ✅ | 直接读取，作为原材料补充 |

### 当前最推荐的原材料组合

1. **你主动写的长文档**：方案、复盘、长邮件、README
2. **你真实回过的消息**：尤其是催进度、拒绝、对齐、提需求这几类
3. **你自己写的规则**：比如“什么我会拍板，什么必须我本人确认”

---

## 安装

### Claude Code

> **重要**：Claude Code 从 **git 仓库根目录** 的 `.claude/skills/` 查找 skill。请在正确的位置执行。

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
cp -R .codex/skill/self-skill .claude/skills/self-skill

# 或安装到全局（所有项目都能用）
cp -R .codex/skill/self-skill ~/.claude/skills/self-skill
```

### OpenClaw

```bash
cp -R .codex/skill/self-skill ~/.openclaw/workspace/skills/self-skill
```

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

> `pypinyin` 仅用于把中文名字更稳定地转成 slug；没有它也能运行。

---

## 使用

在 Claude Code 中输入：

```text
/create-self
```

然后按提示只回答 3 个问题：

1. 你想把这个 Skill 叫什么
2. 你一句话的工作画像
3. 你一句话的沟通画像

之后选择材料来源：工作文档、消息导出、邮件、个人表达，或者直接粘贴文字。所有字段都可以跳过，仅凭描述也能生成第一版。

完成后用 `/{slug}` 调用该 self Skill。

### 管理命令

| 命令 | 说明 |
|------|------|
| `/list-selves` | 列出所有 self Skill |
| `/{slug}` | 调用完整 Skill（Work System + Reply Persona） |
| `/{slug}-work` | 仅工作系统 |
| `/{slug}-reply` | 仅回复风格 |
| `/self-rollback {slug} {version}` | 回滚到历史版本 |
| `/delete-self {slug}` | 删除 |

---

## 效果示例

> 输入：`AI 产品经理，负责需求拆解和落地推进；对老板结论先行，对同事直接，对客户更克制；涉及报价和排期必须本人确认`

**场景一：接到模糊需求**

```text
用户       ❯ 你帮我看下这个需求怎么做

self.skill ❯ 先补 3 个信息：
              1. 目标用户是谁
              2. 这次要解决的核心问题是什么
              3. 有没有明确上线时间
              信息不齐我只能先给一个草稿方向。
```

**场景二：回老板进度**

```text
用户       ❯ 帮我回老板，说这个需求怎么样了

self.skill ❯ 结论：方案已收敛到一版，今天会补完风险和排期。
              风险有两个：数据口径还没对齐、依赖方接口还没确认。
              如果你要我直接承诺上线日期，我建议你本人确认后再发。
```

**场景三：回客户催促**

```text
用户       ❯ 客户在催，帮我回一下

self.skill ❯ 已收到，我们今天会先给你同步当前判断和待确认项。
              具体交付时间我先不在这里拍板，等内部确认完我再补你一个明确时间点。
```

**场景四：有人想让你直接拍板**

```text
用户       ❯ 对方问能不能这周五上线，你替我答应一下

self.skill ❯ 我可以先起草，但不直接替你答应。
              当前更安全的回复是：
              “我们内部正在核对依赖和排期，今天先给你同步风险，最终时间点我确认后回复你。”
```

---

## 功能特性

### 生成的 Skill 结构

每个 self Skill 由两部分组成，共同驱动输出：

| 部分 | 内容 |
|------|------|
| **Part A — Work System** | 负责范围、接单方式、优先级、流程、输出模板、审批边界 |
| **Part B — Reply Persona** | 语气、句式、对不同对象的说话方式、拒绝与确认规则、边界感 |

运行逻辑：`收到任务/消息 → Persona 判断语气和边界 → Work System 组织执行方式 → 用你的风格输出`

### 这个 Skill 解决什么问题

- **把你的工作方式结构化**：不再每次从零解释“我一般怎么接需求、怎么判断优先级”
- **把你的回复风格复用出来**：让草稿更像你，而不是像一个通用 AI
- **保住你的边界**：不会替你乱承诺报价、时间、对外立场
- **支持持续进化**：追加材料、对话纠正、版本回滚

### 硬边界

这个项目在设计上故意保守：

- **不虚构事实**：不会编造你的观点、你的时间表、你的承诺
- **不越权拍板**：涉及报价、排期、法务、财务、人事、客户承诺时，优先给草稿或确认点
- **不把你“美化”成一个平均人格**：保留你真实的表达偏好和边界
- **用户纠正优先级最高**：你说“这不像我”，就会写入 Correction 规则

### 进化机制

- **追加材料** → 新文档/新消息进来后增量 merge 进现有结论
- **对话纠正** → 说“这不像我”/“我不会这么说” → 写入 Correction Record
- **版本管理** → 每次更新可备份，支持列出历史版本和回滚

---

## 项目结构

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准，整个目录就是一个 skill：

```text
self-skill/
├── SKILL.md
├── README.md
├── requirements.txt
├── agents/
│   └── openai.yaml
├── prompts/
│   ├── intake.md
│   ├── work_analyzer.md
│   ├── persona_analyzer.md
│   ├── work_builder.md
│   ├── persona_builder.md
│   ├── merger.md
│   └── correction_handler.md
├── tools/
│   ├── message_parser.py
│   ├── email_parser.py
│   ├── skill_writer.py
│   └── version_manager.py
└── selves/
    └── {slug}/
        ├── SKILL.md
        ├── work.md
        ├── persona.md
        ├── meta.json
        ├── versions/
        └── sources/
```

---

## 注意事项

- **原材料质量决定蒸馏质量**：你主动写的长文档 + 真实消息记录，效果远好于只有一句自我描述
- 建议优先提供：**长邮件/方案/复盘** > **真实工作消息** > **手动口述**
- 当前版本不做企业 IM 自动抓取，主打**可控、本地、低风险**
- 这个 Skill 的定位是**替你起草、替你复用风格、替你跑通低风险流程**，不是无条件替你做所有最终决定

---

<div align="center">

把“我平时就是这么做的”这句话，变成一个真的能跑起来的 Skill。

</div>
