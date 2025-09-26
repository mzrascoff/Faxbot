# ⚠️ AGENT BRANCH POLICY - STOP MAKING A MESS! ⚠️

## FOR ALL AI AGENTS WORKING ON THIS REPO

### 🚫 STOP DOING THIS:
- Creating branches for 2-second fixes
- Leaving branches after merging
- Creating branches with timestamps like `ai-update-17922848900`
- Making separate branches for every tiny change

### ✅ DO THIS INSTEAD:

#### For Quick Fixes (< 5 lines):
```bash
# Just commit directly to the working branch if it's a fix
git add <files>
git commit -m "fix: <description>"
git push
```

#### For Feature Work:
```bash
# Create a descriptive branch
git checkout -b feat/<actual-feature-name>

# When done and merged, DELETE IT:
git push origin --delete feat/<actual-feature-name>
```

#### For Documentation Updates:
```bash
# DON'T create a new branch! Just update in place:
git add docs/
git commit -m "docs: <what you updated>"
git push
```

### 🧹 CLEANUP AFTER YOURSELF:

After ANY PR is merged:
```bash
# Delete the remote branch
git push origin --delete <branch-name>

# Delete local branch
git branch -d <branch-name>
```

### 📏 BRANCH NAMING RULES:
- ✅ GOOD: `feat/user-auth`, `fix/ci-grep`, `docs/api-update`
- ❌ BAD: `ai-update-17922848900`, `update-20240921-010332`, `temp`, `test`

### 🎯 PERMANENT BRANCHES (DO NOT DELETE):
- `main` - Production
- `development` - Staging
- `auto-tunnel` - V4 development
- `electron_*` - Platform-specific apps
- `iOS` - iOS app
- `gh-pages` - Documentation site

### 🤖 AI AGENT SPECIFIC RULES:
1. **One branch per session** - Don't create multiple branches in one conversation
2. **Delete when done** - Always include branch deletion in your workflow
3. **No timestamp branches** - We can see when you made changes in git history
4. **Work in existing branches when possible** - Especially for small fixes

## Cleanup Script

If branches accumulate again, run:
```bash
./scripts/cleanup_branches_auto.sh
```

---

**Remember**: Every branch you leave behind annoys the human developer. Be considerate! 🙏
