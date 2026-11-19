# .NET CI Automation Patterns

Reusable GitHub Actions CI patterns for .NET APIs covering dependency vulnerability scanning, formatting enforcement, EF Core migration script artifacts, merged Coverlet coverage gating, gRPC builds, and NuGet packaging/publishing.

## Contents

- [Dependency Restore & Vulnerability Scanning](#dependency-restore--vulnerability-scanning)
- [Code Formatting Enforcement](#code-formatting-enforcement)
- [EF Core Migration Script Artifact](#ef-core-migration-script-artifact)
- [Merged Coverlet & Cobertura Coverage Gating](#merged-coverlet--cobertura-coverage-gating)
- [gRPC Build with `protoc`](#grpc-build-with-protoc)
- [NuGet Pack & Deploy](#nuget-pack--deploy)

## Dependency Restore & Vulnerability Scanning

Restore dependencies, optionally configure authenticated NuGet feeds, and fail or report on known vulnerable packages with `dotnet list package --vulnerable`:

```yaml
- uses: actions/setup-dotnet@v4
  with:
    dotnet-version: "8.0.x" # or "10.0.x"
    cache: true

- name: Configure NuGet auth (optional)
  if: ${{ secrets.NUGET_AUTH_TOKEN != '' }}
  shell: bash
  run: |
    dotnet nuget add source "https://api.nuget.org/v3/index.json" --name nuget.org || true
    dotnet nuget update source nuget.org --username "USERNAME" --password "${{ secrets.NUGET_AUTH_TOKEN }}" --store-password-in-clear-text || true

- name: Restore
  shell: bash
  run: dotnet restore ${{ inputs.dotnet_build_path }}

- name: Dependency vulnerability scan
  shell: bash
  run: dotnet list package --vulnerable
```

Cache `**/obj/` keyed on `hashFiles('**/*.csproj')` when passing restored state across jobs.

## Code Formatting Enforcement

Enforce `.editorconfig` and analyzer formatting rules in CI without mutating workspace files:

```bash
dotnet restore "${PROJECT_PATH:-.}"
dotnet format --verify-no-changes --severity error "${PROJECT_PATH:-.}"
```

## EF Core Migration Script Artifact

Generate an idempotent SQL migration script in CI so DBAs or release pipelines can review and apply schema changes deterministically:

```bash
dotnet tool install -g dotnet-ef
export PATH="$PATH:$HOME/.dotnet/tools"
dotnet-ef migrations script -o "<out.sql>" -i -s "<startup-project>"
```

- `-i` (`--idempotent`) guards every migration with `__EFMigrationsHistory` checks so the script can be safely re-run.
- `-s` points to the startup project containing `Program.cs` / `appsettings.json` / `DbContext` registration.
- Upload `<out.sql>` as a workflow artifact for release approval.

## Merged Coverlet & Cobertura Coverage Gating

Run unit and integration test suites sequentially, merge Coverlet JSON outputs with `/p:MergeWith`, emit Cobertura XML, generate an HTML report, and enforce both line and branch thresholds (`80%` default):

```bash
set -euo pipefail
export PATH="$PATH:$HOME/.dotnet/tools"

LOG_FOLDER="${GITHUB_WORKSPACE}/TestResults"
COV_THRESHOLD="${COV_THRESHOLD:-80}"
COV_THRESHOLD_TYPE="${COV_THRESHOLD_TYPE:-line,branch}"
COV_EXCLUSIONS="${COV_EXCLUSIONS:-DebuggerNonUserCodeAttribute}"

dotnet tool install -g dotnet-reportgenerator-globaltool
sudo apt-get update && sudo apt-get install -y bc libxml2-utils

mkdir -p "$LOG_FOLDER/coverage"

for FOLDER in $UNIT_TEST_FOLDER; do
  dotnet test "./$FOLDER" --configuration Release \
    --logger "junit;LogFileName=$LOG_FOLDER/{assembly}UnitTestResults.xml" \
    /p:CollectCoverage=true \
    /p:CoverletOutput="$LOG_FOLDER/coverage/" \
    /p:MergeWith="$LOG_FOLDER/coverage/coverage.json" \
    /p:CoverletOutputFormat="cobertura,json" \
    /p:ExcludeByAttribute="$COV_EXCLUSIONS" \
    ${COV_EXCLUDE_FILTER:+/p:Exclude="$COV_EXCLUDE_FILTER"}
done

for FOLDER in $INTEGRATION_TEST_FOLDER; do
  dotnet test "./$FOLDER" --configuration Release \
    --logger "junit;LogFileName=$LOG_FOLDER/{assembly}IntegrationTestResults.xml" \
    /p:CollectCoverage=true \
    /p:CoverletOutput="$LOG_FOLDER/coverage/" \
    /p:MergeWith="$LOG_FOLDER/coverage/coverage.json" \
    /p:CoverletOutputFormat=cobertura \
    /p:ExcludeByAttribute="$COV_EXCLUSIONS" \
    ${COV_EXCLUDE_FILTER:+/p:Exclude="$COV_EXCLUDE_FILTER"}
done

COVERAGE_LINE=$(echo "scale=2; $(xmllint --xpath 'string(//coverage/@line-rate)' "$LOG_FOLDER/coverage/coverage.cobertura.xml")*100/1" | bc)
COVERAGE_BRANCH=$(echo "scale=2; $(xmllint --xpath 'string(//coverage/@branch-rate)' "$LOG_FOLDER/coverage/coverage.cobertura.xml")*100/1" | bc)

reportgenerator -reports:"$LOG_FOLDER/coverage/coverage.cobertura.xml" -targetdir:"$LOG_FOLDER/coverage" -reporttypes:HTML

if [[ "$COV_THRESHOLD_TYPE" == *"branch"* ]] && [[ $(echo "$COVERAGE_BRANCH < $COV_THRESHOLD" | bc) -eq 1 ]]; then
  echo "Branch coverage ($COVERAGE_BRANCH%) below threshold ($COV_THRESHOLD%)!"
  exit 1
fi
if [[ "$COV_THRESHOLD_TYPE" == *"line"* ]] && [[ $(echo "$COVERAGE_LINE < $COV_THRESHOLD" | bc) -eq 1 ]]; then
  echo "Line coverage ($COVERAGE_LINE%) below threshold ($COV_THRESHOLD%)!"
  exit 1
fi
```

## gRPC Build with `protoc`

Install `protoc` before running `dotnet build` for services or shared contracts compiling `.proto` files:

```yaml
- name: Install protoc
  uses: arduino/setup-protoc@v3
  with:
    repo-token: ${{ github.token }}

- name: Build
  shell: bash
  run: |
    set -euo pipefail
    VERSION_PREFIX_PARAM=""
    [[ -n "${VERSION_PREFIX:-}" ]] && VERSION_PREFIX_PARAM="-p:VersionPrefix=${VERSION_PREFIX}"
    VERSION_SUFFIX_PARAM=""
    [[ -n "${VERSION_SUFFIX:-}" ]] && VERSION_SUFFIX_PARAM="--version-suffix=${VERSION_SUFFIX}"
    WARN=""
    [[ "${WARN_AS_ERROR:-false}" == "true" ]] && WARN="/p:TreatWarningsAsErrors=true /warnaserror"
    dotnet build ${DOTNET_BUILD_PATH:-} --configuration Release $WARN $VERSION_PREFIX_PARAM $VERSION_SUFFIX_PARAM
```

## NuGet Pack & Deploy

Pack libraries into `.cinuget/` with repository metadata, then push idempotently using `--skip-duplicate`:

```bash
set -euo pipefail
REPO_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}"

mkdir -p .cinuget
dotnet restore
dotnet pack --configuration Release --no-build --output .cinuget --verbosity normal \
  ${VERSION_PREFIX:+-p:VersionPrefix="$VERSION_PREFIX"} \
  ${VERSION_SUFFIX:+--version-suffix="$VERSION_SUFFIX"} \
  -p:NoDefaultExcludes="${NO_DEFAULT_EXCLUDES:-false}" \
  -p:RepositoryUrl="$REPO_URL" \
  -p:PackageProjectUrl="$REPO_URL"
```

Publish `.nupkg` artifacts to GitHub Packages (or a custom feed) with either username/password or API key:

```bash
set -euo pipefail
FEED="${NUGET_FEED:-https://nuget.pkg.github.com/${GITHUB_REPOSITORY_OWNER}/index.json}"
dotnet nuget add source "$FEED" --name ci-feed --username "${NUGET_USER:-token}" --password "${NUGET_TOKEN}" --store-password-in-clear-text

cd .cinuget
dotnet nuget push "*.nupkg" -s "$FEED" --skip-duplicate
```
