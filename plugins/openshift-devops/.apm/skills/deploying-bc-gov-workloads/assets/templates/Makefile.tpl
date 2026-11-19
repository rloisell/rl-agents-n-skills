CHART_PATH    := ./gitops
ENV           ?= dev
RELEASE       := @@PROJECT@@
POLICY_DIR    ?= ./policies

.PHONY: deps render validate lint deploy

deps:
	helm dependency update $(CHART_PATH)

render: deps
	helm template $(RELEASE) $(CHART_PATH) \
	  --values $(CHART_PATH)/values.yaml \
	  --values $(CHART_PATH)/values-$(ENV).yaml \
	  > rendered.yaml

validate: render
	datree test rendered.yaml --policy-config $(POLICY_DIR)/datree-policies.yaml
	polaris audit --config $(POLICY_DIR)/polaris.yaml --format pretty rendered.yaml
	kube-linter lint rendered.yaml --config $(POLICY_DIR)/kube-linter.yaml
	conftest test rendered.yaml --policy $(POLICY_DIR) --all-namespaces --fail-on-warn

lint:
	helm lint $(CHART_PATH) \
	  --values $(CHART_PATH)/values.yaml \
	  --values $(CHART_PATH)/values-$(ENV).yaml

deploy: validate
	helm upgrade --install $(RELEASE) $(CHART_PATH) \
	  --values $(CHART_PATH)/values.yaml \
	  --values $(CHART_PATH)/values-$(ENV).yaml \
	  --namespace @@NAMESPACE_DEV@@ \
	  --wait --timeout 5m

# Override POLICY_DIR if policy configs live elsewhere:
#   make validate POLICY_DIR=/path/to/policies
