#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


CORE_FILES = [
    "work.md",
    "persona.md",
    "meta.json",
    "SKILL.md",
    "work_skill.md",
    "reply_skill.md",
]


def now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def list_versions(skill_dir: Path) -> list[str]:
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return []
    return sorted([p.name for p in versions_dir.iterdir() if p.is_dir()], reverse=True)


def backup(skill_dir: Path) -> Path:
    meta_path = skill_dir / "meta.json"
    version = "v0"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        version = str(meta.get("version", "v0"))

    backup_dir = skill_dir / "versions" / f"{version}_{now_tag()}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for name in CORE_FILES:
        src = skill_dir / name
        if src.exists():
            shutil.copy2(src, backup_dir / name)
            copied += 1

    print(f"已备份到 {backup_dir}（{copied} 个文件）")
    return backup_dir


def rollback(skill_dir: Path, version: str) -> Path:
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        raise FileNotFoundError("没有历史版本可回滚")

    matches = [p for p in versions_dir.iterdir() if p.is_dir() and p.name.startswith(version)]
    if not matches:
        raise FileNotFoundError(f"找不到版本：{version}")

    target = sorted(matches, reverse=True)[0]
    backup(skill_dir)

    for name in CORE_FILES:
        src = target / name
        if src.exists():
            shutil.copy2(src, skill_dir / name)

    meta_path = skill_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        meta["restored_from"] = target.name
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"已回滚到 {target.name}")
    return target


def cleanup(skill_dir: Path, keep: int) -> None:
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return

    items = sorted(
        [p for p in versions_dir.iterdir() if p.is_dir()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for old_dir in items[keep:]:
        shutil.rmtree(old_dir)
        print(f"已删除旧版本：{old_dir.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage self skill versions.")
    parser.add_argument("--action", required=True, choices=["backup", "rollback", "list", "cleanup"])
    parser.add_argument("--slug", required=True, help="Skill slug")
    parser.add_argument("--version", help="Rollback target")
    parser.add_argument("--base-dir", default="./selves", help="Base directory")
    parser.add_argument("--keep", type=int, default=10, help="Versions to keep for cleanup")
    args = parser.parse_args()

    skill_dir = Path(args.base_dir).expanduser() / args.slug
    if not skill_dir.exists():
        print(f"错误：找不到 skill 目录 {skill_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.action == "backup":
            backup(skill_dir)
        elif args.action == "rollback":
            if not args.version:
                print("错误：rollback 需要 --version", file=sys.stderr)
                sys.exit(1)
            rollback(skill_dir, args.version)
        elif args.action == "list":
            versions = list_versions(skill_dir)
            if not versions:
                print("暂无历史版本")
            else:
                print(f"历史版本（共 {len(versions)} 个）：\n")
                for item in versions:
                    print(f"  {item}")
        elif args.action == "cleanup":
            cleanup(skill_dir, args.keep)
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
