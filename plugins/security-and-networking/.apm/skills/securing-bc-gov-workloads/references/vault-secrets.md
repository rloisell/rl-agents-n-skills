# HashiCorp Vault & External Secrets Operator (ESO)

## Contents

- [Vault Architecture & Endpoints](#vault-architecture--endpoints)
- [Vault Path Convention](#vault-path-convention)
- [User Access & 2-Technical-Lead Limit](#user-access--2-technical-lead-limit)
- [Vault Agent Injector — KSA Standard for BC Gov Vault](#vault-agent-injector--ksa-standard-for-bc-gov-vault)
- [Dynamic Secrets & Data Encryption (Transit)](#dynamic-secrets--data-encryption-transit)
- [External Secrets Operator (ESO) — `external-secrets.io/v1`](#external-secrets-operator-eso--external-secretsiov1)
- [Helm Secret — Shape Template Only](#helm-secret--shape-template-only)
- [GitHub Actions — Vault Integration](#github-actions--vault-integration)
- [Confirmed Facts & Pitfalls](#confirmed-facts--pitfalls)

## Vault Architecture & Endpoints

BC Gov's HashiCorp Vault service runs in HA on the Gold clusters and serves **Silver, Gold/GoldDR, and Emerald**:

| Environment | Vault Address | Enterprise Namespace |
|---|---|---|
| Production clusters (Silver, Gold, GoldDR, Emerald) | `https://vault.developer.gov.bc.ca` | `platform-services` |
| Lab clusters (e.g., KLAB) | `https://vault-lab.developer.gov.bc.ca` | `platform-services` |

> Always set `platform-services` as the Vault Enterprise namespace (`VAULT_NAMESPACE=platform-services`, `vault.hashicorp.com/namespace: platform-services`, or ESO `spec.provider.vault.namespace: platform-services`).

## Vault Path Convention

Platform Product Registry provisions two KV v2 secret engines per ProjectSet (plus `cubbyhole`, which is unused):

```text
<license-plate>-nonprod/<secret-name>   # shared by tools, dev, test
<license-plate>-prod/<secret-name>      # prod only

Examples:
  <license-plate>-nonprod/app-secrets-dev   (keys: dev_db_host, dev_db_pass)
  <license-plate>-nonprod/app-secrets-test  (keys: test_db_host, test_db_pass)
  <license-plate>-prod/app-secrets-prod     (keys: prod_db_host, prod_db_pass)
```

> **Key naming rule**: Do **not** use hyphens (`-`) in Vault secret *keys* (e.g., use `db_password`, not `db-password`). Vault accepts hyphens, but OpenShift templates and `vault-init` fail when parsing hyphenated key names.

## User Access & 2-Technical-Lead Limit

- **2-Technical-Lead OIDC limit**: Due to Vault licensing, only the **two Technical Contacts** registered in the [Platform Product Registry](https://registry.developer.gov.bc.ca/) receive OIDC write access to `<license-plate>-nonprod` and `<license-plate>-prod`.
- **UI login**: `https://vault.developer.gov.bc.ca` → Namespace: `platform-services` → Method: `OIDC` → Role: `<license-plate>` → Sign in with AzureAD IDIR.
- **CLI login & verification**:

```bash
export LICENSE_PLATE=<license-plate>
export VAULT_ADDR=https://vault.developer.gov.bc.ca
export VAULT_NAMESPACE=platform-services

vault login -method=oidc role=${LICENSE_PLATE}
vault kv get ${LICENSE_PLATE}-nonprod/helloworld
vault kv get ${LICENSE_PLATE}-prod/helloworld
```

## Vault Agent Injector — KSA Standard for BC Gov Vault

**Vault Agent Injector** is the standard, non-expiring pattern for BC Gov Private Cloud Vault. It authenticates pods using a pre-provisioned Kubernetes Service Account (KSA) with read-only access.

### Cluster Auth Paths, Roles & KSA

| Item | Value |
|---|---|
| Pre-provisioned KSA | `<license-plate>-vault` (created in `dev`, `test`, `prod`, `tools`) |
| Pre-provisioned Vault roles | `<license-plate>-nonprod` or `<license-plate>-prod` |
| Cluster K8s auth paths | `auth/k8s-silver`, `auth/k8s-gold`, `auth/k8s-golddr`, `auth/k8s-emerald` |

> **KSA ImagePuller / `imagePullSecrets` gotcha**: Because your application pod runs as `<license-plate>-vault`, it also uses this SA to pull container images. Add an `ImagePuller` RoleBinding to `<license-plate>-vault` when pulling from `tools`, or attach `imagePullSecrets` to the SA/Deployment when pulling from Artifactory.

### Pod Template Annotations

Place `vault.hashicorp.com/*` annotations on **`spec.template.metadata.annotations`**, never on Deployment `metadata` (see [vault-agent-injector.tpl.yaml](../assets/templates/vault-agent-injector.tpl.yaml)):

```yaml
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/agent-inject-token: "false"
        vault.hashicorp.com/agent-pre-populate-only: "true"
        vault.hashicorp.com/agent-requests-cpu: "10m"
        vault.hashicorp.com/agent-limits-cpu: "50m"
        vault.hashicorp.com/agent-requests-mem: "25Mi"
        vault.hashicorp.com/agent-limits-mem: "100Mi"
        vault.hashicorp.com/auth-path: "auth/k8s-emerald" # or auth/k8s-silver, auth/k8s-gold, auth/k8s-golddr
        vault.hashicorp.com/namespace: "platform-services"
        vault.hashicorp.com/role: "{{ .Values.licenseplate }}-{{ .Values.vaultEngine }}"
        vault.hashicorp.com/agent-inject-secret-app-secrets: "{{ .Values.licenseplate }}-{{ .Values.vaultEngine }}/app-secrets"
        vault.hashicorp.com/agent-inject-template-app-secrets: |
          {{`{{- with secret `}}"{{ .Values.licenseplate }}-{{ .Values.vaultEngine }}/app-secrets"{{` }}
          export DB_PASSWORD="{{ .Data.data.db_password }}"
          {{- end }}`}}
    spec:
      serviceAccountName: "{{ .Values.licenseplate }}-vault"
      containers:
        - name: app
          args: ["sh", "-c", "source /vault/secrets/app-secrets && exec <entrypoint>"]
```

The init container renders files to `/vault/secrets/<secret-name>` (they are not injected as env vars automatically — source them in the container entrypoint). Always set `vault.hashicorp.com/agent-requests-*` and `vault.hashicorp.com/agent-limits-*` annotations on the Pod template so the Vault Agent container does not inherit namespace `LimitRange` defaults (such as `256Mi` memory) and exhaust resource quotas.

## Dynamic Secrets & Data Encryption (Transit)

Beyond static KV v2 storage, BC Gov Vault supports:

- **Dynamic secrets**: Generates short-lived credentials on demand (e.g., PostgreSQL/SQL database keypairs or Azure credentials) with built-in **leasing, renewal, and automatic revocation** when the lease expires (or on-demand tree revocation during incident response).
- **Data encryption (Transit)**: Encrypts and decrypts application payloads without storing them in Vault, letting security teams centrally manage cryptographic parameters while apps store encrypted data in SQL or other backends.

## External Secrets Operator (ESO) — `external-secrets.io/v1`

ESO (`apiVersion: external-secrets.io/v1`) syncs secrets from external systems into OpenShift `Secret` objects (note: OpenShift etcd volumes are encrypted at rest).

| Backend | Auth Pattern | Token Expiry | Recommended Use |
|---|---|---|---|
| **Azure Key Vault / AWS Secrets Manager** | Service Principal (`authSecretRef`) / IAM | Non-expiring (SP/IAM) | **Preferred ESO pattern** for hybrid cloud or non-expiring sync |
| **BC Gov Private Cloud Vault** | `auth.tokenSecretRef` (manual OIDC token) | **Expires after 1 month** | Only if 1-month manual token rotation is acceptable |

### Azure Key Vault SecretStore (Non-Expiring ESO Pattern)

Request an MFA-exempt Microsoft Entra Service Principal from ADMS with `get` and `list` Secret permissions on the Key Vault, store credentials in `azure-key-vault-creds`, and configure `SecretStore` (see [azure-keyvault-secretstore.tpl.yaml](../assets/templates/azure-keyvault-secretstore.tpl.yaml)).

### Private Cloud Vault SecretStore (`tokenSecretRef`)

Because BC Gov Vault uses OIDC, ESO cannot use KSA auth directly and requires `auth.tokenSecretRef` pointing to a Secret (`eso-vault-creds`) holding a manually generated 1-month OIDC token (see [secretstore.yaml](../assets/templates/secretstore.yaml) and [externalsecret.yaml](../assets/templates/externalsecret.yaml)):

```yaml
apiVersion: external-secrets.io/v1
kind: SecretStore
metadata:
  name: vault-secretstore
  namespace: {{ .Values.namespace }}
spec:
  provider:
    vault:
      server: "https://vault.developer.gov.bc.ca"
      namespace: platform-services
      path: "{{ .Values.licenseplate }}-{{ .Values.vaultEngine }}" # <license-plate>-nonprod or -prod
      version: "v2"
      auth:
        tokenSecretRef:
          name: eso-vault-creds
          key: token
```

## Helm Secret — Shape Template Only

Helm `secret.yaml` must never contain real values:

```yaml
# gitops/charts/<app>/templates/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "app.fullname" . }}-secrets
  namespace: {{ .Values.namespace }}
type: Opaque
data: {}
# Populated at runtime by ESO or replaced by Vault Agent Injector file mounts.
```

## GitHub Actions — Vault Integration

> **BC Gov Vault auth constraint**: BC Gov Private Cloud Vault only self-provisions **OIDC** (for the 2 Technical Leads) and **Kubernetes auth** (`auth/k8s-<cluster>`, `<license-plate>-vault` KSA). **`approle` is NOT provisioned by default** — use AppRole in GitHub Actions only if using a custom/self-managed Vault or if AppRole has been explicitly provisioned.

| GitHub Secret | Value |
|---|---|
| `ARTIFACTORY_USERNAME` / `ARTIFACTORY_PASSWORD` | Artifactory service account credentials |
| `GITOPS_TOKEN` | PAT with write access to the GitOps repo |
| `VAULT_ADDR` | `https://vault.developer.gov.bc.ca` |
| `VAULT_NAMESPACE` | `platform-services` |
| `VAULT_ROLE_ID` / `VAULT_SECRET_ID` | AppRole credentials (only if AppRole is separately provisioned; not default BC Gov Vault) |

```yaml
- name: Import secrets from Vault
  uses: hashicorp/vault-action@v3
  with:
    url:       ${{ secrets.VAULT_ADDR }}
    namespace: platform-services
    method:    approle
    roleId:    ${{ secrets.VAULT_ROLE_ID }}
    secretId:  ${{ secrets.VAULT_SECRET_ID }}
    secrets: |
      ${{ env.LICENSE }}-nonprod/data/app-secrets db_password | DB_PASSWORD ;
      ${{ env.LICENSE }}-nonprod/data/app-secrets connection_string | CONNECTION_STRING
```

## Confirmed Facts & Pitfalls

```yaml
confirmed_facts:
  - "KV v2 engines are <license-plate>-nonprod (tools/dev/test) and <license-plate>-prod (prod) under namespace platform-services"
  - "Vault Agent Injector is the KSA-based standard (<license-plate>-vault) for BC Gov Vault"
  - "Cluster K8s auth paths are auth/k8s-silver, auth/k8s-gold, auth/k8s-golddr, auth/k8s-emerald"
  - "ESO uses apiVersion: external-secrets.io/v1; Azure Key Vault / AWS SM is ESO's non-expiring pattern"
  - "ESO with BC Gov Vault requires auth.tokenSecretRef using a manually rotated 1-month OIDC token"
  - "Only 2 Technical Contacts per ProjectSet get OIDC write access in Vault; approle is NOT provisioned by default"
common_pitfalls:
  - "Using hyphens in Vault secret keys (e.g. db-password) breaks OpenShift/vault-init templates — use underscores"
  - "Forgetting VAULT_NAMESPACE=platform-services or vault.hashicorp.com/namespace: platform-services causes permission denied"
  - "Placing vault.hashicorp.com/* annotations on Deployment metadata instead of Pod template metadata"
  - "Forgetting ImagePuller RoleBinding or imagePullSecrets on <license-plate>-vault KSA blocks pod image pulls"
  - "Omitting vault.hashicorp.com/agent-requests-* / agent-limits-* annotations causes the sidecar to inherit 256Mi LimitRange defaults"
```
