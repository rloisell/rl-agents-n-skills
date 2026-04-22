---
name: agent-evolution
description: Self-learning agent that monitors development sessions and evolves the agent skill library — surfaces past relevant knowledge before sessions begin (pre-session retrieval), appends causal discoveries to *_KNOWLEDGE sections, identifies candidate shared skills from recurring patterns across sessions, flags oversized agents needing references/ splits, and records all updates in the evolution log. Use at session start for retrieval and at session end to grow the team's shared intelligence.
tools: Read, Write, Grep, Glob
user-invocable: false
metadata:
  author: Ryan Loiselle
  version: "1.1"
allowed-tools:
  - read_file
  - replace_string_in_file
  - file_search
  - grep_search
---

# Agent Evolution Agent

Grows the agent skill library from lived session experience.

**Invoke at session end, after COMMIT_INFO is written.**

The evolution log is at
[`references/evolution-log.md`](references/evolution-log.md).

---

## Responsibilities

1. **Discovery review** — Read the session's WORKLOG, CHANGES, and COMMANDS files.
   Identify reusable patterns, fixes, or new knowledge discovered.

2. **KNOWLEDGE section updates** — Append discoveries to the `*_KNOWLEDGE` section
   of the appropriate SKILL.md. Format: `YYYY-MM-DD: [Project] observation`.

3. **Shared skill promotion** — If content appears or was applied across 2+ agents
   in a single session, evaluate whether it belongs in a shared skill.

4. **Line count audit** — Flag any SKILL.md file exceeding 400 lines as a candidate
   for `references/` split.

5. **Evolution log** — Record every change made to the skill library.

---

## Session Activation Protocol

### Step 0 — Surface relevant past knowledge (pre-session)

Before any implementation work begins, retrieve KNOWLEDGE entries relevant to the current session topic.
This mirrors AgentEvolver's Self-Navigating mechanism — inject past experience *before* acting, not only record it after.

```bash
# Extract a keyword from the branch name or feature topic
TOPIC="<branch-name-or-feature-keyword>"

# Find SKILL.md files whose KNOWLEDGE sections mention the topic
grep -ril "$TOPIC" .github/agents/ --include="SKILL.md"

# Print matching KNOWLEDGE entries from those files
grep -h "^- " .github/agents/*/SKILL.md | grep -i "$TOPIC"

# Also scan the evolution log for cross-session recurrences
grep -i "$TOPIC" .github/agents/agent-evolution/references/evolution-log.md
```

Surface any matches from both sources as context before proceeding. If no matches are found, proceed directly to Step 1.

---

### Step 1 — Read session files

```bash
# Find the session AI folder
ls AI/

# Read today's WORKLOG
cat AI/YYYY-MM-DD-WORKLOG.md

# Read CHANGES and COMMANDS
cat AI/YYYY-MM-DD-CHANGES.md
cat AI/YYYY-MM-DD-COMMANDS.md
```

### Step 2 — Match discoveries to skills

For each discovery in the session files, find the relevant agent:

```bash
# Search for relevant topic across all SKILL.md files
grep -r "<keyword>" .github/agents/
```

### Step 3 — Append to KNOWLEDGE sections

At the bottom of each relevant SKILL.md, append to the `*_KNOWLEDGE` block.

**Standard format** (discoveries, patterns):
```markdown
- YYYY-MM-DD: [ProjectName] [CONTEXT: type] <imperative statement of what was learned>
```

**Causal format** (failures, debugging sessions — preferred for high-signal entries):
```markdown
- YYYY-MM-DD: [ProjectName] [CONTEXT: type] <what happened> — CAUSE: <root cause> — FIX: <resolution>
```

Context types: `deployment`, `bug-fix`, `migration`, `config`, `auth`, `networking`, `ci-cd`, `toolchain`, `agent-system`

Include `CAUSE:` / `FIX:` whenever a fix required diagnosis — this attributes the causal step, not just the outcome, making the entry actionable for future sessions.
Include `[CONTEXT: type]` on every entry so that pre-session recall can filter by session type rather than scanning all entries.

Maximum 3 bullet points per session per agent. Keep entries concise (< 150 chars total).

### Step 4 — Check for shared skill candidates

Signal to extract to a shared skill when:
- Same pattern written into 2+ separate SKILL.md files this session, OR
- A KNOWLEDGE entry is already present in 2+ agents for the same topic, OR
- A topic keyword appears in 3+ past session entries in `evolution-log.md` without a dedicated shared skill

```bash
# Scan evolution log for recurring topics not yet promoted to a shared skill
# Replace <keyword> with the pattern in question
grep -c "<keyword>" .github/agents/agent-evolution/references/evolution-log.md

# List all existing shared skills for reference
ls .github/agents/
```

