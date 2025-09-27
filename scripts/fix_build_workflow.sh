#!/bin/bash
# Quick fix to make build.yml work for direct pushes too

echo "=== Fixing build.yml to work with direct pushes ==="
echo ""
echo "The build workflow currently only runs contracts on PRs."
echo "This change will make it run on both PRs and direct pushes."
echo ""

# Create the fixed version
cat > .github/workflows/build.yml.fixed << 'EOF'
name: CI

on:
  pull_request:
    paths:
      - "api/**"
      - "api/admin_ui/**"
      - "config/**"
      - ".github/workflows/**"
      - "Dockerfile*"
  push:
    branches: [ "**" ]

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      ui:  ${{ steps.filter.outputs.ui }}
      docs: ${{ steps.filter.outputs.docs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'api/**'
              - 'Dockerfile'
            ui:
              - 'api/admin_ui/**'
              - 'api/admin_ui/Dockerfile'
            docs:
              - 'docs/**'
              - 'config/provider_traits.json'

  contracts:
    needs: changes
    # FIXED: Run on both PRs and pushes to auto-tunnel/development
    if: ${{ github.event_name == 'pull_request' || (github.event_name == 'push' && (github.ref == 'refs/heads/auto-tunnel' || github.ref == 'refs/heads/development')) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Python deps for OpenAPI generation
        run: |
          python -m pip install --upgrade pip
          pip install -r api/requirements.txt
      - name: Install jsonschema
        run: |
          python -m pip install --upgrade pip
          pip install jsonschema
      - name: Install ripgrep for contract greps
        run: |
          sudo apt-get update
          sudo apt-get install -y ripgrep
      - name: Validate provider traits
        run: |
          python scripts/ci/validate_provider_traits.py
      - name: Generate OpenAPI (FastAPI app.openapi)
        run: |
          python - << 'PY'
          import os, sys, json
          sys.path.insert(0, 'api')
          os.environ.setdefault('FAXBOT_TEST_MODE', 'true')
          os.environ.setdefault('FAX_DISABLED', 'true')
          os.environ.setdefault('DATABASE_URL', 'sqlite:///./test_openapi_ci_build.yml.db')
          from app.main import app
          spec = app.openapi()
          with open('openapi.json', 'w') as f:
              json.dump(spec, f, indent=2)
          print('✅ Generated openapi.json')
          PY
      - name: Diff against pinned snapshot (if present)
        run: |
          if [ -f docs/pinned-openapi.json ]; then
            echo "Pinned snapshot found. Running diff..."
            python scripts/ci/diff_openapi.py || (echo "OpenAPI drift" && exit 1)
          else
            echo "No pinned snapshot at docs/pinned-openapi.json; skipping diff (green)."
          fi
      - name: Contract greps
        run: bash scripts/ci/greps.sh

  build-api:
    needs: [changes, contracts]
    if: needs.changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Buildx
        uses: docker/setup-buildx-action@v3
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build API with cache
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: false
          tags: ghcr.io/${{ toLower(github.repository_owner) }}/faxbot-api:pr-${{ github.run_id }}
          cache-from: type=registry,ref=ghcr.io/${{ toLower(github.repository_owner) }}/faxbot-api:cache
          cache-to:   type=registry,ref=ghcr.io/${{ toLower(github.repository_owner) }}/faxbot-api:cache,mode=max
          build-args: |
            BUILDKIT_INLINE_CACHE=1

  build-ui:
    needs: [changes, contracts]
    if: needs.changes.outputs.ui == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: 'npm'
          cache-dependency-path: api/admin_ui/package-lock.json
      - name: Install UI deps
        working-directory: api/admin_ui
        run: npm ci --prefer-offline --no-audit
      - name: Typecheck + build
        working-directory: api/admin_ui
        run: npm run build
EOF

echo "Fixed version created at .github/workflows/build.yml.fixed"
echo ""
echo "The change: contracts job will now run on:"
echo "  - All pull requests (as before)"
echo "  - Direct pushes to auto-tunnel branch"
echo "  - Direct pushes to development branch"
echo ""
echo "To apply this fix:"
echo "  mv .github/workflows/build.yml.fixed .github/workflows/build.yml"
echo "  git add .github/workflows/build.yml"
echo "  git commit -m 'fix(ci): Allow build workflow to run on direct pushes to auto-tunnel'"
echo "  git push"
