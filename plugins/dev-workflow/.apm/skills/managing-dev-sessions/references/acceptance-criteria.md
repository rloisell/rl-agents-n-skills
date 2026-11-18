# Acceptance Criteria — managing-dev-sessions

Observable pass/fail criteria for verifying session startup orientation and shutdown audit-trail discipline.

## Startup Protocol

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Orientation read order | `AI/nextSteps.md`, `CODING_STANDARDS.md`, and `docs/deployment/DeploymentAnalysis.md` (if present) are read; opening states current status in one sentence | Session starts coding without reading `AI/nextSteps.md` or summarizing state |
| Git & stale change check | `git status` and `git log --oneline -5` are run; user is asked before stashing, committing, or discarding uncommitted work | Prior uncommitted changes are silently overwritten or discarded |
| Dependabot PR triage | Open Dependabot PRs are listed via `gh pr list --state open --author app/dependabot` and unrecorded PRs added to `AI/nextSteps.md` | Open Dependabot PRs are ignored or omitted from `AI/nextSteps.md` |
| Branch discipline | Active work switches off `main` to a feature branch before editing files | Files are edited directly on `main` |
| Past knowledge recall | Branch/feature topic is scanned against skills and evolution logs before implementing | Past knowledge scan is skipped |

## Shutdown Protocol

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| `AI/` audit files updated | `AI/WORKLOG.md`, `AI/CHANGES.csv`, `AI/COMMANDS.sh`, and `AI/COMMIT_INFO.txt` match required schemas | Any of the four `AI/` audit files is missing or out of date |
| `AI/nextSteps.md` current | Completed items are marked done and newly discovered tasks are recorded | `AI/nextSteps.md` reflects stale session state |
| `agent-evolution` invoked | `agent-evolution` runs and logs discoveries or "no new patterns" | Session closes without running `agent-evolution` |
| Remote push verified | `git log --oneline origin/$(git branch --show-current)..HEAD` is empty | Local commits remain unpushed at session end |

## Scope Boundaries

- **Trigger**: Session startup orientation, session shutdown wrap-up, or `AI/` audit file schema questions.
- **Do not trigger**: GitHub Ruleset configuration (`managing-github-workflows`) or Spec-Kit authoring (`driving-spec-development`).
