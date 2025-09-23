#!/usr/bin/env bash
set -euo pipefail

# Compare docs trees between two branches (defaults: development vs mkdocs)
# Usage: scripts/docs_tools/compare_docs_trees.sh [branch_a] [branch_b]

BR_A="${1:-development}"
BR_B="${2:-mkdocs}"

if ! git rev-parse --verify "$BR_A" >/dev/null 2>&1; then
  echo "Branch not found: $BR_A" >&2
  exit 2
fi
if ! git rev-parse --verify "$BR_B" >/dev/null 2>&1; then
  echo "Branch not found: $BR_B" >&2
  exit 2
fi

tmp_a=$(mktemp)
tmp_b=$(mktemp)
trap 'rm -f "$tmp_a" "$tmp_b"' EXIT

git ls-tree -r --name-only "$BR_A":docs | sort > "$tmp_a"
git ls-tree -r --name-only "$BR_B":docs | sort > "$tmp_b"

echo "Only in $BR_A (not in $BR_B):"
comm -23 "$tmp_a" "$tmp_b" || true
echo
echo "Only in $BR_B (not in $BR_A):"
comm -13 "$tmp_a" "$tmp_b" || true

