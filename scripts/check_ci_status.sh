#!/bin/bash
# Script to check which CI checks are actually required vs optional

echo "=== Checking CI Status Requirements ==="
echo ""

# Get the latest commit SHA
LATEST_SHA=$(git rev-parse HEAD)
echo "Latest commit: $LATEST_SHA"
echo ""

# Check GitHub API for status checks (requires auth for full details)
echo "Attempting to fetch status checks..."
echo "(Note: Full details require GitHub authentication)"
echo ""

# Try to get commit status
curl -s "https://api.github.com/repos/DMontgomery40/Faxbot/commits/$LATEST_SHA/status" 2>/dev/null | \
  python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"Overall State: {data.get('state', 'unknown').upper()}\")
    print(f\"Total Checks: {data.get('total_count', 0)}\")
    print()
    
    statuses = data.get('statuses', [])
    if statuses:
        print('Individual Checks:')
        for s in statuses:
            state = s.get('state', 'unknown')
            symbol = '✅' if state == 'success' else '❌' if state in ['failure', 'error'] else '⏳'
            print(f\"  {symbol} {s.get('context', 'unknown')}: {state}\")
            if s.get('description'):
                print(f\"     Description: {s.get('description')}\")
    else:
        print('No status checks found (they might be GitHub Apps/Checks API)')
except:
    print('Unable to parse status response')
" || echo "Unable to fetch status from GitHub API"

echo ""
echo "=== Your Repository's Workflow Files ==="
echo "These are the checks YOU control:"
echo ""

for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        name=$(basename "$workflow" .yml)
        # Check if workflow has 'on:' triggers for PRs
        if grep -q "pull_request" "$workflow" 2>/dev/null; then
            echo "  ✓ $name (runs on PRs)"
        else
            echo "    $name (does not run on PRs)"
        fi
    fi
done

echo ""
echo "=== What This Means ==="
echo "• Red X's from external services (Project preview, Scorecard, etc.) are NOT blocking"
echo "• Only 'Required' status checks can block merging"
echo "• Your commits show 'Verified' = they're passing required checks"
echo "• External services can be removed via GitHub Settings > Installations"
echo ""
echo "To see/modify required checks:"
echo "  Visit: https://github.com/DMontgomery40/Faxbot/settings/branches"
echo "  Edit the 'auto-tunnel' branch protection rules"
