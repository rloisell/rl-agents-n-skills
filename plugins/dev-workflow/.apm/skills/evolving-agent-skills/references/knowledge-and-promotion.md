# Knowledge Format & Promotion Rules

Standards for recording session learnings, promoting shared skills, and
auditing skill health.

## Contents

- [Knowledge entry format](#knowledge-entry-format) • [Shared skill promotion](#shared-skill-promotion) • [Skill health indicators](#skill-health-indicators) • [Naming rules](#naming-rules) • [Meta-learnings](#meta-learnings)

## Knowledge entry format

Append discoveries to the target skill's knowledge section or `references/*-knowledge.md`.
Cap at 3 bullet points per session per skill and keep entries under 150 characters.

### Standard format (patterns, discoveries)

```markdown
- YYYY-MM-DD: [<project-code>] [CONTEXT: <type>] <imperative statement of what was learned>
```

### Causal format (failures, debugging — preferred)

```markdown
- YYYY-MM-DD: [<project-code>] [CONTEXT: <type>] <what happened> — CAUSE: <root cause> — FIX: <resolution>
```

Allowed `[CONTEXT: <type>]` values: `deployment`, `bug-fix`, `migration`,
`config`, `auth`, `networking`, `ci-cd`, `toolchain`, `agent-system`.

## Shared skill promotion

Promote a pattern to a shared skill when any of these signals trigger:

- The same pattern is written into 2+ separate skills in a single session.
- A knowledge entry is already duplicated across 2+ skills for the same topic.
- A topic keyword appears in 3+ past entries in `evolution-log.md` without a dedicated skill.

### Extraction workflow

1. Create `.apm/skills/<gerund-skill-name>/SKILL.md` (with `name` matching directory).
2. Move shared guidance into the new skill and its `references/` directory.
3. Replace duplicated inline content in source skills with a reference by skill name.
4. Update the plugin `README.md` inventory and append to `evolution-log.md`.

## Skill health indicators

| Indicator | Threshold | Action |
|-----------|-----------|--------|
| `SKILL.md` line count | > 100 lines | Split detail into `references/` |
| Knowledge bullets inline | > 15 bullets | Move to `references/*-knowledge.md` |
| Shared pattern in N skills | N >= 2 | Extract to shared skill |
| `references/*.md` line count | > 300 lines | Review for further split or add `## Contents` |
| Stale knowledge entry | > 90 days without review | Verify if still accurate |

## Naming rules

- Skill directory names must use lowercase gerunds and hyphens only (`^[a-z0-9-]+$`), matching frontmatter `name` exactly, <= 64 characters.
- Project codes in knowledge entries use generic identifiers (`[template]`, `[sample-app]`, `[engagement]`, or feature branch slug) — never real client names or namespaces.

## Meta-learnings

- 2026-02-27: [template] [CONTEXT: agent-system] Initial skill library migrated from flat `.agent.md` files to `SKILL.md` directories with shared skills extracted.
- 2026-03-04: [template] [CONTEXT: agent-system] Added pre-session knowledge retrieval, causal `CAUSE`/`FIX` annotation format, and cross-session pattern scanning.
- 2026-04-22: [template] [CONTEXT: agent-system] Added `[CONTEXT: type]` tags on all knowledge entries and included `evolution-log.md` in pre-session recall.
- 2026-04-22: [template] [CONTEXT: agent-system] When a submodule appears in `.gitmodules` but `git submodule status` returns nothing and the directory is missing — CAUSE: `.gitmodules` was edited without running `git submodule add` — FIX: run `git submodule add --force <url> <path>`.
