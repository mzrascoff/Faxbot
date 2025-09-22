#!/bin/bash
# Build docs for all branches

for branch in main development hybrid-refactor auto-tunnel; do
    echo "Building docs for $branch..."
    git checkout $branch
    
    # Create branch-specific config
    cat > _config.$branch.yml << CONFIG
baseurl: /$branch
branch_name: $branch
CONFIG
    
    # Build to branch subdirectory
    bundle exec jekyll build --config _config.yml,_config.$branch.yml -d _site/$branch/
done

# Go back to docs branch
git checkout docs-jekyll-branch

echo "All branches built successfully!"
echo "Access them at:"
echo "  https://docs.faxbot.net/main"
echo "  https://docs.faxbot.net/development"
echo "  https://docs.faxbot.net/hybrid-refactor"
echo "  https://docs.faxbot.net/auto-tunnel"
