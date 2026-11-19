# Acceptance Criteria — evolving-agent-skills

Observable pass/fail criteria for verifying skill retrieval, knowledge capture, promotion, and evolution logging.

## Session-Start Retrieval

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Topic scan executed | Skills and `evolution-log.md` are searched for keywords matching the active branch or feature | Implementation begins without scanning past knowledge |
| Relevant entries surfaced | Matching `CAUSE:`/`FIX:` entries or log items are summarized before work starts | Known recurring pitfalls in the skill library are ignored |

## Session-End Capture & Maintenance

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Session logs inspected | `AI/WORKLOG.md`, `AI/CHANGES.csv`, and `AI/COMMANDS.sh` are reviewed for discoveries | Knowledge updates are fabricated without inspecting session logs |
| Causal knowledge format | New entries use `CAUSE:` and `FIX:` with `[CONTEXT: type]` tags, <= 3 bullets/skill/session, < 150 chars each | Entries are verbose prose, lack causal tags, or exceed bullet/char caps |
| Promotion check | Patterns appearing in 2+ skills in one session or 3+ log entries are flagged/promoted to a shared skill | Recurring cross-skill patterns remain duplicated without promotion |
| `SKILL.md` line-count audit | Any `SKILL.md` exceeding 100 lines is flagged for splitting into `references/` | Oversized `SKILL.md` files pass audit unflagged |
| Evolution log updated | Dated summary (or explicit "no new patterns" entry) is prepended to `evolution-log.md` | Session ends with no entry in `evolution-log.md` |

## Scope Boundaries

- **Trigger**: Session-start knowledge recall, session-end learning capture, or promoting recurring patterns across skills.
- **Do not trigger**: Git state / Dependabot startup triage (`managing-dev-sessions`) or CI failure diagnosis (`managing-github-workflows`).
