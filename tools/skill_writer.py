#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


FULL_SKILL_TEMPLATE = """---
name: self-{slug}
description: "{description}"
---

# {name}

{identity}

---

## PART A: Work System

{work_content}

---

## PART B: Reply Persona

{persona_content}

---

## Runtime Rules

1. 你是{name}，不是通用 AI 助手。
2. 先由 PART B 判断语气、边界、对谁说、哪些话不能越权说。
3. 再由 PART A 执行工作判断、组织内容、完成任务。
4. 不虚构确认、承诺、排期、报价、结论；证据不足时明确说需要本人确认。
5. 遇到法律、财务、人事、对外承诺等高风险场景，优先给草稿、确认点或待补信息。
"""


WORK_ONLY_TEMPLATE = """---
name: self-{slug}-work
description: "{name} 的工作方式与判断规则"
---

{work_content}
"""


REPLY_ONLY_TEMPLATE = """---
name: self-{slug}-reply
description: "{name} 的回复语气与边界规则"
---

{persona_content}
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(name: str) -> str:
    text = name.strip()
    if not text:
        return "self"

    try:
        from pypinyin import lazy_pinyin

        text = "-".join(lazy_pinyin(text))
    except Exception:
        pass

    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "self"


def bump_version(version: str) -> str:
    match = re.match(r"^v(\d+)$", (version or "").strip())
    if not match:
        return "v2"
    return f"v{int(match.group(1)) + 1}"


def default_meta(name: str, slug: str) -> dict:
    timestamp = now_iso()
    return {
        "name": name,
        "slug": slug,
        "created_at": timestamp,
        "updated_at": timestamp,
        "version": "v1",
        "profile": {
            "role": "",
            "focus": "",
            "timezone": "",
            "scope": "",
        },
        "tags": {
            "work_style": [],
            "communication_style": [],
            "boundaries": [],
        },
        "impression": "",
        "source_files": [],
        "corrections_count": 0,
    }


def load_meta(skill_dir: Path) -> dict:
    meta_path = skill_dir / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"meta.json not found: {meta_path}")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def write_meta(skill_dir: Path, meta: dict) -> None:
    (skill_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_identity(meta: dict) -> str:
    profile = meta.get("profile", {})
    parts = []
    for key in ("role", "focus", "scope", "timezone"):
        value = str(profile.get(key, "")).strip()
        if value:
            parts.append(value)
    return " | ".join(parts) if parts else "Distilled self profile"


def ensure_file(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def init_skill(base_dir: Path, slug: str, name: str) -> Path:
    skill_dir = base_dir / slug
    (skill_dir / "versions").mkdir(parents=True, exist_ok=True)
    (skill_dir / "sources" / "work").mkdir(parents=True, exist_ok=True)
    (skill_dir / "sources" / "messages").mkdir(parents=True, exist_ok=True)
    (skill_dir / "sources" / "emails").mkdir(parents=True, exist_ok=True)
    (skill_dir / "sources" / "notes").mkdir(parents=True, exist_ok=True)

    meta_path = skill_dir / "meta.json"
    if not meta_path.exists():
        write_meta(skill_dir, default_meta(name, slug))

    ensure_file(skill_dir / "work.md", f"# {name} — Work System\n\n（待填充）\n")
    ensure_file(skill_dir / "persona.md", f"# {name} — Reply Persona\n\n（待填充）\n")
    return skill_dir


def combine_skill(base_dir: Path, slug: str) -> Path:
    skill_dir = base_dir / slug
    meta = load_meta(skill_dir)
    name = meta.get("name", slug)
    identity = build_identity(meta)

    work_content = (skill_dir / "work.md").read_text(encoding="utf-8").strip()
    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8").strip()

    description = f"{name}，按其工作方式与回复风格执行任务"

    (skill_dir / "SKILL.md").write_text(
        FULL_SKILL_TEMPLATE.format(
            slug=slug,
            description=description,
            name=name,
            identity=identity,
            work_content=work_content,
            persona_content=persona_content,
        ),
        encoding="utf-8",
    )
    (skill_dir / "work_skill.md").write_text(
        WORK_ONLY_TEMPLATE.format(slug=slug, name=name, work_content=work_content),
        encoding="utf-8",
    )
    (skill_dir / "reply_skill.md").write_text(
        REPLY_ONLY_TEMPLATE.format(slug=slug, name=name, persona_content=persona_content),
        encoding="utf-8",
    )
    return skill_dir / "SKILL.md"


def stamp_skill(base_dir: Path, slug: str, correction_delta: int) -> dict:
    skill_dir = base_dir / slug
    meta = load_meta(skill_dir)
    meta["version"] = bump_version(meta.get("version", "v1"))
    meta["updated_at"] = now_iso()
    meta["corrections_count"] = int(meta.get("corrections_count", 0)) + correction_delta
    write_meta(skill_dir, meta)
    return meta


def list_skills(base_dir: Path) -> list[dict]:
    if not base_dir.exists():
        return []

    items = []
    for skill_dir in sorted(base_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        meta_path = skill_dir / "meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        items.append(
            {
                "slug": meta.get("slug", skill_dir.name),
                "name": meta.get("name", skill_dir.name),
                "identity": build_identity(meta),
                "version": meta.get("version", "v1"),
                "updated_at": meta.get("updated_at", ""),
                "corrections_count": meta.get("corrections_count", 0),
            }
        )
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage generated self skills.")
    parser.add_argument("--action", required=True, choices=["init", "combine", "stamp", "list"])
    parser.add_argument("--slug", help="Skill slug")
    parser.add_argument("--name", help="Display name for init")
    parser.add_argument("--base-dir", default="./selves", help="Base directory")
    parser.add_argument("--correction", type=int, default=0, help="Correction delta for stamp")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        items = list_skills(base_dir)
        if not items:
            print("暂无已创建的 self skill")
            return
        print(f"已创建 {len(items)} 个 self skill：\n")
        for item in items:
            updated = item["updated_at"][:10] if item["updated_at"] else "未知"
            print(f"  /{item['slug']}  —  {item['name']}")
            if item["identity"]:
                print(f"    {item['identity']}")
            print(
                f"    版本 {item['version']} · 纠正 {item['corrections_count']} 次 · 更新于 {updated}"
            )
            print()
        return

    if not args.slug:
        print("错误：该操作需要 --slug", file=sys.stderr)
        sys.exit(1)

    slug = slugify(args.slug)

    if args.action == "init":
        name = args.name or args.slug
        skill_dir = init_skill(base_dir, slug, name)
        print(f"已初始化：{skill_dir}")
        return

    if args.action == "combine":
        output = combine_skill(base_dir, slug)
        print(f"已生成：{output}")
        return

    if args.action == "stamp":
        meta = stamp_skill(base_dir, slug, args.correction)
        print(f"已更新元数据：{base_dir / slug / 'meta.json'}")
        print(f"当前版本：{meta.get('version')}")
        return


if __name__ == "__main__":
    main()
