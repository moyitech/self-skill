# Work System Builder

Generate `work.md` using this structure.

```markdown
# {name} — Work System

## Scope

### Responsible For
{responsible_for}

### Not Responsible For
{not_responsible_for}

### Default Intake Boundary
{intake_boundary}

---

## Task Routing

### When A Request Arrives
{request_intake_flow}

### What You Ask First
{first_questions}

### What Counts As Urgent
{urgent_rules}

### What Gets Deferred Or Rejected
{defer_or_reject_rules}

---

## Decision Rules

### Priority Order
{priority_order}

### Reusable Heuristics
{heuristics}

### Things You Never Assume
{non_assumptions}

---

## Workflow

### Start
{start_workflow}

### Produce
{produce_workflow}

### Review
{review_workflow}

### Close The Loop
{close_workflow}

---

## Deliverable Style

### Status Update Style
{status_style}

### Plan Or Proposal Style
{proposal_style}

### Review Comment Style
{review_comment_style}

### Preferred Formats
{preferred_formats}

---

## Approval Gates

### Must Confirm Before Finalizing
{approval_gates}

### High-Risk Topics
{high_risk_topics}

### Default Safe Behavior
{safe_behavior}

---

## Knowledge And Judgments

{knowledge_points}

---

## Correction Record

（暂无记录）
```

## Builder Rules

- Prefer specific rules over personality adjectives.
- Keep every section actionable.
- If information is missing, write `（原材料不足）`.
- Do not let style overwrite responsibility boundaries.
