# BC Gov Reusable Services & Common Components

Official BC Government shared services and OpenShift-ready components to reuse instead of building custom email, document generation, object storage, geocoding, analytics, or security scanning from scratch.

## Contents

- [Common Services (CHES, CDOGS, COMS, GETOK)](#common-services-ches-cdogs-coms-getok)
- [Document Rendering (`bcgov/docker-weasyprint`)](#document-rendering-bcgovdocker-weasyprint)
- [BC Address Geocoder](#bc-address-geocoder)
- [Privacy-Compliant Web Analytics (Fathom & Matomo)](#privacy-compliant-web-analytics-fathom--matomo)
- [Security & Code Quality (`bcgov/owasp-zap-openshift`, SonarQube / SonarCloud)](#security--code-quality-bcgovowasp-zap-openshift-sonarqube--sonarcloud)
- [Prebuilt Platform Images (`bcgov/s2i-caddy-nodejs`, `bcgov/AppAssessment`)](#prebuilt-platform-images-bcgovs2i-caddy-nodejs-bcgovappassessment)

## Common Services (CHES, CDOGS, COMS, GETOK)

| Service | Purpose | Key Capabilities | Reference |
|---|---|---|---|
| **CHES** (Common Hosted Email Service) | Programmatic email delivery | Appointment/schedule notifications, case status updates, bulk/templated email via REST API | [CHES Docs](https://bcgov.github.io/common-service-showcase/services/ches.html) |
| **CDOGS** (Common Document Generation Service) | Template-based document generation | Merge JSON datasets into PDF or XML-based templates (`docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp`, `html`) | [CDOGS Docs](https://bcgov.github.io/common-service-showcase/services/cdogs.html) |
| **COMS** (Common Object Management Service) | S3 object storage REST API | Upload/download/delete objects, versioning, public access toggles, fine-grained user permissions, metadata/tag search | [COMS Docs](https://bcgov.github.io/common-service-showcase/services/coms.html) |
| **GETOK** (Get Token) | Common Services client provisioning | Self-service tool (`bcgov/nr-get-token`) to generate Keycloak service clients and encrypted secrets for CHES/CDOGS/COMS | [GETOK Repo](https://github.com/bcgov/nr-get-token) |

- Overview portal: [BCGov Common Components](https://digital.gov.bc.ca/common-components/).
- Use **GETOK** (`bcgov/nr-get-token`) when onboarding to Common Services to provision Keycloak service-account clients and receive public/private-key encrypted credentials.

## Document Rendering (`bcgov/docker-weasyprint`)

- **Repository:** `https://github.com/bcgov/docker-weasyprint`
- Bundles [WeasyPrint](https://weasyprint.org/) as an OpenShift-compatible HTML-to-PDF/PNG microservice with a simple REST interface.
- Supports modern CSS3/HTML5, Flexbox, Grid, pagination/page layout control, custom fonts, MathML, and SVG.
- Prefer **CDOGS** for Office/template mail-merge workflows and **WeasyPrint** when rendering HTML/CSS directly to PDF/PNG.

## BC Address Geocoder

- **Base URL:** `https://geocoder.api.gov.bc.ca/`
- Real-time physical address standardization, validation, and geocoding (sites, intersections, occupants, and proximity queries).
- **Access tiers:**
  - Public access and sandbox API keys (up to 1,000 requests/min) via the [Geocoder API Console](https://catalogue.data.gov.bc.ca/dataset/bc-address-geocoder-web-service).
  - Unrestricted government API keys via the [Data Systems & Services request system](https://api.gov.bc.ca/).
- **Developer Guide:** [BC Address Geocoder Developer Guide](https://github.com/bcgov/api-specs/blob/master/geocoder/geocoder-developer-guide.md).

## Privacy-Compliant Web Analytics (Fathom & Matomo)

Avoid Google Analytics when data ownership and BC privacy compliance (FOIPPA) require self-hosted analytics:

- **Fathom (`bcgov/fathom-openshift`):** Lightweight website analytics without tracking or storing personal data. Deployable in OpenShift via `https://github.com/bcgov/fathom-openshift`.
- **Matomo (`bcgov/matomo-openshift`):** Full-featured web analytics server with complete data ownership and privacy compliance. Deployable in OpenShift via `https://github.com/bcgov/matomo-openshift`.

## Security & Code Quality (`bcgov/owasp-zap-openshift`, SonarQube / SonarCloud)

- **OWASP ZAP (`bcgov/owasp-zap-openshift`):** `https://github.com/bcgov/owasp-zap-openshift` — The upstream public OWASP ZAP Docker image requires privileged containers, which OpenShift disallows. `bcgov/owasp-zap-openshift` provides an unprivileged, OpenShift-compatible container image supporting active/passive scans, authenticated scanning, API scans, WebSockets, fuzzing, and AJAX spidering; integrates with CI/CD pipelines (`https://github.com/bcgov/pipeline-templates`).
- **SonarQube & SonarCloud (`bcgov/sonarqube`):** `https://github.com/bcgov/sonarqube` — Static code analysis for bugs, vulnerabilities, security hotspots, and code smells across 17+ languages.
  - **SonarCloud** is enabled on BCGov GitHub organizations, free for open-source repositories, saves OpenShift cluster resources, and automatically decorates GitHub pull requests (can be invoked from local workstations, OpenShift pipelines, or GitHub Actions). Submit onboarding requests via [DevOps Requests](https://github.com/bcgov/devops-requests).
  - **Self-hosted SonarQube:** Install in OpenShift using the `bcgov/sonarqube` repository instructions if SonarCloud is not suitable.

## Prebuilt Platform Images (`bcgov/s2i-caddy-nodejs`, `bcgov/AppAssessment`)

All OpenShift project sets receive an `artifactory-creds` secret (`imagePullSecrets: [{ name: artifactory-creds }]`) to pull Platform Services prebuilt images from Artifactory:

- **Caddy s2i (`bcgov/s2i-caddy-nodejs`):** `https://github.com/bcgov/s2i-caddy-nodejs` (Artifactory: `bcgov-docker-local/caddy-s2i-builder`) — Source-to-Image (s2i) Caddy + Node.js builder image used by `bcgov/pipeline-templates` to serve static/SPA frontends without maintaining custom base images.
- **AppAssessment (`bcgov/AppAssessment`):** `https://github.com/bcgov/AppAssessment` (Artifactory: `bcgov-docker-local/app-assessment`) — Identifies configuration issues in OpenShift namespaces and helps improve resource consumption and health checks.
