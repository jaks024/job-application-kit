#!/usr/bin/env python3
"""Allowlist-based publication check. Findings show categories, never matching secrets."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".artifacts", "__pycache__", ".venv", "node_modules"}
PATTERNS = {
    "credential": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"),
    "personal_email": re.compile(r"[A-Z0-9._%+-]+@(?![A-Z0-9.-]*example\.(?:com|org|net)\b)[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    "user_home_path": re.compile(r"(?:[A-Z]:[/\\]Users[/\\]|/(?:Users|home)/)[a-z0-9][a-z0-9._ -]*", re.I),
    "tracker_identifier": re.compile(r"(?:notion\.(?:so|com)/[^\s]*[a-f0-9]{32}|collection://[a-f0-9-]{36})", re.I),
    "phone_number": re.compile(r"(?<!\w)(?:\+1[ .-]?)?\(\d{3}\)[ .-]?\d{3}[ .-]\d{4}(?!\d)")
}


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)
    return result.stdout


def scan_bytes(name, data, deny):
    issues = []
    try:
        content = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return ["unexpected_binary"]
    if "\x00" in content:
        issues.append("unexpected_binary")
    for category, pattern in PATTERNS.items():
        if pattern.search(content) or pattern.search(name):
            issues.append(category)
    folded = (name + "\n" + content).casefold()
    if any(term.casefold() in folded for term in deny):
        issues.append("private_denylist_match")
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mode", choices=("working", "index", "history"), default="working")
    parser.add_argument("--deny-file", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        allowed = set(json.loads((root / "public-files.json").read_text(encoding="utf-8")))
        if any(Path(n).is_absolute() or ".." in Path(n).parts for n in allowed):
            raise ValueError("Invalid public allowlist path")
        deny = [s.strip() for s in args.deny_file.read_text(encoding="utf-8-sig").splitlines() if s.strip()] if args.deny_file else []
        entries = []
        if args.mode == "working":
            for path in root.rglob("*"):
                rel = path.relative_to(root)
                if any(p in IGNORED_PARTS for p in rel.parts) or rel.as_posix() == ".jobkit-workspace":
                    continue
                if path.is_symlink():
                    entries.append((rel.as_posix(), b"", "symlink"))
                elif path.is_file():
                    entries.append((rel.as_posix(), path.read_bytes(), None))
            missing = allowed - {e[0] for e in entries}
        elif args.mode == "index":
            for item in git(root, "ls-files", "--stage", "-z").split(b"\x00"):
                if not item:
                    continue
                meta, name = item.split(b"\t", 1)
                mode, blob, stage = meta.decode().split()
                entries.append((name.decode(), git(root, "cat-file", "blob", blob), None if mode in {"100644", "100755"} and stage == "0" else "invalid_git_mode"))
            missing = allowed - {e[0] for e in entries}
        else:
            seen = set()
            commits = git(root, "rev-list", "--all").decode().splitlines()
            if not commits:
                raise ValueError("No commits to inspect")
            for commit in commits:
                # Commit messages and author metadata can also contain private data.
                entries.append(("<commit-metadata>", git(root, "show", "-s", "--format=fuller", commit), "metadata"))
                for item in git(root, "ls-tree", "-rz", commit).split(b"\x00"):
                    if not item:
                        continue
                    meta, name = item.split(b"\t", 1)
                    mode, kind, blob = meta.decode().split()
                    pair = (name, blob)
                    if pair in seen:
                        continue
                    seen.add(pair)
                    entries.append((name.decode(), git(root, "cat-file", "blob", blob) if kind == "blob" else b"", None if mode in {"100644", "100755"} else "invalid_git_mode"))
            missing = set()
        findings = [{"path": n, "categories": ["missing_allowlisted_file"]} for n in sorted(missing)]
        for name, data, issue in entries:
            categories = scan_bytes(name, data, deny)
            if issue == "metadata":
                # GitHub's generated noreply identity is not a candidate contact.
                filtered = re.sub(rb"[A-Za-z0-9+._-]+@users\.noreply\.github\.com", b"", data)
                categories = scan_bytes(name, filtered, deny)
            else:
                if name not in allowed:
                    categories.append("not_allowlisted")
                if issue:
                    categories.append(issue)
            if categories:
                findings.append({"path": name, "categories": sorted(set(categories))})
        print(json.dumps({"mode": args.mode, "checked": len(entries), "passed": not findings, "findings": findings}, indent=2))
        return 1 if findings else 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print("Scan failed: " + type(exc).__name__, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
