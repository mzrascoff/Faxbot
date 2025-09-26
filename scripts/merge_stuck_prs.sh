#!/bin/bash
# Script to merge all stuck feature branches into auto-tunnel
# CRITICAL: This is for a production HIPAA system - ensure all changes are preserved

set -e

echo "=== Starting systematic merge of stuck PRs ==="
echo "Working on auto-tunnel branch..."

# Ensure we're on auto-tunnel and up to date
git checkout auto-tunnel
git pull origin auto-tunnel

# List of stuck feature branches (from git branch -r --no-merged origin/auto-tunnel)
BRANCHES=(
  "feat/p2-01-02-05-scaffold"
  "feat/p4-marketplace-api"
  "feat/p4-marketplace-fetch"
  "feat/p4-marketplace-install-stub"
  "feat/p4-marketplace-ui"
  "feat/p4-marketplace-wiring"
  "feat/p4-runbook"
  "feat/p4-webhooks-scaffold"
  "feat/p5-async-sinch-uploads"
  "feat/pr13-config-db-models"
  "feat/pr14-hierarchical-ui"
  "feat/pr16-provider-circuit-breaker"
  "feat/pr17-webhook-dlq"
)

# Counter for successful merges
MERGED=0
FAILED=0

# Process each branch
for BRANCH in "${BRANCHES[@]}"; do
  echo ""
  echo "=== Processing branch: $BRANCH ==="
  
  # Check if branch exists on remote
  if ! git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
    echo "Branch $BRANCH doesn't exist on remote, skipping..."
    continue
  fi
  
  # Create a local branch tracking the remote
  git checkout -B "merge-$BRANCH" "origin/$BRANCH"
  
  # Try to rebase onto auto-tunnel to resolve conflicts automatically
  echo "Attempting to rebase $BRANCH onto auto-tunnel..."
  if git rebase origin/auto-tunnel; then
    echo "✓ Rebase successful for $BRANCH"
    
    # Switch back to auto-tunnel and merge
    git checkout auto-tunnel
    if git merge --ff-only "merge-$BRANCH"; then
      echo "✓ Merged $BRANCH into auto-tunnel"
      ((MERGED++))
      
      # Delete the temporary local branch
      git branch -D "merge-$BRANCH"
      
      # Push the merge
      echo "Pushing merged changes..."
      git push origin auto-tunnel
      
      # Delete the remote feature branch since it's merged
      echo "Deleting remote branch $BRANCH..."
      git push origin --delete "$BRANCH" || true
    else
      echo "✗ Failed to fast-forward merge $BRANCH"
      ((FAILED++))
      git branch -D "merge-$BRANCH"
    fi
  else
    echo "✗ Rebase failed for $BRANCH - manual intervention needed"
    ((FAILED++))
    
    # Abort the rebase
    git rebase --abort
    
    # Clean up
    git checkout auto-tunnel
    git branch -D "merge-$BRANCH"
  fi
done

echo ""
echo "=== Merge Summary ==="
echo "Successfully merged: $MERGED branches"
echo "Failed to merge: $FAILED branches"

# Final push to ensure everything is up
echo "Final push to ensure all changes are on remote..."
git push origin auto-tunnel

echo "Done!"
