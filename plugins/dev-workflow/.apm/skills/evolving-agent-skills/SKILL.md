---
name: evolving-agent-skills
description: >-
  Monitors development sessions to evolve the agent skill library — surfaces
  relevant past knowledge before sessions begin, appends causal discoveries to
  skill knowledge sections, promotes recurring patterns to shared skills,
  audits skill line counts, and records updates in the evolution log. Use at
  session start for retrieval and at session end to capture learnings.
---

# Evolving Agent Skills

Grows and maintains the agent skill library from lived session experience.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Always run at session end**: even when no new patterns emerged, record an explicit "no new patterns" entry in [evolution-log.md](references/evolution-log.md).
2. **Causal format for fixes**: use `CAUSE:` and `FIX:` plus `[CONTEXT: type]` tags on knowledge entries, capped at 3 bullets per session per skill (< 150 chars each).
3. **Lean `SKILL.md` discipline**: flag any `SKILL.md` exceeding 100 lines for splitting into `references/`.
4. **Promote recurring patterns**: extract patterns appearing across 2+ skills in one session or 3+ log entries into a shared skill.

## Quick start

Before implementation begins, scan skills and the evolution log for entries
matching the active branch or feature topic:

```bash
TOPIC="<branch-name-or-feature-keyword>"
grep -ril "$TOPIC" .apm/skills/ --include="SKILL.md" --include="*.md"
grep -i "$TOPIC" .apm/skills/evolving-agent-skills/references/evolution-log.md
```

## Workflow

1. **Read session logs**: inspect `AI/WORKLOG.md`, `AI/CHANGES.csv`, and `AI/COMMANDS.sh`.
2. **Match and append knowledge**: locate the target skill's knowledge section (or `references/*-knowledge.md`) and append concise causal entries per [knowledge-and-promotion.md](references/knowledge-and-promotion.md).
3. **Check promotion candidates**: scan `evolution-log.md` and `SKILL.md` files for patterns appearing in 2+ skills or 3+ sessions.
4. **Audit line counts and external references**: flag oversized `SKILL.md` files and add any newly cited external standards to `README.md`.
5. **Update evolution log**: prepend a dated summary entry to [evolution-log.md](references/evolution-log.md).

## Verification

Confirm the evolution log has an entry for the current session, no `SKILL.md`
violates line-count limits, and all updates are committed and pushed:

```bash
head -n 20 .apm/skills/evolving-agent-skills/references/evolution-log.md
git status --short
```

## References

- [Evolution Log](references/evolution-log.md) — chronological record of skill library updates
- [Knowledge Format & Promotion Rules](references/knowledge-and-promotion.md) — causal entry schema, shared skill extraction, health indicators, and naming rules
- [Seven-Section Skill Template](assets/templates/seven-section-skill-template.md) — standard 7-section skeleton for authoring new skills
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for skill retrieval, causal capture, and promotion
