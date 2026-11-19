## Contents

- [WCAG 2.2 AA Deltas & SPA Behaviour](#wcag-22-aa-deltas--spa-behaviour)
- [Sensitive-Identifier Masking & Reveal UX](#sensitive-identifier-masking--reveal-ux)
- [Consequential Decision & Degraded-State UX](#consequential-decision--degraded-state-ux)
- [Structured UX Finding Schema](#structured-ux-finding-schema)

# UX and Accessibility Patterns

Supplements the delegated [`bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system) skill (which owns official B.C. Design System tokens and `@bcgov/*` components) with WCAG 2.2 AA interaction rules, sensitive-identifier UX, consequential decision/degraded-state patterns, and a structured finding schema.

## WCAG 2.2 AA Deltas & SPA Behaviour

Verify all B.C. government digital services against [WCAG 2.2 Level AA](https://www.w3.org/TR/WCAG22/). Automated scans find only a subset of defects; pair tooling with manual keyboard, zoom, and screen-reader checks.

- **Reflow (320px / 400% zoom):** Verify layout at 400% browser zoom and a 320 CSS-pixel-equivalent viewport with no horizontal scrolling for ordinary content (document legitimate exceptions such as complex data tables or maps). Preserve usable labels, errors, and actions at 200% text sizing without clipping.
- **Target-size minimums:** Meet WCAG 2.2 AA target-size minimums (`24x24` CSS px or spacing exceptions); where a released B.C. Design System component specifies a larger target, use the B.C. requirement.
- **Unobscured focus:** Keep focus indicators visible and sufficiently contrasted, and ensure sticky headers, cookie notices, and floating controls do not obscure focused elements (`scroll-padding-top` / layout spacing).
- **Reduced motion:** Respect `prefers-reduced-motion`; remove non-essential motion and never rely on motion alone to explain state.
- **SPA route-change announcements:** On route or view changes in single-page applications, update `document.title` and deliberately manage focus (e.g., main heading or skip target) or announce the new view via a polite live region.
- **Authentication & paste:** Support password managers and paste in credential/code fields; do not require cognitive-function tests without an accessible alternative or assistance mechanism.

## Sensitive-Identifier Masking & Reveal UX

When displaying or editing sensitive identifiers (such as Social Insurance Numbers or Personal Health Numbers):

- **Mask by default:** Render sensitive values masked on initial view or edit load.
- **Per-field deliberate reveal:** Provide an individual, authorized reveal control per field rather than revealing all sensitive values as a side effect.
- **Accessible toggle semantics:** Give each show/mask button an accessible name identifying the field (e.g., `Show Social Insurance Number`), expose state with visible text and `aria-pressed`, support keyboard activation, and **do not move focus** when toggling visibility.
- **Safe announcements & DOM hygiene:** Announce that the value was shown or masked, **never** announce the sensitive value itself through an `aria-live` region. Never expose unmasked values in DOM attributes, tooltips, URLs, analytics events, or client logs.
- **Re-mask on exit:** Keep a user-controlled way to re-mask the value and automatically re-mask when leaving the editing context or clearing sensitive screen content. Masking is presentation protection only — never a substitute for authorization, TLS, storage encryption, or log redaction.

## Consequential Decision & Degraded-State UX

When a screen presents an automated eligibility/denial decision, an external register result, or a degraded/async/offline/assisted state:

- **Point-of-use explanation & provenance:** State what happened in plain language, explain relevant factors supported by approved policy (without exposing security-sensitive rules or another person's data), and surface provenance where available (source/service, version, timestamp/freshness; label unavailable provenance as unknown rather than guessing).
- **Actionable recourse:** Provide the user's next step at the point of use (correcting source data, human review request, contact/alternate channel). Distinguish final decisions from pending, provisional, stale, denied, expired, or revoked states.

| State | Required UI Behaviour |
|---|---|
| **Degraded / dependency unavailable** | Explain the limitation, whether work is safe to continue, and the retry or assisted option. |
| **Asynchronous / pending** | State that no final result is available yet, explain how to check status, and prevent duplicate submission. |
| **Offline / stale** | Identify what is unavailable or stale with its last-known timestamp; never present stale data as current. |
| **Assisted / manual** | Explain who or what will assist, what information is needed, and how to obtain follow-up. |

Never hide a consequential failure inside an indefinite spinner or silently retry an action that has side effects.

## Structured UX Finding Schema

Record UX and accessibility review findings using this uniform schema (mark source-only suspicions as `Needs manual verification`):

```text
Severity: Blocker | High | Medium | Low
Status: Verified | Needs manual verification
Location: repository-relative file and line, selector, or component
Observed: evidence from source and/or interaction
Rule: B.C. Design System source and/or WCAG 2.2 criterion
Impact: affected users and task consequence
Remediation: specific standards-aligned change
Applied: Yes | No | Partial
Verification: test performed and result
```
