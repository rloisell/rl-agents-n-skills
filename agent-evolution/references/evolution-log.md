# Agent Evolution Log

Records all changes to the agent skill library.
Maintained by `agent-evolution` at session end.

---

## Format

```
## YYYY-MM-DD — Session: <branch or feature name>

**Skills updated:** <skill1, skill2, ...>
**Shared skills created/updated:** <or "none">
**Agents split:** <or "none">
**Summary:** <1-2 sentences>
```

---

## 2026-04-22 — Session: agent-evolution-hermes-improvements

**Skills updated:** CLAUDE.md, agent-evolution/SKILL.md, session-workflow/SKILL.md, agents/agent-evolution.md, agents/ocp-resilience-analyst.md, README.md
**Shared skills created/updated:** bc-gov-network-architect/SKILL.md (new), sysadmin/SKILL.md (new)
**Agents split:** none
**Summary:** Applied Hermes Agent-inspired improvements to agent-evolution (mid-session retain nudges,
[CONTEXT: type] tags, USER_MODEL section, evolution-log in Step 0 recall, push verification in shutdown).
Fixed critical gaps: ocp-resilience-analyst YAML frontmatter, 3 missing agents in CLAUDE.md dispatch
table, agent-evolution made user-invocable. Propagated all changes to 6 consuming projects via submodule
update. README updated to reflect actual 19 agents / 14 shared skills.

---

## 2026-02-27 — Session: agent-skills-migration

**Skills updated:** all
**Shared skills created/updated:** ai-session-files, git-conventions, bc-gov-emerald, containerfile-standards (all new)
**Agents split:** diagram-generation (plantuml-templates.md), bc-gov-devops (networkpolicy-patterns.md)
**Summary:** Migrated entire agent team from custom flat `.agent.md` format to Agent Skills open
standard (`SKILL.md` directory per skill). Extracted 4 shared skills from cross-cutting content.
Created self-learning `agent-evolution` agent. Agent team is now 9 specialised skills + 4 shared
skills = 13 total SKILL.md directories. Old `*.agent.md` flat files deleted.
