8-step PR loop (repeat per prompt)

Branch off auto-tunnel:

git checkout auto-tunnel && git pull
git checkout -b feat/prX-short-title


Run the Codex prompt for that PR (PR0, PR1, PR2…); let it edit only the listed files.

Commit small, atomic diffs:

git add -A && git commit -m "PRX: <short summary>"


Local smoke + checks (from the prompt):

bash scripts/ci/greps.sh || true
docker compose build && docker compose up -d
curl -fsS http://localhost:8080/health || true


Push & open PR targeting auto-tunnel:

git push -u origin HEAD
# with GitHub CLI (optional)
gh pr create -B auto-tunnel -t "PRX: <title>" -b "Implements PRX… (include acceptance greps + smoke outputs)"


Require green CI (must pass): OpenAPI diff, traits schema validation, greps, tests.

Merge (recommend “Squash and merge” for a linear history). Delete the feature branch.

Sanity run after merge:

git checkout auto-tunnel && git pull
docker compose build && docker compose up -d

Branch policy (answering your last Q directly)

All PRs target auto-tunnel (base branch = auto-tunnel).

Keep auto-tunnel protected: require CI checks to pass; no direct pushes.

After a milestone (e.g., PR0–PR5 merged and stable), open one PR from auto-tunnel → development and merge that too. Never touch main.

“Definition of Done” per PR

✅ CI green (OpenAPI diff, traits schema, greps, tests)

✅ Docker smoke: /health, /metrics, /admin/providers respond, no route renames

✅ For webhook PRs: 202 returned and idempotency confirmed (duplicate returns 202, no reprocess)

✅ For UI PRs: no provider name checks remain; traits drive the view

Rollback snippet (if something slips)
# revert the merge commit of the bad PR on auto-tunnel
git checkout auto-tunnel && git pull
git log --oneline   # copy the merge commit SHA
git revert -m 1 <merge-commit-sha>
git push


Use the three prompts I gave (PR0–PR2) exactly as-is, one by one, with this loop. When those are merged, use the next set (PR3–PR5), same loop.