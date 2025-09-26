#!/bin/bash
# Auto-cleanup unused branches without prompting

set -e

echo "=== Auto Branch Cleanup - Removing AI Agent Mess ==="
echo ""

# Branches to DELETE (AI cruft and old stuff)
DELETE_BRANCHES=(
  # AI-generated documentation branches (ugh, why do they do this?)
  "docs/ai-update-17922848900"
  "docs/ai-update-17922882760"
  "docs/ai-update-17922928937"
  "docs/ai-update-17923436133"
  "update-admin-demo-20250921-010332"
  
  # Old/completed work
  "chore/disable-redocly-check"
  "backup-pre-rollback"
  "emergency-rollback-2025-09-15"
  "docs-jekyll-site-backup-d4579de"
  
  # Old feature branches that were never cleaned up
  "feat/pr9-admin-config-test"
  "feat/pr17-config-write"
  "feature/signalwire-freeswitch"
  "hybrid-refactor"
  "rebrand-assets"
  
  # Documentation experiments
  "docs-jekyll-site"
  "mkdocs"
)

DELETED=0
SKIPPED=0

for branch in "${DELETE_BRANCHES[@]}"; do
  echo -n "🗑️  Deleting $branch... "
  if git push origin --delete "$branch" 2>/dev/null; then
    echo "✅ Deleted!"
    ((DELETED++))
  else
    echo "⏭️  Already gone"
    ((SKIPPED++))
  fi
done

echo ""
echo "=== 🎉 Cleanup Complete! ==="
echo "✅ Deleted: $DELETED branches"
echo "⏭️  Already gone: $SKIPPED branches"
echo ""
echo "=== Remaining Branches (the ones we want) ==="
git branch -r | grep -v HEAD | sed 's/origin\//  /'
echo ""
echo "Much cleaner! No more visual clutter from agent-created branches! 🧹"
