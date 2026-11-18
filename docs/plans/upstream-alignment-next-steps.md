# AI Next Steps

## Current Session Status

Completed:

1. Added new generic deployment and CI/CD analyst skill scaffold.
2. Added paired deployment-cicd-analyst agent persona.
3. Completed Phase 1 and Phase 2 standards adoption:
   - Added seven-section skill policy.
   - Added canonical seven-section template.
   - Refactored bc-gov-deployment-cicd-analyst skill to seven-section format.

## Remaining Next Steps

### Required for bcgov/agent-skills contribution

1. Check upstream for overlap before new skill submission (per CONTRIBUTING guidance).
2. Create upstream-ready trimmed copy of `bc-gov-deployment-cicd-analyst` under `skills/<name>/SKILL.md` in a local clone of `bcgov/agent-skills`.
3. Ensure skill matches upstream spec contract (`spec/SKILL_SPEC.md`) and includes all required seven sections.
4. Remove personal/local references from frontmatter and body (no local filesystem paths, no personal metadata unless required).
5. Validate locally in upstream repo:
   - `uv run python scripts/validate_skill.py skills/<name>/SKILL.md`
6. Run upstream project checks before PR:
   - `make lint`
   - `make test`
   - `make validate-one SKILL=skills/<name>/SKILL.md`
7. Create branch in upstream repo and raise PR with:
   - problem statement,
   - why existing upstream skills do not already cover this,
   - what is added,
   - expected usage and value.

### Recommended for higher-confidence merge

1. Keep initial upstream PR narrow (skill only; defer agent persona to follow-up PR unless explicitly requested).
2. Add one concise example invocation and one sample control-matrix output in references/examples if upstream allows.
3. Cross-link relevant BC Gov standards references in a neutral, reusable way.
4. After upstream PR is opened, track review feedback back into this repo to minimize future drift.
5. Add lightweight Phase 3 validator in this repo to keep new skills aligned with seven-section structure.
6. Add CI check in this repo for changed skills to enforce section structure and reduce regression risk.
7. Add a short contributor guide section in this repo documenting seven-section authoring expectations.
