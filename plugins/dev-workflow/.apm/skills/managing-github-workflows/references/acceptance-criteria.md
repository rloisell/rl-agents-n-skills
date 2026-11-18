# Acceptance Criteria — managing-github-workflows

Observable pass/fail criteria for verifying branch-first PR lifecycle, conventional commits, GitHub Rulesets, and CI diagnosis.

## Branching, Commits & PR Lifecycle

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Branch-first workflow | All changes are committed on a `<type>/<short-slug>` branch (<= 40 chars), never directly to `main` | Direct commits pushed to `main` or non-conventional branch names |
| Conventional commits | Commit messages follow `<type>: <imperative description>` (<= 72 chars) | Commit messages lack conventional type prefix or exceed 72-char subject |
| PR creation & merge | PR targets `main` via `gh pr create`, passes all required checks, and merges via `gh pr merge --squash --delete-branch` | PR merged with failing checks or feature branch left undeleted |
| Local `main` sync | After merge, local `main` is checked out and fast-forwarded (`git pull origin main`) | Local `main` remains behind remote after merge |

## Rulesets, CI Diagnosis & Compliance

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Ruleset job matching | Required status check names in GitHub Rulesets match the workflow job's `name:` field (not YAML job ID) | Ruleset references YAML job ID when `name:` differs, causing stuck checks |
| CI failure diagnosis | Failed run ID is fetched via `gh run list` and inspected with `gh run view <id> --log-failed` | Guessing at CI failures without inspecting failed step logs |
| BC Gov OCIO §2.1 & OSS | Public-sector Open Source repos satisfy OCIO §2.1 and OSS guidelines (LICENSE, README, SECURITY, etc.) | Public-sector repo omits required OCIO §2.1 governance files |

## Scope Boundaries

- **Trigger**: Branch creation, conventional commits, PR creation/merging, GitHub Rulesets, or CI failure diagnosis.
- **Do not trigger**: Session `AI/` file logging (`managing-dev-sessions`) or architecture diagramming (`documenting-architecture`).
