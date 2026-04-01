#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


SENDER_KEYS = ("sender", "from", "author", "speaker", "name", "user", "nickname")
CONTENT_KEYS = ("content", "text", "message", "body", "msg")
TIME_KEYS = ("timestamp", "time", "date", "created_at", "datetime", "send_time")
STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "you",
    "have",
    "from",
    "我们",
    "你们",
    "他们",
    "就是",
    "然后",
    "这个",
    "那个",
    "一下",
    "已经",
    "还是",
    "没有",
}
TIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%m/%d/%Y, %I:%M %p",
    "%m/%d/%Y, %H:%M",
]


def parse_targets(raw: str) -> list[str]:
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def strip_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", "", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return normalize_text(html.unescape(text))


def parse_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    candidate = str(raw).strip().strip("[]")
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(candidate, fmt)
        except ValueError:
            continue
    return None


def message_signature(item: dict) -> tuple[str, str, str]:
    return (
        item.get("sender", "").strip(),
        item.get("timestamp", "").strip(),
        item.get("content", "").strip()[:120],
    )


def matches_sender(sender: str, targets: list[str]) -> bool:
    lower = sender.lower()
    return any(target in lower for target in targets)


def first_value(record: dict, keys: tuple[str, ...]) -> str:
    lowered = {str(key).lower(): value for key, value in record.items()}
    for key in keys:
        if key in lowered and lowered[key] is not None:
            return str(lowered[key]).strip()
    return ""


def coerce_message(record: dict) -> dict | None:
    sender = first_value(record, SENDER_KEYS)
    content = first_value(record, CONTENT_KEYS)
    timestamp = first_value(record, TIME_KEYS)
    if not sender or not content:
        return None
    return {
        "sender": sender,
        "content": normalize_text(content),
        "timestamp": timestamp,
    }


def collect_json_messages(node, seen: set[tuple[str, str, str]], result: list[dict]) -> None:
    if isinstance(node, dict):
        maybe_message = coerce_message(node)
        if maybe_message:
            signature = message_signature(maybe_message)
            if signature not in seen:
                seen.add(signature)
                result.append(maybe_message)
        for value in node.values():
            collect_json_messages(value, seen, result)
    elif isinstance(node, list):
        for item in node:
            collect_json_messages(item, seen, result)


