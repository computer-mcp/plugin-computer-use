# Release

Release status: [CI](https://github.com/computer-mcp/plugin-computer-use/blob/master/.github/workflows/ci.yml)
builds candidate archives on pull requests, `master` pushes and manual runs.
[`release.yml`](https://github.com/computer-mcp/plugin-computer-use/blob/master/.github/workflows/release.yml)
implements dry runs and publication; native and host acceptance are manual.

The organization [VERSIONING](https://github.com/computer-mcp/.github/blob/master/VERSIONING.md)
owns version rules, including tags, version choice and the changelog. This
reference records this repository's version sources, compatibility, release
procedure and checks. The shared
[release workflow guide](https://github.com/computer-mcp/github-workflows/blob/master/docs/plugin-release.md)
describes workflow verification and recovery.

## Components and Version Sources

| Shipped component | Version meaning | Version source | Mirrors and derived fields | Update and read-only check |
| --- | --- | --- | --- | --- |
| `computer-use.zip` plugin package | Package version | `version` in [`computer-mcp-plugin.toml`](../../computer-mcp-plugin.toml) | builder and release receipts, release tag, catalog entry, the App's bundled index | Edit the manifest; `release.yml` checks agreement with the tag |
| Manifest and host runtime contract | Plugin API version | `plugin_api` in [`computer-mcp-plugin.toml`](../../computer-mcp-plugin.toml) | release receipt and host compatibility evaluation | Package tests check the declaration; `release.yml` verifies it |

The archive contains the README, contribution guide, manifest, license, notices,
`skills/`, `docs/` and the README images `.github/assets/logo/logo-light.png`
and `.github/assets/logo/logo-dark.png`. Tests, build scripts and workflows
are excluded from the archive.

## Compatibility Surface

The package contributes the vendor's native stdio MCP registration and portable
observe–act–verify guidance. [Package architecture](../Architecture/Package.md)
owns executable discovery and the host/vendor authority boundaries. Native
tool behavior and caller authentication belong to the vendor.

The manifest owns the plugin API declaration and host compatibility bounds.
Validate changes to those bounds against the required host.

## Dependencies and Verified Combinations

The package is a declaration: it registers the vendor's native Computer Use MCP
client and ships no runtime code. The manifest locates that client by command
name or application bundle, and the vendor owns its installation and caller
authentication.

The builder needs only the Python 3.11 standard library. CI runs the tests and
build on Python 3.11 and 3.13. Package checks do not establish compatibility of
a particular vendor client, caller or GUI target; native discovery and action
acceptance identify the combination actually observed.

## Derived Metadata and Drift Checks

`scripts/build_package.py` verifies the plugin ID, explicitly includes the README
logo images, skips hidden files and Python caches when traversing content trees,
rejects links and special files, and produces the same archive bytes from the
same source. `tests/test_build_package.py` checks the plugin API
declaration and pins the exact archive file set. The builder receipt prints the
ID, version and SHA-256.

## Candidate, Acceptance and Publication

Publication depends on the repository's GitHub release immutability setting.
The shared workflow checks that setting before writing a Release.

### Publish

1. Confirm that `version` in `computer-mcp-plugin.toml` has not been released
   and that the reviewed `master` commit has a successful `push` run of
   `ci.yml`, including its `computer-use-plugin-<commit>` artifact.
2. Dispatch `release.yml` with `ref` set to that full commit SHA and `publish`
   set to `false` (the default). The workflow rebuilds with
   `scripts/build-package.sh` and compares the archive bytes with the exact CI
   artifact. Inspect the `plugin-release-<run-id>-<attempt>` Actions artifact:
   `assets/` contains `computer-use.zip`, `release-receipt.json` and `SHA256SUMS`.
   An untagged dry run reports the signed annotated tag still required for
   publication.
3. Rebuild the same commit with `scripts/build-package.sh <output-directory>`
   and confirm it matches the dry-run archive. Validate and install that exact
   archive with the selected Computer MCP host, and confirm native catalog
   discovery with the installed vendor client. GUI checks use a disposable,
   explicitly authorized target.
4. Create the version tag that [VERSIONING](https://github.com/computer-mcp/.github/blob/master/VERSIONING.md) requires on the accepted commit and push it.
   Create a draft GitHub Release for that tag, targeting the full commit SHA,
   and record the manual acceptance results and their limits in its notes.
5. Dispatch `release.yml` with `ref` set to that version tag and `publish` set
   to `true`. The workflow verifies the tag, manifest, CI source and archive
   bytes, completes the draft's assets and publishes the verified release.
   Confirm the public release is immutable and its archive digest matches the
   accepted archive.

The public assets are `computer-use.zip`, the shared `release-receipt.json` and
`SHA256SUMS`. CI's `package-receipt.json` remains builder evidence in the CI
artifact.

### App distribution

The Computer MCP App bundles a copy of this package, pinned by version and
SHA-256 in the App repository's `Resources/PluginArchives/index.json`. Before
the first release, the host may bundle an archive reproducibly built from an
accepted commit before that plugin version is published. A host release
requires the plugin release with the same archive digest to be public first.

### Catalog notification

`release.yml` calls `notify-catalog.yml` only when `publish` is `true` and the
shared release workflow reports `published: true`. Only the notifier job
receives the catalog App private key; the shared release workflow receives no
secret inputs. This explicit call handles publication through `GITHUB_TOKEN`,
which does not trigger release-event workflows.

`notify-catalog.yml` also runs when a release is published, edited, released,
unpublished or deleted, and on manual dispatch. It asks the website to
reconcile the complete catalog. The website verifies the actual GitHub
releases rather than the event payload, keeps verified history, and applies
its own withdrawal policy; an event never withdraws a release by itself.

The workflow authenticates as the receiver-scoped catalog GitHub App through
the `CATALOG_APP_CLIENT_ID` variable and the `CATALOG_APP_PRIVATE_KEY` secret.
The App needs Actions write access to `computer-mcp/computer-mcp.github.io` only.
The job checks this repository's immutable ID, does not check out package code,
and grants its own token no repository permissions. Missing or rejected
authority fails the run visibly.

The shared notification action is pinned to a reviewed full commit of
`computer-mcp/github-workflows`. Publish that commit first, then update the pin
here when adopting a change to the notification contract.

## Evidence Reuse and Invalidation

The CI artifact name identifies the source commit, and the builder receipt records
the archive SHA-256. The release workflow verifies CI provenance and artifact
digests; `release-receipt.json` records the commit, CI run and attempt, artifact
digest and archive SHA-256.

An archive with the accepted digest keeps its archive acceptance for the tested
combination. Reuse of manual results is reviewed against the native dependency,
selected host, check definitions and relevant environment recorded with them.
Changes to packaged files produce a new archive and require the affected checks
again. A check-only change can reuse unchanged archive bytes with fresh affected
checks. Source tests do not replace installation, native or authenticated
execution evidence. Keep failed-check output and result limits with the manual
acceptance record.

## Entry Points and Artifact Retention

| Operation | Existing command or explicit manual procedure | Required access |
| --- | --- | --- |
| Version update and check | Edit `computer-mcp-plugin.toml`; `python3 -m unittest discover -s tests -p 'test_*.py'` | Local checkout |
| Candidate validation and build | `ci.yml`; locally `scripts/build-package.sh <output-directory>` | CI or local checkout |
| Native and host acceptance | Validate and install the exact archive with the selected host; verify native catalog discovery and authorized GUI behavior | Selected host, vendor client and authorized disposable target |
| Acceptance and publication | Manual checks above; dispatch `release.yml`, dry run first | Repository Actions; publication also needs a signing key and release write access |
| Status and interrupted-run recovery | Inspect CI or `release.yml`; follow [Retry](#retry) | Repository Actions |
| Cleanup | Delete obsolete local output and evidence directories | Local checkout |

CI keeps candidate artifacts for 14 days. The builder refuses to overwrite a
different archive. Local package output belongs in ignored `dist/`; keep
manual evidence outside the repository and retain it while the acceptance
record requires it.

### Retry

For an interrupted publication, use **Re-run failed jobs** and follow the shared
workflow guide's recovery rules. If verification already succeeded, the publish
job reuses its verified bundle and digest outputs.

For a missed or failed notification, rerun only the notifier job or dispatch:

```sh
gh workflow run notify-catalog.yml --repo computer-mcp/plugin-computer-use --ref master
```

A successful dispatch only proves the request was accepted. Follow the run's
`run_url` output to the website run, confirm it succeeded, and confirm the public
index lists the expected release. Retrying never requires changing or
republishing the release: reconciliation is idempotent, and the website's
hourly schedule also repairs missed notifications.

The website's
[catalog publication and notification contract](https://github.com/computer-mcp/computer-mcp.github.io/blob/master/docs/plugin-catalog.md)
covers provenance, credentials, retry bounds and deployment.
