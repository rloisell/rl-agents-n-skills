---
name: bc-gov-rest-api
description: BC Government REST API Development Standard — 8 mandated minimums for public APIs (RESTful architecture, HTTP verbs per RFC, single-resource URLs, multiple output formats, response metadata, error messaging, version numbers). Use when designing or reviewing public BC Gov APIs, writing OpenAPI specs, or evaluating API conformance.
tools: Read, Grep, Glob
metadata:
  author: Ryan Loiselle
  version: "1.0"
  sources:

    - title: "REST API Development Standard (Effective 2015-04-01)"
      note: "Authoritative — 8 mandated minimums for public-facing BC Gov APIs."
      url: "https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/api-standard.pdf"

    - title: "OCIO REST API Development Guide"
      note: "Companion guide \u2014 examples, optional features, best practices."
      url: "https://github.com/bcgov/REST-API-Development-Guide"

    - title: "Roy T. Fielding \u2014 \"Architectural Styles and the Design of Network-based Software Architectures\" (2000)"
      note: "Foundational dissertation referenced normatively by the standard."
      url: "https://www.ics.uci.edu/~fielding/pubs/dissertation/top.htm"

compatibility: All BC Government public-facing APIs and (recommended) internal APIs.
---

# BC Gov REST API Development Standard

The **REST API Development Standard** (effective 2015-04-01) requires that all *new public
APIs* in BC Government MUST be designed and developed according to RESTful architecture
principles per Fielding's dissertation, adapted to BC Gov mandated minimums. Internal APIs
SHOULD follow the same pattern.

> The intent is not to prescribe a re-architecture of existing APIs or limit development to
> the prescribed minimums, but to ensure BCGov APIs behave consistently and balance a truly
> RESTful interface with positive developer experience (DX).

## Mandated minimum attributes

| # | Mandate | Notes |
| --- | --- | --- |
| 1 | Public APIs **MUST** expose RESTful interfaces. | RPC-over-HTTP, SOAP, GraphQL-only do not satisfy this for public APIs. |
| 2 | Internal APIs **SHOULD** expose RESTful interfaces. | Same pattern recommended for internal consistency. |
| 3 | HTTP verbs **MUST** be used per HTTP/1.1 (RFC 7231). Only `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `TRACE`, `OPTIONS` are permitted. | No verb tunnelling (e.g., `POST /resource/delete`). |
| 4 | A URL **MUST** identify only a single resource. | No multi-resource fan-out URLs. |
| 5 | APIs **SHOULD** allow multiple output formats. | Recommended minimum: JSON and/or XML via `Accept` content negotiation. |
| 6 | Metadata **MUST** be described in a variable in the response. | Minimum fields: 6.1 creation date-time (ISO 8601 with timezone), 6.2 license(s) relevant to the dataset payload. |
| 7 | APIs **MUST** provide relevant error messaging. | Use HTTP status codes correctly; include machine-parseable error body. |
| 8 | APIs **MUST** be released with a version number. | URL or header versioning are both acceptable; version each breaking change. |

## Verb conformance reference

| Verb | Idempotent | Safe | Typical use |
| --- | --- | --- | --- |
| `GET` | Yes | Yes | Read; cacheable |
| `HEAD` | (not in standard's allow-list) | (n/a) | \u2014 |
| `POST` | No | No | Create; non-idempotent action |
| `PUT` | Yes | No | Replace |
| `PATCH` | No (recommended idempotent in practice) | No | Partial update |
| `DELETE` | Yes | No | Remove |
| `TRACE` | Yes | Yes | Diagnostic loop-back |
| `OPTIONS` | Yes | Yes | CORS preflight; capability discovery |

## Response metadata template (Mandate #6)

```json
{
  "metadata": {
    "createdAt": "2026-04-30T14:30:00-07:00",
    "license": [
      {
        "name": "Open Government Licence \u2013 British Columbia",
        "url": "https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc"
      }
    ],
    "version": "1.2.0"
  },
  "data": [ /* ... */ ]
}
```

ISO 8601 with timezone offset is required (Control #6.1.1, also enforced by the BC Government
date and time standard). UTC zulu (`Z`) suffix is also acceptable.

## Common BC Gov anti-patterns

| Anti-pattern | Why it violates the standard |
| --- | --- |
| `POST /api/users/12/delete` | Verb tunnelling \u2014 violates Mandate #3 (use `DELETE`). |
| `GET /api/v1/users-and-orders/12` | URL identifies two resources \u2014 violates Mandate #4. |
| Returning HTTP 200 with `{ "error": "not found" }` body | Misuses status code \u2014 violates Mandate #7. |
| Releasing v2 in place by overwriting v1 routes | Breaks Mandate #8 \u2014 ship `/v2/` (or `Accept-Version: 2`). |
| Omitting metadata wrapper | Violates Mandate #6 \u2014 license + creation timestamp are minimum. |

## Where to apply

This standard applies when an information system, API, or service is **being developed by,
or on behalf of**, the Province of British Columbia. CIO-level exemption is required for
non-compliance.

## Companion standards

| Topic | Standard |
| --- | --- |
| Authentication for the API | IMIT 6.13 + DIAM/Common SSO (see `bc-gov-iam`) |
| API hosting network zone | IMIT 6.13 (typically Low/DMZ for public APIs with WAF) |
| API security controls (input validation, OWASP) | Security Standard for Application and Web Development and Deployment |
| Data classification of API payload | IMIT 6.18 ISCF |
| Database providing the data | `bc-gov-database-security` skill |