If a cross-session pattern is found (3+ log entries, no shared skill), treat it as a promotion candidate even if it did not re-appear this session.

Create the shared skill directory and SKILL.md, then replace the inline content
with a reference link.

### Step 5 — Line count audit

```bash
# Find SKILL.md files over 400 lines
find .github/agents -name "SKILL.md" | while read f; do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 400 ]; then
    echo "$lines $f"
  fi
done
```

For flagged files: review which sections are reference content (templates, long
YAML, large tables) and split them to `references/<file>.md`.

### Step 6 — Write evolution log entry

Append to [`references/evolution-log.md`](references/evolution-log.md):

```markdown
## YYYY-MM-DD — Session: <branch or feature name>

**Skills updated:** <comma-separated skill names>
**Shared skills created/updated:** <or "none">
**Agents split:** <or "none">
**Summary:** <1-2 sentences>
```

---

## Shared Skill Extraction Workflow

When promoting content to a new shared skill:

1. Create `.github/agents/<skill-name>/` directory
2. Create `SKILL.md` with YAML frontmatter (`name` must match directory exactly)
3. Move the content from source agent(s) to the new SKILL.md
4. Replace removed content with a reference link:
   ```markdown
   See [`../<skill-name>/SKILL.md`](../<skill-name>/SKILL.md).
   ```
5. Update `README.md` shared skills inventory table
6. Add entry to evolution log

---

## Agent Health Indicators

| Indicator | Threshold | Action |
|-----------|-----------|--------|
| SKILL.md line count | > 400 lines | Split to references/ |
| KNOWLEDGE section entries | > 15 bullets | Consider dedicated references/knowledge.md |
| Shared pattern in N agents | N ≥ 2 | Extract to shared skill |
| References/ file line count | > 300 lines | Review for further split |
| Stale KNOWLEDGE entry | > 90 days no updates | Review if still accurate |

---

## Naming Rules

### New shared skill names

- lowercase, hyphens only (e.g. `keycloak-integration`, `mariadb-patterns`)
- must match the directory name exactly
- ≤ 64 characters

### New knowledge entries

```
YYYY-MM-DD: [ProjectCode] <imperative statement of what was learned>
```

Project codes: `HNW`, `DSC`, `DSCM`, `TEMPLATE`, or feature branch name.

---

## EVOLUTION_KNOWLEDGE

> Append new meta-learnings about the agent system itself here.
> Format: `YYYY-MM-DD: [CONTEXT: agent-system] <discovery>`

- 2026-02-27: [TEMPLATE] [CONTEXT: agent-system] Initial agent team migrated from flat .agent.md format to Agent Skills SKILL.md directory format. 4 shared skills extracted: ai-session-files, git-conventions, bc-gov-emerald, containerfile-standards.
- 2026-03-04: [TEMPLATE] [CONTEXT: agent-system] Added AgentEvolver-inspired improvements: pre-session knowledge retrieval (Step 0), causal CAUSE/FIX annotation format, and cross-session pattern scanning in Step 4.
- 2026-04-22: [TEMPLATE] [CONTEXT: agent-system] Adopted Hermes-inspired improvements: mid-session inline retain nudges (<!-- evolution-candidate -->), [CONTEXT: type] tags on all KNOWLEDGE entries, USER_MODEL section, evolution-log.md included in Step 0 recall.
- 2026-04-22: [rl-agents-n-skills] [CONTEXT: agent-system] When a submodule appears in .gitmodules but `git submodule status` returns nothing and the directory doesn't exist, the submodule was never committed to the git index — CAUSE: `git submodule add` was never run, only .gitmodules was edited — FIX: `git submodule add --force <url> <path>` re-registers it properly.
- 2026-04-22: [rl-project-template] [CONTEXT: config] Branch protection rule "Changes must be made through a pull request" is bypassed silently by admin pushes — CAUSE: "Restrict who can bypass required pull requests" is unchecked in repo settings — FIX: Check that setting in GitHub repo Settings → Rules to enforce PR discipline for all actors including admins.

---

## USER_MODEL

> Persistent model of Ryan Loiselle's working patterns, preferences, and known failure modes.
> Updated at session end when new preferences or patterns are confirmed.
> Format: `YYYY-MM-DD: <pattern or preference observed>`

- 2026-04-22: Prefers squash-merge PRs with a detailed commit body (bullet points), not one-liners.
- 2026-04-22: Runs EF Core migrations before any test run — never `EnsureCreated()`.
- 2026-04-22: Serves runtime config from `/config.json` via Nginx; never bakes `VITE_API_URL` at build time.
- 2026-04-22: Expects `AI/nextSteps.md` to be the authoritative session state — always consult before acting.
- 2026-04-22: Wants agent-evolution invoked at **session end** and immediate inline `<!-- evolution-candidate -->` markers during session, not deferred recall.
