# Process Knowledge

Session process rules, startup recall queries, and accumulated process findings.

## Process Rules

1. **Never skip startup orientation**: `AI/nextSteps.md` is the cross-session memory.
2. **Branch before code**: `main` is protected; create a feature branch before any file change.
3. **Log everything**: `WORKLOG.md`, `CHANGES.csv`, `COMMANDS.sh`, and `COMMIT_INFO.txt` form the audit trail.
4. **One session = one commit set**: do not accumulate uncommitted work across sessions.
5. **Ask about stale changes**: never silently overwrite or discard uncommitted work.
6. **End every session with a push**: verify `git log origin/<branch>..HEAD` is empty before closing.

## Pre-Session Knowledge Recall

Before implementation begins, scan installed skills and the evolution log for
entries matching the active feature or branch topic:

```bash
TOPIC="<branch-name-or-feature-keyword>"
grep -ril "$TOPIC" .apm/skills/ --include="SKILL.md" --include="*.md"
```

Summarize any matches in one sentence before proceeding.

## Dependabot Triage Order

Review and merge open Dependabot PRs in risk order:

1. GitHub Actions version bumps (lowest risk)
2. Backend package minor/patch updates (review changelog, merge on green CI)
3. Frontend package minor/patch updates (`npm audit` locally, merge on green CI)
4. Major version bumps (require manual verification)

## Recorded Findings

- 2026-02-27: [sample-app] [CONTEXT: ci-cd] Main branch is protected via GitHub Ruleset (`<ruleset-id>`). All changes must go through PRs with required status checks passing.
