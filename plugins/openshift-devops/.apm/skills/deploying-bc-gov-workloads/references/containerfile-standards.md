# Containerfile Standards

All container images for BC Gov Emerald OpenShift workloads must follow these patterns.

## Port Rule

**Always expose port `8080` inside containers.** Never 80, 443, 5000, or 5005.
OpenShift Routes and the AVI load balancer handle TLS externally.

---

## .NET API Containerfile

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /app
COPY . .
RUN dotnet publish -c Release -o /publish

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY --from=build /publish .
USER appuser
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:8080/health/live || exit 1
ENTRYPOINT ["dotnet", "<AppName>.dll"]
```

---

## React / Vite Frontend Containerfile

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
EXPOSE 8080
RUN apk add --no-cache wget
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
USER appuser
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -q -O /dev/null http://localhost:8080/nginx-health || exit 1
```

---

## Runtime Config — Frontend API URL

**Never** bake `VITE_API_URL` at build time. Use a `/config.json` served by Nginx
so one image works across dev, test, and prod.

### Nginx location block

```nginx
location = /config.json {
    alias /usr/share/nginx/html/config.json;
    add_header Cache-Control "no-cache";
}
```

### React app fetch (`main.jsx`)

```javascript
// top-level await requires build.target: 'esnext' in vite.config.js
const config = await fetch('/config.json').then(r => r.json()).catch(() => ({
  apiUrl: 'http://localhost:5200',
}));
window.__env__ = config;
```

The Helm chart writes `config.json` into the container via a ConfigMap at deploy time.

---

## Common Rules

- Non-root user `appuser` on all containers — `USER appuser` as final instruction
- `cap_drop: [ALL]` and `security_opt: [no-new-privileges: true]` in compose files
- Install `curl` (API) or `wget` (frontend) for health checks
- `HEALTHCHECK` required on every image pointing at `/health/live` or `/nginx-health`

---

## PID 1 Init Reaper (Preventing Defunct / Zombie PIDs)

Containers that spawn child processes (including `exec` readiness/liveness probes or multi-process workers) can accumulate **defunct (zombie) PIDs** if PID 1 does not reap exited children, threatening OpenShift node kernel stability and triggering platform defunct-PID alerts.

- **Immediate mitigation**: Delete the affected pod to clear accumulated zombies and restart cleanly.
- **Permanent fix**: Wrap your container `ENTRYPOINT` with a lightweight init reaper such as **`Tini`** (`ENTRYPOINT ["/sbin/tini", "--", ...]`), **`dumb-init`** (`ENTRYPOINT ["/usr/bin/dumb-init", "--", ...]`), or **`s6-overlay`** so orphaned child processes are reaped as PID 1. Also review `exec` health probes to ensure they do not leave unwaited subshells.