def parse_json_file(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    result: list[dict] = []
    collect_json_messages(data, set(), result)
    return result


def parse_csv_file(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        reader = csv.DictReader(handle)
        result = []
        for row in reader:
            message = coerce_message(row)
            if message:
                result.append(message)
        return result


def parse_text_file(path: Path) -> tuple[list[dict], str]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if "<html" in raw.lower() or "<div" in raw.lower():
        raw = strip_html(raw)
    else:
        raw = normalize_text(raw)

    messages: list[dict] = []
    inline_pattern = re.compile(
        r"^\[?((?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}/\d{1,2}/\d{4})[^\]]{0,24})\]?\s+([^:：]+?)[:：]\s*(.+)$"
    )
    block_pattern = re.compile(r"^(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)$")
    current: dict | None = None

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        inline_match = inline_pattern.match(stripped)
        if inline_match:
            if current:
                messages.append(current)
            timestamp, sender, content = inline_match.groups()
            current = {"timestamp": timestamp, "sender": sender.strip(), "content": content.strip()}
            continue

        block_match = block_pattern.match(stripped)
        if block_match and len(stripped.split()) >= 3:
            if current:
                messages.append(current)
            timestamp, sender = block_match.groups()
            current = {"timestamp": timestamp, "sender": sender.strip(), "content": ""}
            continue

        if current:
            current["content"] = normalize_text(f"{current['content']}\n{stripped}")

    if current:
        messages.append(current)

    return messages, raw


def token_frequency(messages: list[dict]) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    pattern = re.compile(r"[\u4e00-\u9fff]{2,8}|[A-Za-z][A-Za-z0-9_-]{2,}")
    for item in messages:
        for token in pattern.findall(item.get("content", "")):
            normalized = token.lower()
            if normalized in STOPWORDS:
                continue
            counter[normalized] += 1
    return counter.most_common(15)


def opener(text: str) -> str:
    return normalize_text(text)[:8]


def closer(text: str) -> str:
    return normalize_text(text)[-8:]


def response_stats(messages: list[dict], targets: list[str]) -> str:
    deltas = []
    for index in range(1, len(messages)):
        prev_item = messages[index - 1]
        current_item = messages[index]
        if matches_sender(prev_item.get("sender", ""), targets):
            continue
        if not matches_sender(current_item.get("sender", ""), targets):
            continue
        prev_time = parse_datetime(prev_item.get("timestamp"))
        current_time = parse_datetime(current_item.get("timestamp"))
        if not prev_time or not current_time:
            continue
        seconds = (current_time - prev_time).total_seconds()
        if 0 <= seconds <= 7 * 24 * 3600:
            deltas.append(seconds)

    if not deltas:
        return "时间信息不足，无法稳定估计回复时延"

    within_5m = sum(1 for item in deltas if item <= 300)
    within_1h = sum(1 for item in deltas if item <= 3600)
    avg_minutes = sum(deltas) / len(deltas) / 60
    return (
        f"平均约 {avg_minutes:.1f} 分钟；"
        f"5 分钟内 {within_5m} 次；"
        f"1 小时内 {within_1h} 次；"
        f"1 小时以上 {len(deltas) - within_1h} 次"
    )


def analyze(messages: list[dict], raw_text: str, targets: list[str]) -> str:
    target_messages = [item for item in messages if matches_sender(item.get("sender", ""), targets)]
    all_text = "\n".join(item.get("content", "") for item in target_messages)

    particles = Counter(re.findall(r"[哈嗯哦噢嘿唉啊呀吧呢嘛]+", all_text))
    emojis = Counter(
        re.findall(
            r"[\U0001F300-\U0001FAFF\u2600-\u27BF]+",
            all_text,
        )
    )
    openers = Counter(opener(item.get("content", "")) for item in target_messages if item.get("content"))
    closers = Counter(closer(item.get("content", "")) for item in target_messages if item.get("content"))
    lengths = [len(item.get("content", "")) for item in target_messages if item.get("content")]
    punctuation = {
        "句号": all_text.count("。") + all_text.count("."),
        "问号": all_text.count("？") + all_text.count("?"),
        "感叹号": all_text.count("！") + all_text.count("!"),
        "省略号": all_text.count("…") + all_text.count("..."),
        "波浪号": all_text.count("~") + all_text.count("～"),
    }

    lines = [
        "# 消息提取结果",
        "",
        f"目标别名：{', '.join(targets)}",
        f"结构化消息数：{len(messages)}",
        f"目标消息数：{len(target_messages)}",
        "",
    ]

    if not target_messages:
        lines.extend(
            [
                "## 结论",
                "未稳定提取到目标发送者的结构化消息，请检查 `--target` 或消息导出格式。",
                "",
                "## 原始文本摘录",
                raw_text[:3000],
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "## 风格摘要",
            f"- 平均消息长度：{(sum(lengths) / len(lengths)):.1f} 字" if lengths else "- 平均消息长度：N/A",
            f"- 回复节奏：{response_stats(messages, targets)}",
            f"- 常见开头：{', '.join(item for item, _ in openers.most_common(8) if item)}",
            f"- 常见结尾：{', '.join(item for item, _ in closers.most_common(8) if item)}",
            f"- 高频词：{', '.join(f'{word}({count})' for word, count in token_frequency(target_messages)[:12])}",
            f"- 高频语气词：{', '.join(f'{word}({count})' for word, count in particles.most_common(10)) or '无明显语气词'}",
            f"- 常见 emoji：{', '.join(f'{word}({count})' for word, count in emojis.most_common(10)) or '几乎不用 emoji'}",
            f"- 标点偏好：{', '.join(f'{key}{value}' for key, value in punctuation.items())}",
            "",
            "## 样本消息",
        ]
    )

    for index, item in enumerate(target_messages[:40], start=1):
        timestamp = item.get("timestamp", "")
        prefix = f"{index}. [{timestamp}] " if timestamp else f"{index}. "
        lines.append(prefix + item.get("content", ""))

    lines.extend(["", "## 原始文本摘录", raw_text[:3000]])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse exported messages and summarize the user's reply style.")
    parser.add_argument("--file", required=True, help="Input file path")
    parser.add_argument("--target", required=True, help="Comma-separated aliases for the user")
    parser.add_argument("--output", required=True, help="Output markdown path")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"错误：文件不存在 {path}", file=sys.stderr)
        sys.exit(1)

    suffix = path.suffix.lower()
    raw_text = ""
    if suffix == ".json":
        messages = parse_json_file(path)
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".csv":
        messages = parse_csv_file(path)
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
    else:
        messages, raw_text = parse_text_file(path)

    targets = parse_targets(args.target)
    output = analyze(messages, raw_text, targets)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output + "\n", encoding="utf-8")
    print(f"分析完成，结果已写入 {output_path}")


if __name__ == "__main__":
    main()
