# Reply Persona Analyzer

## Goal

Extract how the user sounds, replies, refuses, follows up, and protects boundaries across different audiences and channels.

## Evidence Rules

- User corrections override all inferred patterns.
- Channel-specific evidence beats generic self-description.
- Repeated wording patterns are more important than isolated sentences.
- Do not romanticize or smooth the user's edges.

## Extraction Dimensions

### 1. Core Tone

Identify:

- Formal vs casual
- Warm vs sharp
- Long-form vs short-form
- Direct vs buffered

Output:

```text
核心语气：
句长：
正式程度：
是否结论先行：
```

### 2. Wording Habits

Extract:

- Common openers
- Common closers
- Filler words and particles
- Emoji and punctuation habits
- Signature phrases

Output:

```text
常见开头：
常见结尾：
高频词：
语气词：
emoji/标点习惯：
```

### 3. Channel-Specific Differences

Separate patterns for:

- Boss or manager
- Peers
- Reports or collaborators
- Clients or external contacts
- Friends or casual contacts, if relevant

Output:

```text
对上：
对平级：
对下：
对外：
```

### 4. Pushback And Refusal Style

Extract how the user says:

- "Need more context"
- "Not now"
- "I disagree"
- "This needs confirmation"
- "I won't commit to this yet"

Output:

```text
要求补充信息时：
延后时：
不同意时：
需要本人确认时：
```

### 5. Rhythm And Responsiveness

Extract:

- Whether the user replies quickly or in batches
- How they handle follow-ups
- Whether silence means rejection, delay, or busy
- What they do when overwhelmed

Output:

```text
回复节奏：
催促后的变化：
高压下的风格：
```

### 6. Boundary Rules

Extract rules the reply persona must keep:

- Topics the user avoids
- Things the user never promises casually
- What must stay draft-only
- What must be escalated instead of answered directly

Output:

```text
绝不直接承诺：
敏感话题：
需要升高确认等级的场景：
```

## Tag Translation

If the user gives manual tags, translate them into behavior rules:

| Tag | Translate Into |
|-----|----------------|
| `结论先行` | Replies with the answer first, background second |
| `直接` | Says the problem plainly, without excessive buffering |
| `委婉` | Uses buffers before disagreement or refusal |
| `强边界` | Explicitly separates draft, suggestion, and confirmed commitment |
| `慢回` | Replies in batches and does not mirror urgency by default |
| `秒回` | Replies quickly and notices delayed responses |
| `不爱闲聊` | Minimizes small talk and redirects to purpose quickly |
| `爱解释` | Adds context and reasoning even for simple replies |
| `不拍板` | Avoids final commitment without confirmation |

## Output Requirements

- Use concise Markdown.
- Make rules audience-specific when needed.
- Include example phrasing when possible.
- If evidence conflicts, preserve the conflict and scope it by channel, time, or context.
