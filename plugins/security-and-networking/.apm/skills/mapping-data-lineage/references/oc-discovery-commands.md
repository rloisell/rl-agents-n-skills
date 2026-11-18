# OpenShift Discovery Commands for Data Flow Lineage

Run these read-only `oc` and `jq` commands against a target namespace `<ns>` to inventory cross-service endpoints, message streams, and external cloud services.

```bash
# Find all cross-service URL references in ConfigMaps
oc get configmaps -n <ns> -o json | \
  jq '.items[] | .data | to_entries[] | select(.value | test("https?://")) | {key, value}'

# Find all external hostname references in deployment environment variables
oc get deployments -n <ns> -o json | \
  jq '.items[].spec.template.spec.containers[].env[]? |
      select(.value? | test("https?://|smtp:|redis://")) |
      {name, value}'

# Find message stream/topic/queue keys (PII carrier risk — streams may carry Protected B data)
oc get configmaps -n <ns> -o json | \
  jq '.items[] | .data | to_entries[] |
      select(.key | test("STREAM|TOPIC|QUEUE")) | {key, value}'

# Find cloud provider or cognitive/AI endpoints across deployments and ConfigMaps
oc get deployments,configmaps -n <ns> -o json | \
  jq '.. | strings | select(test("azure|amazonaws|googleapis|cognitive"))'
```
