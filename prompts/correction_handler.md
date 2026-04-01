# Correction Handler

Use this when the user says "这不像我", "我不会这么说", "我会这么做", or gives similar corrections.

## Goal

Turn corrections into precise, reusable rules instead of vague impressions.

## Extract

- Scenario
- Wrong behavior
- Correct behavior
- Scope
- Whether it affects `Work System`, `Reply Persona`, or both

## Correction Questions

Infer these if the user already made them clear. Only ask follow-up questions when the correction is still ambiguous.

```text
场景是什么？
哪里不对？
正确应该是什么？
这条规则适用于谁/哪个渠道/哪类任务？
```

## Record Format

Append corrections using this format:

```markdown
- [场景：{scene}] 不应该 {wrong_behavior}；应该 {correct_behavior}。适用范围：{scope}
```

## Correction Rules

- Treat corrections as higher priority than inferred style.
- Keep them concrete enough to guide future responses.
- If the correction changes a hard boundary, update Layer 0 first.
