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

## Epistemic Labeling

Label material facts in session notes, handoffs, and user confirmations by
evidence strength:

| Label | Meaning | Rule |
|---|---|---|
| `Verified` | Directly observed in source, command output, or tool response | Cite the file, command, or check |
| `Inferred` | Reasoned from partial or indirect evidence | Confirm with user or inspect source before irreversible writes |
| `Unknown` | Not observed or unverifiable in current context | State the gap explicitly; never present as `Verified` |

Never raise a confidence label without new direct evidence or explicit user
confirmation.

## Multi-Agent Single-Writer Ownership and Bounded Retries

When coordinating multiple agents or parallel workers in a session:

1. **Single-writer ownership**: assign exactly one owner per output file or
   shared contract. Parallel read-only evidence workers may run concurrently
   only when their declared write paths are disjoint.
2. **Dependency ordering**: consumers wait for verified prerequisites and
   required sign-offs; workers report cross-scope issues to the coordinator
   rather than editing another owner's file.
3. **Bounded retry contract**: give each worker a terminal deliverable and a
   finite review/retry budget. If the retry limit is exhausted, pause and
   surface the blocker rather than entering unsolicited peer-update loops or
   weakening acceptance checks.
