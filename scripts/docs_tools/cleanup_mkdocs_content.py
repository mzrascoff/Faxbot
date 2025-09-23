#!/usr/bin/env python3
"""
Cleanup MkDocs content migrated from Jekyll:
- Strip Jekyll front matter (--- ... --- at file start)
- Normalize internal links from Jekyll-era slugs to MkDocs paths
- Remove Liquid variables like {{ site.baseurl }}

Usage:
  python scripts/docs_tools/cleanup_mkdocs_content.py [docs_dir] [--dry-run]

Defaults:
  docs_dir = ./docs
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def strip_front_matter(text: str) -> tuple[str, bool]:
    if text.startswith("---\n"):
        # Find the closing '---' after the first line
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :], True
    return text, False


REPLACEMENTS = [
    # (pattern, replacement)
    (re.compile(r"\{\{\s*site\.baseurl\s*\}\}"), ""),
    # Common old slugs → new MkDocs paths
    (re.compile(r"\((?:https?://[^\)]*)?/api-docs\.html\)"), "(https://faxbot.net/api/v1/)"),
    (re.compile(r"\((?:/)?backends/phaxio-setup/?\)"), "(go-live/phaxio.md)"),
    (re.compile(r"\((?:/)?backends/sinch-setup/?\)"), "(go-live/sinch.md)"),
    (re.compile(r"\((?:/)?backends/sip-setup/?\)"), "(go-live/sip-asterisk.md)"),
    (re.compile(r"\((?:/)?ai-integration/?\)"), "(mcp/index.md)"),
    # Development SDK links
    (re.compile(r"\((?:/)?development/node-sdk\.html\)"), "(sdks/node.md)"),
    (re.compile(r"\((?:/)?development/python-sdk\.html\)"), "(sdks/python.md)"),
    # Admin console and getting started
    (re.compile(r"\((?:/)?admin-console/\)"), "(admin-console.md)"),
    (re.compile(r"\((?:/)?getting-started/\)"), "(getting-started.md)"),
    # Old security deep-links from GitHub Pages folder structure
    (re.compile(r"\((?:/)?Faxbot/security/authentication\.html\)"), "(security/authentication.md)"),
    (re.compile(r"\((?:/)?Faxbot/security/oauth-setup\.html\)"), "(security/oauth-setup.md)"),
]


def rewrite_links(text: str) -> tuple[str, int]:
    count = 0
    for pattern, repl in REPLACEMENTS:
        new_text, n = pattern.subn(repl, text)
        if n:
            text = new_text
            count += n
    return text, count


def process_file(path: Path, dry_run: bool = False) -> tuple[bool, str]:
    original = path.read_text(encoding="utf-8")
    updated, fm_removed = strip_front_matter(original)
    updated, replaced = rewrite_links(updated)

    if updated != original:
        if not dry_run:
            path.write_text(updated, encoding="utf-8")
        return True, (
            f"updated (front-matter removed={fm_removed}, replacements={replaced})"
        )
    return False, "no changes"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("docs_dir", nargs="?", default="docs")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"Docs directory not found: {docs_dir}", file=sys.stderr)
        return 2

    changed = 0
    scanned = 0
    for md in docs_dir.rglob("*.md"):
        scanned += 1
        did_change, msg = process_file(md, dry_run=args.dry_run)
        if did_change:
            changed += 1
            rel = md.relative_to(docs_dir)
            print(f"[CHANGED] {rel}: {msg}")

    print(f"Scanned {scanned} markdown files; changed {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
