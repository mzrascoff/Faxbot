#!/usr/bin/env python3
"""
Mirror Markdown files from another branch into mkdocs/docs with front-matter removal
and basic link normalization, to achieve content parity with legacy docs.

Usage:
  python scripts/docs_tools/mirror_from_branch.py --branch docs-jekyll-site

This script is intentionally opinionated for Faxbot and includes a baked-in mapping.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import re


def git_show(branch: str, path: str) -> str:
    cp = subprocess.run(["git", "show", f"{branch}:{path}"], capture_output=True, text=True)
    if cp.returncode != 0:
        raise RuntimeError(f"git show failed for {branch}:{path}: {cp.stderr.strip()}")
    return cp.stdout


def strip_front_matter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :]
    return text


REPLACEMENTS = [
    (re.compile(r"\{\{\s*site\.baseurl\s*\}\}"), ""),
]


def normalize(text: str) -> str:
    for pat, repl in REPLACEMENTS:
        text = pat.sub(repl, text)
    return text


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    branch = "docs-jekyll-site"
    if "--branch" in sys.argv:
        try:
            branch = sys.argv[sys.argv.index("--branch") + 1]
        except Exception:
            print("--branch requires a value", file=sys.stderr)
            return 2

    mappings = [
        # Admin Console
        ("admin-console/index.md", "docs/admin-console.md"),
        ("admin-console/api-keys.md", "docs/admin-console/api-keys.md"),
        ("admin-console/settings.md", "docs/admin-console/settings.md"),
        ("admin-console/diagnostics.md", "docs/admin-console/diagnostics.md"),
        ("admin-console/diagnostics-matrix.md", "docs/admin-console/diagnostics-matrix.md"),
        ("admin-console/plugin-builder.md", "docs/admin-console/plugin-builder.md"),
        ("admin-console/annotated-demo.md", "docs/admin-console/annotated-demo.md"),
        ("admin-console/setup-wizard.md", "docs/admin-console/setup-wizard.md"),
        # Plugins
        ("plugins/index.md", "docs/plugins/index.md"),
        ("plugins/registry.md", "docs/plugins/registry.md"),
        ("plugins/manifest-http.md", "docs/plugins/manifest-http.md"),
        ("plugins/sip-provider-plugins.md", "docs/plugins/sip-provider-plugins.md"),
        ("plugins/config-file.md", "docs/plugins/config-file.md"),
        ("plugins/homeassistant.md", "docs/plugins/homeassistant.md"),
        # Setup helpers / backends extras
        ("backends/public-access.md", "docs/setup/public-access.md"),
        ("backends/webhooks.md", "docs/setup/webhooks.md"),
        ("backends/images-and-pdfs.md", "docs/guides/images-and-pdfs.md"),
        ("backends/freeswitch-setup.md", "docs/setup/freeswitch.md"),
        ("backends/signalwire-setup.md", "docs/setup/signalwire.md"),
        ("backends/documo-setup.md", "docs/setup/documo.md"),
        ("backends/test-mode.md", "docs/setup/test-mode.md"),
        # Tools / Troubleshooting / SDKs
        ("development/scripts-and-tests.md", "docs/tools/scripts-and-tests.md"),
        ("development/troubleshooting.md", "docs/troubleshooting.md"),
        ("development/node-sdk.md", "docs/sdks/node.md"),
        ("development/python-sdk.md", "docs/sdks/python.md"),
    ]

    written = 0
    for src, dst in mappings:
        try:
            raw = git_show(branch, src)
        except RuntimeError as e:
            print(f"[SKIP] {src}: {e}")
            continue
        content = normalize(strip_front_matter(raw))
        write_file(Path(dst), content)
        print(f"[WROTE] {dst} (from {branch}:{src})")
        written += 1

    print(f"Mirrored {written} files from {branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

