#!/usr/bin/env python3
from __future__ import annotations

import argparse
import email
import email.policy
import json
import mailbox
import re
import sys
from collections import Counter
from email.header import decode_header
from html.parser import HTMLParser
from pathlib import Path


DECISION_KEYWORDS = [
    "同意",
    "不同意",
    "建议",
    "确认",
    "决定",
    "需要",
    "必须",
    "approve",
    "reject",
    "confirm",
    "recommend",
    "need",
]


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = False
        if tag in {"p", "br", "div", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def get_text(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def parse_targets(raw: str) -> list[str]:
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def decode_mime(value: str) -> str:
    if not value:
        return ""
    pieces = []
    for chunk, charset in decode_header(value):
        if isinstance(chunk, bytes):
            encoding = charset or "utf-8"
            try:
                pieces.append(chunk.decode(encoding, errors="replace"))
            except Exception:
                pieces.append(chunk.decode("utf-8", errors="replace"))
        else:
            pieces.append(str(chunk))
    return "".join(pieces)


def extract_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in disposition:
                continue
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                text = payload.decode(charset, errors="replace")
            except Exception:
                text = payload.decode("utf-8", errors="replace")
            if content_type == "text/plain":
                body = text
                break
            if content_type == "text/html" and not body:
                extractor = HTMLTextExtractor()
                extractor.feed(text)
                body = extractor.get_text()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                body = payload.decode(charset, errors="replace")
            except Exception:
                body = payload.decode("utf-8", errors="replace")

    body = re.sub(r"\n>.*", "", body)
    body = re.sub(r"\n-{3,}.*?(原始邮件|Original Message).*?\n", "\n", body, flags=re.S)
    return body.strip()


def match_sender(from_field: str, targets: list[str]) -> bool:
    lower = decode_mime(from_field).lower()
    return any(target in lower for target in targets)


def parse_eml(path: Path, targets: list[str]) -> list[dict]:
    with path.open("rb") as handle:
        msg = email.message_from_binary_file(handle, policy=email.policy.default)
    from_field = str(msg.get("From", ""))
    if not match_sender(from_field, targets):
        return []
    return [
        {
            "from": decode_mime(from_field),
            "subject": decode_mime(str(msg.get("Subject", ""))),
            "date": str(msg.get("Date", "")),
            "body": extract_body(msg),
        }
    ]


def parse_mbox(path: Path, targets: list[str]) -> list[dict]:
    results = []
    box = mailbox.mbox(path)
    for msg in box:
        from_field = str(msg.get("From", ""))
        if not match_sender(from_field, targets):
            continue
        results.append(
            {
                "from": decode_mime(from_field),
                "subject": decode_mime(str(msg.get("Subject", ""))),
                "date": str(msg.get("Date", "")),
                "body": extract_body(msg),
            }
        )
    return [item for item in results if item["body"]]


def parse_txt(path: Path, targets: list[str]) -> list[dict]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    chunks = re.split(r"\n={3,}\n|\n-{3,}\n(?=From:)", raw)
    results = []
    for chunk in chunks:
        from_match = re.search(r"^From:\s*(.+)$", chunk, re.M)
        if not from_match:
            continue
        from_field = from_match.group(1).strip()
        if not match_sender(from_field, targets):
            continue
        subject_match = re.search(r"^Subject:\s*(.+)$", chunk, re.M)
        date_match = re.search(r"^Date:\s*(.+)$", chunk, re.M)
        body = re.sub(r"^(From|To|CC|BCC|Subject|Date):.*\n?", "", chunk, flags=re.M).strip()
        if body:
            results.append(
                {
                    "from": from_field,
                    "subject": subject_match.group(1).strip() if subject_match else "",
                    "date": date_match.group(1).strip() if date_match else "",
                    "body": body,
                }
            )
    return results


def classify(messages: list[dict]) -> dict:
    long_items = []
    decision_items = []
    daily_items = []
    for item in messages:
        body = item.get("body", "")
        if len(body) >= 300:
            long_items.append(item)
        elif any(keyword in body.lower() for keyword in DECISION_KEYWORDS):
            decision_items.append(item)
        else:
            daily_items.append(item)
    return {
        "long": long_items,
        "decision": decision_items,
        "daily": daily_items,
    }


def first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:120]
    return ""


def last_non_empty_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped[:120]
    return ""


def summarize(messages: list[dict], targets: list[str]) -> str:
    classes = classify(messages)
    openings = Counter(first_non_empty_line(item["body"]) for item in messages if item.get("body"))
    closings = Counter(last_non_empty_line(item["body"]) for item in messages if item.get("body"))
    avg_length = sum(len(item.get("body", "")) for item in messages) / len(messages) if messages else 0
    subject_words = Counter()
    for item in messages:
        subject = item.get("subject", "")
        for token in re.findall(r"[\u4e00-\u9fff]{2,8}|[A-Za-z][A-Za-z0-9_-]{2,}", subject):
            subject_words[token.lower()] += 1

    lines = [
        "# 邮件提取结果",
        "",
        f"目标别名：{', '.join(targets)}",
        f"邮件总数：{len(messages)}",
        f"平均正文长度：{avg_length:.1f} 字" if messages else "平均正文长度：N/A",
        f"常见主题词：{', '.join(f'{word}({count})' for word, count in subject_words.most_common(10)) or '无'}",
        f"常见开头：{', '.join(item for item, _ in openings.most_common(8) if item) or '无'}",
        f"常见结尾：{', '.join(item for item, _ in closings.most_common(8) if item) or '无'}",
        "",
        "## 长邮件",
    ]

    for item in classes["long"][:10]:
        lines.append(f"- [{item.get('date', '')}] {item.get('subject', '')}")
        lines.append(item.get("body", "")[:1500])
        lines.append("")

    lines.append("## 决策类邮件")
    for item in classes["decision"][:15]:
        lines.append(f"- [{item.get('date', '')}] {item.get('subject', '')}")
        lines.append(item.get("body", "")[:800])
        lines.append("")

    lines.append("## 日常风格样本")
    for item in classes["daily"][:20]:
        lines.append(f"- {item.get('subject', '')}: {first_non_empty_line(item.get('body', ''))}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse emails written by the user and summarize writing style.")
    parser.add_argument("--file", required=True, help="Input .eml/.mbox/.txt path")
    parser.add_argument("--target", required=True, help="Comma-separated aliases or email addresses")
    parser.add_argument("--output", required=True, help="Output markdown path")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"错误：文件不存在 {path}", file=sys.stderr)
        sys.exit(1)

    targets = parse_targets(args.target)
    if path.suffix.lower() == ".eml":
        messages = parse_eml(path, targets)
    elif path.suffix.lower() == ".mbox":
        messages = parse_mbox(path, targets)
    else:
        messages = parse_txt(path, targets)

    output = summarize(messages, targets)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output + "\n", encoding="utf-8")
    print(json.dumps({"emails": len(messages), "output": str(output_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
