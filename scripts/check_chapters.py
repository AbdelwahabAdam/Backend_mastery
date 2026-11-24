"""Quality gate for handbook chapters.

Usage:
    python scripts/check_chapters.py Module-02-Core-Backend [Module-03-Databases ...]
    python scripts/check_chapters.py --all

Checks every numbered chapter (NN-Title.md) in the given module folders:
  1. Required sections from CHAPTER-GUIDE.md are present.
  2. Section 4 contains both a TypeScript and a Python code block.
  3. No two chapters share an identical section body (after replacing each
     chapter's own title), which is how templated filler is caught.
  4. Every relative .md link resolves to an existing file (all .md files in
     the folder, not only chapters).

Exit code is 1 if any check fails.
"""

from __future__ import annotations

import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_SECTIONS = [
    "## ⏱ If You Only Have 2 Minutes",
    "## 1. What It Is and Why It Exists",
    "## 2. How It Works",
    "## 3. Key Concepts",
    "## 4. Code Examples",
    "## 5. Production Concerns",
    "## 6. Common Mistakes",
    "## 8. Interview Questions",
    "## 9. Cheat Sheet",
    "## Related Topics",
]
CHAPTER_RE = re.compile(r"^\d{2}-.+\.md$")
LINK_RE = re.compile(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)")
CODE_FENCE_RE = re.compile(r"^```(\w+)", re.M)
MIN_DUP_LENGTH = 120  # ignore tiny bodies such as a single shared link


def split_sections(text: str) -> dict[str, str]:
    """Map each '## ' heading to its body, ignoring '## ' lines inside code fences."""
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            current = sections.setdefault(line.strip(), [])
            continue
        if current is not None:
            current.append(line)
    return {heading: "\n".join(body).strip() for heading, body in sections.items()}


def check_module(folder: Path, errors: list[str], seen: dict[str, list[str]]) -> int:
    chapters = sorted(p for p in folder.iterdir() if CHAPTER_RE.match(p.name))
    for path in chapters:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text else ""
        sections = split_sections(text)

        for required in REQUIRED_SECTIONS:
            if required not in sections:
                errors.append(f"{rel}: missing section '{required}'")

        code = sections.get("## 4. Code Examples", "")
        langs = {lang.lower() for lang in CODE_FENCE_RE.findall(code)}
        if not langs & {"ts", "typescript"}:
            errors.append(f"{rel}: section 4 has no ```ts code block")
        if not langs & {"python", "py"}:
            errors.append(f"{rel}: section 4 has no ```python code block")

        for heading, body in sections.items():
            normalized = body.replace(title, "TITLE").replace(title.lower(), "title")
            if len(normalized) < MIN_DUP_LENGTH:
                continue
            digest = hashlib.sha1(normalized.encode()).hexdigest()
            seen[f"{heading}|{digest}"].append(rel)

    for path in sorted(folder.glob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://")):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"{rel}: broken link -> {target}")
    return len(chapters)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    folders = sorted(ROOT.glob("Module-*")) if argv == ["--all"] else [ROOT / a for a in argv]

    errors: list[str] = []
    seen: dict[str, list[str]] = defaultdict(list)
    total = 0
    for folder in folders:
        if not folder.is_dir():
            errors.append(f"{folder}: not a directory")
            continue
        total += check_module(folder, errors, seen)

    for key, files in seen.items():
        if len(files) > 1:
            heading = key.split("|", 1)[0]
            errors.append(f"identical '{heading}' body in {len(files)} chapters: {', '.join(files[:5])}"
                          + (" ..." if len(files) > 5 else ""))

    for line in errors:
        print("FAIL", line)
    print(f"\nChecked {total} chapters in {len(folders)} module(s): {len(errors)} problem(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
