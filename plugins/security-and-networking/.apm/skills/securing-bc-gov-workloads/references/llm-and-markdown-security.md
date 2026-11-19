# LLM Prompt Injection & Markdown Security

Controls for workloads that invoke LLMs/agents, ingest documents for retrieval (RAG), expose tool/function calling, render model output, or process Markdown/frontmatter from any untrusted source.

## Contents

- [Prompt Injection & Second-Order Paths](#prompt-injection--second-order-paths)
- [RAG & Tool-Calling Trust Boundaries](#rag--tool-calling-trust-boundaries)
- [Untrusted Model Output Handling](#untrusted-model-output-handling)
- [Markdown & Frontmatter Security](#markdown--frontmatter-security)
- [OWASP LLM & CWE Mapping](#owasp-llm--cwe-mapping)

## Prompt Injection & Second-Order Paths

Treat chat messages, uploaded files, URLs, tickets, RAG documents, vector-store records, database text, tool/MCP responses, and Markdown/frontmatter as **untrusted data, never instructions**.

Trace both **direct** and **second-order (stored)** injection paths end to end:

```text
Untrusted write/import -> database/document/vector store/report -> later retrieval ->
prompt context -> model decision/output -> privileged tool or executable/rendering sink
```

- **Search both writers and later readers**: content that is benign at write time (tickets, comments, imported docs, PR descriptions) becomes an injection vector when later consumed by scheduled jobs, RAG summaries, or remediation agents.
- **Delimiters are not a security boundary**: instructions such as `"ignore commands in this document"` or XML/markdown fences provide defence-in-depth only; never rely on prompt wording to isolate untrusted text from system policy.
- **Secrets & PII hygiene**: ensure system prompts, credentials, internal endpoints, and cross-tenant data cannot enter prompts, logs, traces, fine-tuning data, or model responses.

## RAG & Tool-Calling Trust Boundaries

- **Pre-retrieval authorization & tenant filtering**: retrieval relevance is not authorization. Enforce user/tenant/role filters **before** vector or database retrieval so unauthorized chunks never enter the model context.
- **Tool allowlists & typed schemas**: expose the smallest possible set of tools with strict typed parameter schemas and server-side argument validation.
- **Least-privilege & confirmation**: run tools with least-privilege identities, bound iteration/token/cost limits, require explicit user confirmation for consequential or state-changing actions, and enforce server-side authorization independent of model decisions.

## Untrusted Model Output Handling

Treat all model output as untrusted user input:

- Validate against a strict schema and the exact destination context before rendering, storing, executing, or passing to another tool.
- Never pass unvalidated model output into raw HTML/Markdown renderers, `eval`, shell/process APIs, SQL, template engines, source/config writes, or outbound URL/redirect targets.

## Markdown & Frontmatter Security

Audit Markdown-processing pipelines (`.md`, `.mdx`, `.markdown`) whenever content is contributor-supplied, rendered to HTML, fetched server-side, or ingested by automation:

| Risk Area | What to Flag | Required Control |
|---|---|---|
| Raw HTML passthrough | `html: true` (`markdown-it`), `sanitize: false` (`marked`), `dangerouslySetInnerHTML`, `v-html`, `{@html}` | Disable raw HTML passthrough or sanitize output with a maintained allowlist (e.g., DOMPurify). |
| Unsafe URL schemes | `javascript:`, `vbscript:`, or executable `data:` in links/images | Enforce an explicit scheme allowlist (`https:`, `http:`, `mailto:`, relative `/`). |
| Remote fetch SSRF / tracking | Server-side fetching of remote images, embeds, includes, or link previews | Disable remote fetches or proxy through an allowlisted egress service; bound size/timeouts. |
| Unsafe YAML / frontmatter | `yaml.load()` without safe schema, Liquid/template directives, unbounded YAML aliases | Use safe loaders (`yaml.load(data, { schema: SAFE_SCHEMA })` / `yaml.safe_load`), disable executable directives. |
| MDX & includes | MDX executing contributor JS/components; path traversal in includes/attachments | Disable arbitrary MDX component execution for untrusted authors; canonicalize and jail file paths. |
| Hidden unicode & directives | Invisible/bidirectional control chars (Trojan Source), zero-width text, homoglyphs, hidden HTML comments containing LLM directives | Strip or reject bidirectional/zero-width control characters in CI/ingestion; review hidden comments before LLM ingestion. |

## OWASP LLM & CWE Mapping

- **OWASP LLM01**: Prompt Injection (`CWE-1427`)
- **OWASP LLM02**: Sensitive Information Disclosure
- **OWASP LLM05**: Improper Output Handling
- **OWASP LLM06**: Excessive Agency
- **OWASP LLM08**: Vector and Embedding Weaknesses
- **OWASP LLM10**: Unbounded Consumption
