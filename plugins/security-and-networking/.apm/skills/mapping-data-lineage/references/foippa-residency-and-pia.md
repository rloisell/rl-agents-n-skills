# FOIPPA Residency & PIA Trigger Checklist

## Contents

- [External AI/OCR Service Pattern](#external-aiocr-service-pattern)
- [Legal Risk (FOIPPA s.30.1)](#legal-risk-foippa-s301)
- [How to Determine Cloud Region](#how-to-determine-cloud-region)
- [PIA Trigger Checklist](#pia-trigger-checklist)
- [Confirmed Facts](#confirmed-facts)

## External AI/OCR Service Pattern

This pattern applies when a BC Gov application sends Protected B document content to an external AI/cloud service for processing (e.g., OCR, text extraction, document intelligence).

### What to Check

A downstream microservice sends document content (scanned PDFs, images) to an **external cloud AI service** for OCR and text extraction. These documents may contain Protected B personal information (names, addresses, financial records, medical information).

## Legal Risk (FOIPPA s.30.1)

Under **FOIPPA s.30.1**, personal information stored outside Canada must be:
1. Disclosed in the public body's privacy notice.
2. Covered by a written agreement with the service provider.
3. Subject to Canadian law protections where reasonably possible.

Cloud service endpoints outside `Canada East` / `Canada Central` trigger a FOIPPA s.30.1 disclosure obligation and require a **MISA Data Processing Agreement (DPA)**.

## How to Determine Cloud Region

Check the service endpoint URL in environment variables or ConfigMaps:

```bash
# Find all external HTTPS endpoint env vars across all deployments
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec.containers[].env[]? | select(.value | test("https://")) | {name, value}'

# Also check ConfigMaps
oc get configmaps -n <ns> -o json | \
  jq '.items[] | .data | to_entries[] | select(.value | test("https://")) | {key, value}'
```

The endpoint URL is the authoritative source for data residency determination. Canada-based endpoints (e.g., `canadacentral`, `canadaeast`) still require a MISA DPA but satisfy Canadian residency requirements.

## PIA Trigger Checklist

A Privacy Impact Assessment (PIA) is required when:

- [ ] **New cross-cloud data flow** involving personal information (any cloud provider)
- [ ] **New third-party data processor** where personal data is shared or processed
- [ ] **Change to data retention periods** for personal information
- [ ] **New AI/ML processing** of personal data — cloud Document Intelligence, LLMs, OCR, etc. all qualify
- [ ] **New automated decision** supported by personal data (algorithmic decision-making)
- [ ] **New collection of personal information** not covered by an existing PIA
- [ ] **Significant change** to an existing system that handles personal information

When a PIA trigger is identified:
1. Document in `AI/securityNextSteps.md` under "PIA Status".
2. Engage the Ministry Privacy Officer.
3. Do not deploy to production until PIA is reviewed.
4. Capture accepted residual risks in the STRA.

## Confirmed Facts

- External AI/OCR services receiving Protected B document content require confirming the cloud region and obtaining a MISA DPA before production.
- The service endpoint env var in a ConfigMap or deployment is the authoritative source for data residency determination — always check this first.
- Message stream keys in ConfigMaps indicate cross-namespace data flows that must appear in the data flow ledger — check stream key naming for data classification hints.
