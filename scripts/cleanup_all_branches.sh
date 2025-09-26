#!/bin/bash
# Clean up unused branches left by AI agents and old work

set -e

echo "=== Comprehensive Branch Cleanup ==="
echo ""

# Branches to KEEP (important ones)
KEEP_BRANCHES=(
  "main"
  "master"
  "development"
  "auto-tunnel"
  "electron_linux"
  "electron_macos" 
  "electron_windows"
  "iOS"
  "gh-pages"  # GitHub Pages
)

# Branches to definitely DELETE (AI cruft and old stuff)
DELETE_BRANCHES=(
  # AI-generated documentation branches
  "docs/ai-update-17922848900"
  "docs/ai-update-17922882760"
  "docs/ai-update-17922928937"
  "docs/ai-update-17923436133"
  "update-admin-demo-20250921-010332"
  
  # Old/completed work
  "chore/disable-redocly-check"  # Already merged
  "backup-pre-rollback"
  "emergency-rollback-2025-09-15"
  "docs-jekyll-site-backup-d4579de"
  
  # Old feature branches
  "feat/pr9-admin-config-test"
  "feat/pr17-config-write"
  "feature/signalwire-freeswitch"
  "hybrid-refactor"
  "rebrand-assets"
  
  # Documentation experiments
  "docs-jekyll-site"
  "mkdocs"
)

echo "Branches to KEEP:"
for branch in "${KEEP_BRANCHES[@]}"; do
  echo "  ✓ $branch"
done

echo ""
echo "Branches to DELETE:"
for branch in "${DELETE_BRANCHES[@]}"; do
  echo "  ✗ $branch"
done

echo ""
read -p "Proceed with deletion? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "Deleting branches..."
echo ""

DELETED=0
FAILED=0

for branch in "${DELETE_BRANCHES[@]}"; do
  echo -n "Deleting $branch... "
  if git push origin --delete "$branch" 2>/dev/null; then
    echo "✓"
    ((DELETED++))
  else
    echo "✗ (already deleted or doesn't exist)"
    ((FAILED++))
  fi
done

echo ""
echo "=== Cleanup Summary ==="
echo "Deleted: $DELETED branches"
echo "Skipped: $FAILED branches (already deleted or don't exist)"
echo ""

# Show remaining branches
echo "=== Remaining Branches ==="
git branch -r | grep -v "HEAD" | sed 's/origin\///' | while read branch; do
  is_kept=false
  for keep in "${KEEP_BRANCHES[@]}"; do
    if [[ "$branch" == *"$keep"* ]]; then
      is_kept=true
      break
    fi
  done
  
  if $is_kept; then
    echo "  ✓ $branch (intentionally kept)"
  else
    echo "  ? $branch (review if needed)"
  fi
done

echo ""
echo "Done! Your repo is much cleaner now."
echo ""
echo "Tip: To prevent this in the future, remind agents to:"
echo "  1. Use --no-push for quick fixes"
echo "  2. Delete branches after merging"
echo "  3. Use descriptive branch names with dates for cleanup"
