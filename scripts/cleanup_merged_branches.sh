#!/bin/bash
# Check if PR branches are already merged and clean them up

set -e

echo "=== Checking remaining PR branches for already-merged content ==="

# Branches to check
BRANCHES=(
  "feat/pr14-config-provider"
  "feat/pr16-config-manager"
  "feat/pr17-config-write"
  "feat/pr18-events-sse"
  "feat/pr6-typed-bases"
  "feat/pr7-send-idempotency"
  "feat/pr8-storage-plugins"
)

for BRANCH in "${BRANCHES[@]}"; do
  echo ""
  echo "Checking $BRANCH..."
  
  # Extract PR number
  PR_NUM=$(echo "$BRANCH" | sed -E 's/.*pr([0-9]+).*/\1/')
  
  # Check if PR is already in commit history
  if git log --oneline | grep -i "PR${PR_NUM}:" > /dev/null 2>&1; then
    echo "✓ PR${PR_NUM} is already merged in commit history"
    echo "  Deleting remote branch $BRANCH..."
    git push origin --delete "$BRANCH" || echo "  (already deleted or failed)"
  else
    echo "? PR${PR_NUM} not found in commit history - needs investigation"
  fi
done

echo ""
echo "=== Cleanup complete ==="
