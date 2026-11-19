## Contents

- [Mandated Minimum Attributes](#mandated-minimum-attributes)
- [Verb Conformance Reference](#verb-conformance-reference)
- [Response Metadata Template (Mandate #6)](#response-metadata-template-mandate-6)
- [Error Contracts (RFC 9457 ProblemDetails)](#error-contracts-rfc-9457-problemdetails)
- [API Scope, Versioning & Evolution](#api-scope-versioning--evolution)
- [Indigenous-Language UTF-8 & Unicode Readiness](#indigenous-language-utf-8--unicode-readiness)
- [Common BC Gov Anti-Patterns](#common-bc-gov-anti-patterns)
- [Where to Apply & Companion Standards](#where-to-apply--companion-standards)

# BC Gov REST API Development Standard

The **REST API Development Standard** (effective 2015-04-01) requires that all *new public APIs* in BC Government MUST be designed and developed according to RESTful architecture principles per Fielding's dissertation, adapted to BC Gov mandated minimums. Internal APIs SHOULD follow the same pattern.

## Mandated Minimum Attributes

| # | Mandate | Notes |
|---|---|---|
| 1 | Public APIs **MUST** expose RESTful interfaces. | RPC-over-HTTP, SOAP, GraphQL-only do not satisfy this for public APIs. |
| 2 | Internal APIs **SHOULD** expose RESTful interfaces. | Same pattern recommended for internal consistency. |
| 3 | HTTP verbs **MUST** be used per HTTP/1.1 (RFC 7231). Only `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `TRACE`, `OPTIONS` are permitted. | No verb tunnelling (e.g., `POST /resource/delete`). |
| 4 | A URL **MUST** identify only a single resource. | No multi-resource fan-out URLs. |
| 5 | APIs **SHOULD** allow multiple output formats. | Recommended minimum: JSON and/or XML via `Accept` content negotiation. |
| 6 | Metadata **MUST** be described in a variable in the response. | Minimum fields: 6.1 creation date-time (ISO 8601 with timezone), 6.2 license(s) relevant to the dataset payload. |
| 7 | APIs **MUST** provide relevant error messaging. | Use HTTP status codes correctly; include machine-parseable error body. |
| 8 | APIs **MUST** be released with a version number. | URL or header versioning are both acceptable; version each breaking change. |

## Verb Conformance Reference

| Verb | Idempotent | Safe | Typical use |
|---|---|---|---|
| `GET` | Yes | Yes | Read; cacheable |
| `HEAD` | (not in standard's allow-list) | (n/a) | — |
| `POST` | No | No | Create; non-idempotent action |
| `PUT` | Yes | No | Replace |
| `PATCH` | No (recommended idempotent in practice) | No | Partial update |
| `DELETE` | Yes | No | Remove |
| `TRACE` | Yes | Yes | Diagnostic loop-back |
| `OPTIONS` | Yes | Yes | CORS preflight; capability discovery |

## Response Metadata Template (Mandate #6)

```json
{
  "metadata": {
    "createdAt": "2026-04-30T14:30:00-07:00",
    "license": [
      {
        "name": "Open Government Licence – British Columbia",
        "url": "https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc"
      }
    ],
    "version": "1.2.0"
  },
  "data": [ /* ... */ ]
}
```

ISO 8601 with timezone offset is required (Control #6.1.1, also enforced by the BC Government date and time standard). UTC zulu (`Z`) suffix is also acceptable.

## Error Contracts (RFC 9457 ProblemDetails)

Use **RFC 9457** `ProblemDetails` (superseding RFC 7807) for machine-parseable API errors and validation failures:

- Return the real HTTP status code (4xx for caller-correctable problems, 5xx for faults/dependency failures; never HTTP 200) with `Cache-Control: no-store`.
- Set `type` to a stable documentation/runbook URI per error code (or `about:blank`), `title` and `detail` from a central error catalog (never raw `exception.Message`, stack traces, or internal hostnames), and `instance` to a route template or vetted path (never a query-bearing URL).
- Include extension members for `code`, support reference (`traceId` or `requestId`), and UTC `timestamp`. Emit `Retry-After` on `429` and `503` when the wait is known.

## API Scope, Versioning & Evolution

- **Prefer narrow-question / decision APIs over bulk replication:** Return the decision or minimum attributes needed for a stated purpose rather than exposing broad data dumps or encouraging downstream dataset replication. Enforce subject and purpose scope at the provider, not in the UI; consumers must not request, cache, log, or persist fields they do not need.
- **Expand / migrate / contract versioning:** Every externally consumed API needs an identified owner, explicit compatibility/deprecation policy, consumer notification, and a tested rollback path. When mixed versions coexist, sequence breaking changes as **expand** (add new fields/routes alongside existing ones) -> **migrate** (move consumers) -> **contract** (retire old surface after deprecation window). Never expose mutable persistence models or internal exceptions as public contracts.

## Indigenous-Language UTF-8 & Unicode Readiness

BC Gov APIs and records must preserve Indigenous and multilingual names end-to-end (aligned with B.C. Government guidance and `bcgov/inclusive-names-service`):

- **Preserve original text:** Use UTF-8 for HTTP/JSON interchange and Unicode-capable database columns/collations. Do not strip diacritics, transliterate, force ASCII, or normalize destructively. Decode strictly at trust boundaries.
- **Grapheme-aware operations:** Use `System.Globalization.StringInfo` / text-element APIs for user-visible length limits, truncation, and substrings (never index UTF-16 `char` directly); use `Rune` for Unicode scalar-value processing and explicit `StringComparison` (ordinal for IDs/protocol tokens, approved culture/collation for linguistic text).
- **Keep ICU enabled:** Do not set `InvariantGlobalization=true` or select chiseled container images that strip ICU/globalization data when handling culture-sensitive or Indigenous-language text.
- **Round-trip corpus testing:** Test the full path (input -> API -> persistence -> retrieval/search -> response/export) with combining marks (e.g., base Latin character + `U+0313`), Unified Canadian Aboriginal Syllabics, canonically equivalent composed/decomposed sequences, and supplementary-plane characters.

## Common BC Gov Anti-Patterns

| Anti-pattern | Why it violates the standard |
|---|---|
| `POST /api/users/12/delete` | Verb tunnelling — violates Mandate #3 (use `DELETE`). |
| `GET /api/v1/users-and-orders/12` | URL identifies two resources — violates Mandate #4. |
| Returning HTTP 200 with `{ "error": "not found" }` body | Misuses status code — violates Mandate #7. |
| Releasing v2 in place by overwriting v1 routes | Breaks Mandate #8 — ship `/v2/` (or `Accept-Version: 2`). |
| Omitting metadata wrapper | Violates Mandate #6 — license + creation timestamp are minimum. |

## Where to Apply & Companion Standards

This standard applies when an information system, API, or service is **being developed by, or on behalf of**, the Province of British Columbia. CIO-level exemption is required for non-compliance.

| Topic | Standard / Control Summary |
|---|---|
| Authentication for the API | IMIT 6.13 + DIAM/Common SSO (see `building-bc-gov-web-apps`) |
| API hosting network zone | IMIT 6.13 (typically Low/DMZ for public APIs with WAF) |
| API security controls | Security Standard for Application and Web Development and Deployment v1.3 (code review before release, OWASP-aware, no creds in source, dormant accounts <= 45 days) |
| Data classification of API payload | IMIT 6.18 ISCF |
| Database security | Database Security Standard for Information Protection v1.0 (23 controls: data classification, TLS connection string, separation of duties, prod/non-prod segregation, no production data in test, patch cadence, audit) |
