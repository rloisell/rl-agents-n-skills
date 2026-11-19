---
name: managing-dev-sessions
description: >-
  Governs startup and shutdown discipline for AI-assisted development sessions,
  including orientation files, git state checks, Dependabot PR triage, past
  knowledge recall, and AI/ audit trail maintenance. Use at the start and end
  of every development session or when asked about session process and AI
  collaboration files.
---

# Managing Dev Sessions

Enforces consistent startup and shutdown discipline across development sessions
so context persists across stateless AI invocations.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Never skip startup orientation**: `AI/nextSteps.md` is the authoritative session state.
2. **Branch before code**: `main` is protected; switch to or create a feature branch before editing files.
3. **Ask about stale changes**: never silently overwrite or discard uncommitted work from a prior session.
4. **Log everything**: maintain `AI/WORKLOG.md`, `AI/CHANGES.csv`, `AI/COMMANDS.sh`, and `AI/COMMIT_INFO.txt`.
5. **End every session with a push**: nothing should remain local-only at session end.
6. **Label evidence honestly**: distinguish `Verified`, `Inferred`, and `Unknown` facts, and enforce single-writer ownership in multi-agent sessions per [process-knowledge.md](references/process-knowledge.md).

## Quick start

Read `AI/nextSteps.md`, `CODING_STANDARDS.md`, and `git status`, then open with
one sentence summarizing the current state before starting work.

## Workflow

### Startup protocol

Run silently at session start (note any missing files and continue):

1. **Orientation (read in order)**:
   - `AI/nextSteps.md` — active TODOs and carry-over state
   - `CODING_STANDARDS.md` — project conventions and AI guardrails
   - `.workbench/project.config.yaml` or `crow.config` — public-safe project manifest (if present; see [project-context-manifest.md](references/project-context-manifest.md))
   - `docs/deployment/DeploymentAnalysis.md` — platform context (if present)
   - Open with **one sentence** summarizing current state from `AI/nextSteps.md`.
2. **Git state check**: run `git status` and `git log --oneline -5`. If stale uncommitted changes exist, ask the user whether to stash, commit, or discard.
3. **Dependabot PR check**: run `gh pr list --state open --author app/dependabot --json number,title,createdAt` and add unrecorded PRs to `AI/nextSteps.md`.
4. **Branch state**: if on `main` with active work in `AI/nextSteps.md`, create or switch to the feature branch.
5. **Surface past knowledge**: derive `<topic>` from branch or `AI/nextSteps.md` and scan `SKILL.md` files and evolution logs for matching entries before implementing.

### Shutdown protocol

Run at session end before closing the conversation:

1. **Update AI session files**: update `AI/WORKLOG.md`, `AI/CHANGES.csv`, `AI/COMMANDS.sh`, and `AI/COMMIT_INFO.txt` per [ai-session-files.md](references/ai-session-files.md).
2. **Commit and push**: stage, commit using conventional commit format (see `managing-github-workflows`), push the feature branch, and open a PR if none exists.
3. **Verify `AI/nextSteps.md`**: mark completed items done, add newly discovered tasks, and confirm the next-session starting state.
4. **Invoke `agent-evolution`** (mandatory): capture session discoveries and update knowledge sections or record that no new patterns emerged.
5. **Push verification**: confirm `git log --oneline origin/$(git branch --show-current)..HEAD` is empty.

## Verification

Confirm all four `AI/` audit files are updated, `AI/nextSteps.md` reflects the
next session state, `agent-evolution` has logged the session, and the remote
tracking branch has zero unpushed commits:

```bash
git status --short
git log --oneline origin/$(git branch --show-current)..HEAD
```

## References

- [AI Session Files Schema](references/ai-session-files.md) — formats for `WORKLOG.md`, `CHANGES.csv`, `COMMANDS.sh`, and `COMMIT_INFO.txt`
- [Project Context Manifest](references/project-context-manifest.md) — public-safe `.workbench/project.config.yaml` / `crow.config` schema, symbolic refs, and confirmation gate
- [Process Knowledge](references/process-knowledge.md) — session rules, `Verified / Inferred / Unknown` epistemic labeling, and multi-agent single-writer ownership
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for session startup and shutdown discipline
