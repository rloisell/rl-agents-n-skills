# BC Gov Hosting Tiers, CNI/SDN & Porter TCP Connectivity

## Contents

- [Hosting Tiers Comparison](#hosting-tiers-comparison)
- [SDN vs NSX-T vs OVN-Kubernetes](#sdn-vs-nsx-t-vs-ovn-kubernetes)
- [Porter Operator TransportServerClaim](#porter-operator-transportserverclaim)
- [OVN-Kubernetes NodePort Migration (Feb 2026)](#ovn-kubernetes-nodeport-migration-feb-2026)
- [Security & NetworkPolicy Requirements](#security--networkpolicy-requirements)

## Hosting Tiers Comparison

| Attribute | Silver | Gold / GoldDR | Emerald |
| --- | --- | --- | --- |
| **Target Uptime (30-day rolling)** | 90% single-node / 99.5% multi-node (<= 4h outage) | **99.95% ONLY** with multi-node + Calgary DR failover (<= 22m outage); without DR, matches Silver (90% / 99.5%) | 90% single-node / 99.5% multi-node (<= 4h outage) |
| **Max Data Sensitivity** | Protected B at rest; Protected C processing-only (stored elsewhere) | Protected B at rest; Protected C processing-only (stored elsewhere) | Protected C storage and/or processing |
| **Integrated HA / DR** | `TransportServerClaim` | `TransportServerClaim` (Gold ↔ GoldDR) + Global Load Balancing (Active/Passive DR) | None |
| **OpenShift Upgrade Plan** | N-1 tracking Red Hat point releases | N-1 tracking Red Hat point releases | Extended Update Support (EUS), even-numbered releases only |
| **Scalability Limits** | 1500 CPU cores / 30TB storage / 10G | 225 CPU cores / 16TB storage / 10G | 175 CPU cores / 16TB storage / 10G |
| **Egress & Internet** | Shared cluster egress IP (STMS-Classic); direct internet egress | Shared cluster egress IP (STMS-Classic); direct internet egress | Per-namespace egress subnet (STMS-Classic); proxy-only internet egress (approved workloads) |
| **API & App Exposure** | Public internet access to cluster API and hosted apps | Public internet access to cluster API and hosted apps | **API inside SPAN-BC only**; hosted apps may be granted public internet access; VM-SDN access |
| **Authentication** | GitHub (bcgov org + IDIR link) or IDIR (MFA required) | GitHub (bcgov org + IDIR link) or IDIR (MFA required) | **IDIR MFA only** |

## SDN vs NSX-T vs OVN-Kubernetes

| Cluster Tier | Network Provider | Egress NetworkPolicy Support | Key Operational Notes |
| --- | --- | --- | --- |
| **Silver / Gold / GoldDR** (legacy) | OpenShift SDN | **Limited Egress**: `.spec.egress.to.ipBlock` and `.except` only | Cannot target `namespaceSelector` or `podSelector` in egress rules |
| **Silver / Gold / GoldDR** (target) | **OVN-Kubernetes** | Full Kubernetes NetworkPolicy egress & ingress | Requires `type: NodePort` Services for Porter `TransportServerClaim` (effective Feb 2026) |
| **Emerald** (and KLAB2) | **VMware NSX-T** | Full Egress NetworkPolicies supported and required | Default-deny egress; requires `allow-egress-dns` and explicit egress rules |

## Porter Operator TransportServerClaim

Use the Porter Operator (`porter.devops.gov.bc.ca/v1alpha1`) to expose non-HTTPS TCP services on **Silver** or establish cross-cluster TCP connectivity between **Gold** (Kamloops) and **GoldDR** (Calgary), such as database replication.

### Standard Cross-Cluster or Silver Manifest

Create `TransportServerClaim` (`tscs`) in **Silver** or in **Gold only** (never in GoldDR — the operator creates `TransportServer` (`ts`) resources in both Gold and GoldDR, plus cross-connect endpoints `<svc>-gold` and `<svc>-golddr`, or `<svc>-<port>-<cluster>` for multi-port Services):

```yaml
apiVersion: porter.devops.gov.bc.ca/v1alpha1
kind: TransportServerClaim
metadata:
  name: <app-name>-tsc
  namespace: <license-plate>-dev
spec:
  monitor:
    interval: 10
    timeout: 10
    type: tcp
  overrideServicePort: true # Optional: keeps local cross-connect Service port matching servicePort
  service: <app-name>
  servicePort: 8000
```

### Standalone Mode on Gold (Without GoldDR)

To expose a Gold service directly via TCP without creating GoldDR cross-connect Services, add `mode: Standalone`:

```yaml
apiVersion: porter.devops.gov.bc.ca/v1alpha1
kind: TransportServerClaim
metadata:
  name: <app-name>-standalone
  namespace: <license-plate>-dev
spec:
  mode: Standalone
  monitor:
    interval: 10
    timeout: 10
    type: tcp
  service: <app-name>
  servicePort: 8000
```

Inspect the generated virtual server IP and port with `oc -n <license-plate>-dev get ts` (`VIRTUALSERVERADDRESS` / `VIRTUALSERVERPORT`) or `oc -n <license-plate>-dev get endpoints | grep gold`.

## OVN-Kubernetes NodePort Migration (Feb 2026)

As of **February 2026**, Services targeted by a `TransportServerClaim` MUST use `type: NodePort` instead of `ClusterIP` to remain functional after clusters switch to **OVN-Kubernetes**.

1. Update the target Service to `NodePort` (in both Gold and GoldDR for cross-cluster):

```bash
oc -n <license-plate>-dev patch svc <app-name> -p '{"spec":{"type":"NodePort"}}'
```

2. Trigger Porter Operator resync by patching a spec field (e.g., monitor interval), then revert if desired:

```bash
oc -n <license-plate>-dev patch tscs <app-name>-tsc --type=merge -p '{"spec":{"monitor":{"interval":30}}}'
```

3. Changing from `ClusterIP` to `NodePort` updates the `TransportServer` IP addresses on both sides while keeping the port unchanged. Schedule the change in a maintenance window and update any firewall rules to the new `VIRTUALSERVERADDRESS`.

## Security & NetworkPolicy Requirements

> **SPAN-BC-Wide Exposure Warning**: A `TransportServerClaim` functions like a Route — you **cannot** restrict source IPs using a Kubernetes `NetworkPolicy`. Any endpoint exposed via Porter is reachable by **all SPAN-BC users within the datacenter**. Always secure the service at the application/transport layer using **strong authentication (username/password)** or **mutual TLS (mTLS)** commensurate with data sensitivity.

Every namespace using a `TransportServerClaim` (both Gold and GoldDR for cross-cluster) requires an ingress `NetworkPolicy` allowing traffic from the F5/ingress load balancers to the Service's pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-f5-ingress
  namespace: <license-plate>-dev
spec:
  podSelector:
    matchLabels:
      app: <app-name>
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              network.openshift.io/policy-group: ingress
```
