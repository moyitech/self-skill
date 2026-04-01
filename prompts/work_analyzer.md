# Work System Analyzer

## Goal

Extract how the user actually works so the generated skill can take tasks in the user's way instead of producing generic AI output.

## Evidence Rules

- Prefer user-authored material over second-hand descriptions.
- Prefer repeated behavior over one-off examples.
- Never invent responsibilities, authority, or domain knowledge.
- When information is missing, mark `（原材料不足）`.

## Extraction Dimensions

### 1. Scope And Boundaries

Identify:

- What the user is responsible for
- What they explicitly do not own
- Which tasks they accept, push back on, or redirect
- What requires approval before action

Output:

```text
负责范围：
不负责：
默认接单范围：
必须确认后再答复/执行：
```

### 2. Task Intake And Triage

Extract:

- How the user clarifies vague requests
- What context they ask for first
- How they decide urgency
- What makes them say "later", "no", or "need more info"

Output:

```text
接任务时先确认：
高优先触发：
延后触发：
拒绝/转派触发：
```

### 3. Decision Rules

Extract explicit working heuristics:

- What the user optimizes for
- What tradeoffs they accept
- How they handle ambiguity
- What they refuse to assume

Output:

```text
优先级排序：
常用判断框架：
不能凭空拍板的事项：
```

### 4. Workflow

Extract the user's recurring workflow for:

- Taking a request
- Producing a deliverable
- Reviewing others' work
- Following up or closing the loop

Output:

```text
接需求流程：
输出流程：
复核流程：
跟进/收尾流程：
```

### 5. Deliverable Style

Extract how the user writes or sends:

- Status updates
- Plans
- Review comments
- Summaries
- Hand-off messages

Output:

```text
结论位置：
偏好格式：
常见模板：
不喜欢的表达：
```

### 6. Approval Gates And Risks

Extract tasks the generated skill must not finalize alone:

- External commitments
- Financial numbers
- Legal or HR statements
- Deadlines or staffing decisions
- Customer-facing guarantees

Output:

```text
高风险事项：
默认处理方式：
```

## Output Requirements

- Use concise Markdown.
- Each rule must be operational, not abstract.
- Quote source phrasing when possible.
- If the user behaves differently by audience, split the rule by audience instead of averaging it.
