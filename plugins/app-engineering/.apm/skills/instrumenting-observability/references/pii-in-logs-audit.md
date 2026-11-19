# PII-in-Logs Audit

Systems handling personal information (Protected B) must not write PII to logs. FOIPPA and the Privacy Act treat PII in application logs as a disclosure risk — logs are often retained longer than business records and may be accessed by ops staff without data steward approval.

## PII-Free Logging Rules

**NEVER** log:
- User names, email addresses
- SIN, DL number, student number, or other personal identifiers
- Connection strings, tokens, passwords, or Vault values
- Full HTTP request/response bodies (may contain form data)
- Query string parameters that may carry tokens (`?code=`, `?token=`)

**Safe to log:**
- User ID (GUID / `sub` claim) — opaque identifier only
- HTTP method + path (no query string)
- HTTP status code
- Duration (ms)
- Correlation ID / trace ID

## Common PII Categories to Check

- Full names, addresses, dates of birth
- SIN, health card numbers, driver's licence numbers
- BCeID / IDIR usernames (identifiers linked to real people)
- Email addresses
- IP addresses (context-dependent — usually PII for Protected B systems)
- `<program-area>` request content (subject matter, request description, requester details)
- Other program-area-specific sensitive fields (configmap keys, request payloads, document content)

## Language Checklists

### Python
- [ ] No `logging.debug(request.json())` or `logging.info(vars(model))` — these dump full objects
- [ ] No `f"Processing request for {user.name}"` — use opaque user ID only (e.g. `user.id`)
- [ ] No full request body logging at `INFO` or `DEBUG` level
- [ ] Flask: never log `request.data` or `request.form` at `INFO`
- [ ] SQLAlchemy: confirm `LOG_SQLALCHEMY=ERROR` (not `DEBUG`, which logs full queries with bound parameter values)
- [ ] Structured log format (JSON output) confirmed — verify with `LOG_FORMAT=json` or equivalent env var

### Go
- [ ] No `log.Printf("%+v", document)` on full document structs — `%+v` dumps all fields including content
- [ ] Use structured logging (`slog` or `zap`) with an explicit field allowlist
- [ ] Never log document content (raw bytes, extracted text, OCR output)
- [ ] Confirm log output is JSON-formatted (structured), not plain text

### Node.js
- [ ] No `console.log(req.body)` in middleware or request handlers
- [ ] No `JSON.stringify(user)` in log statements
- [ ] Morgan (HTTP logger): use `:method :url :status :res[content-length] - :response-time ms` format only — no body logging
- [ ] No `winston.debug(JSON.stringify(requestPayload))` patterns

## Audit Command — Scan for PII-Risk Log Statements

```bash
# Python — flag logging calls that reference request bodies, user objects, or email/name fields
grep -rn "logging\.\(info\|debug\|warning\)(.*\(request\|body\|user\|email\|name\))" \
  --include="*.py" .

# Go — flag log calls that reference document, user, email, or body variables
grep -rn "log\.\(Print\|Info\|Debug\)(.*\(document\|user\|email\|body\))" \
  --include="*.go" .

# Node.js — flag console.log or logger calls referencing req.body or req.user
grep -rn "console\.log\|logger\.\(info\|debug\)(.*req\.\(body\|user\))" \
  --include="*.js" --include="*.ts" .
```

Review all matches manually — not all are violations, but each needs a justification.
