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

1. Phase 3: Add lightweight validator script to check seven required section headings in SKILL.md.
2. Phase 3: Add CI check to run skill-section validation for changed skills.
3. Upstream prep: Create trimmed upstream variant for bcgov/agent-skills using their exact skill spec contract.
4. Upstream prep: Run upstream local validation (`uv run python scripts/validate_skill.py ...`) in bcgov/agent-skills clone before PR.
5. Documentation: Add short contributor guide section in this repo on how to author skills with the seven-section structure.
