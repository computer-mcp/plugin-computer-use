# Versioning and Release

This document owns the current version and release rules for
plugin-computer-use. Shared versioning, plugin compatibility, tags, release
contents and recovery rules belong to the organization's
[VERSIONING.md](https://github.com/computer-mcp/.github/blob/master/VERSIONING.md).
The [release guide](../Reference/Release.md) describes this repository's
acceptance and workflow procedure.

## Components and Version Authority

| Shipped component | Version meaning | Authoritative source | Derived fields | Update and read-only check |
| --- | --- | --- | --- | --- |
| `computer-use.zip` plugin package | Package version | `version` in `computer-mcp-plugin.toml` | builder and release receipts, version tag, catalog entry, the App's bundled index | Edit the manifest; `release.yml` checks agreement with the tag |
| Manifest and host runtime contract | Plugin API version | `plugin_api` in `computer-mcp-plugin.toml` | release receipt and host compatibility evaluation | Package tests check the declaration; `release.yml` verifies it |

The archive contains the README, contribution guide, manifest, license, notices,
`skills/` and `Documentation/`. Changes to tests, scripts or workflows alone do
not change the archive.

## Dependencies and Verified Combinations

The package is a declaration: it registers the vendor's native Computer Use MCP
client and ships no runtime code. The manifest locates that client by command
name or application bundle, and the vendor owns its installation and caller
authentication.

The manifest owns this package's plugin API declaration and host compatibility
bounds. A host-version constraint is changed only after validating the package
against the required host.

The builder needs only the Python 3.11 standard library. CI runs the tests and
build on Python 3.11 and 3.13.

## Derived Metadata and Drift Checks

`Scripts/build_package.py` verifies the plugin ID, skips hidden files and Python
caches, rejects links and special files, and produces the same archive bytes
from the same source. `Tests/test_build_package.py` checks the plugin API
declaration and pins the exact archive file set. The builder receipt prints the
ID, version and SHA-256.

## Candidate, Acceptance and Publication

The candidate is the `computer-use-plugin-<commit>` artifact from a successful
`master` push run of `ci.yml` for a reviewed commit. Acceptance requires a
byte-identical local rebuild, host package validation and installation of that
exact archive, and native catalog discovery with the installed vendor client.
Native actions remain subject to the vendor's caller authentication and system
permissions; acceptance records what was observed and does not assume a working
action path.

`release.yml` calls the shared release workflow with `Scripts/build-package.sh`
and this repository's exact CI artifact name. Manual acceptance results belong
in the Release notes. After verified publication, its dependent notifier calls
`notify-catalog.yml`.

The Computer MCP App bundles a copy of this package, pinned by version and
SHA-256 in the App repository's `Resources/PluginArchives/index.json`. Before
the first release, the host may bundle an archive reproducibly built from an
accepted commit before that plugin version is published. A host release
requires the plugin release with the same archive digest to be public first.

## Evidence Reuse and Invalidation

The CI artifact name binds the source commit, and the builder receipt binds the
archive SHA-256. An archive whose digest matches the accepted one keeps its
acceptance. Any change to a packaged file produces a new archive that needs the
affected checks again.

## Entry Points and Artifact Retention

| Operation | Existing command or explicit manual procedure | Required access |
| --- | --- | --- |
| Version update and check | Edit `computer-mcp-plugin.toml`; `python3 -m unittest discover -s Tests -p 'test_*.py'` | Local checkout |
| Candidate validation and build | `ci.yml`; locally `Scripts/build-package.sh <output-directory>` | CI or local checkout |
| Release verification and publication | Dispatch `release.yml`, dry run first; manual acceptance in [Release](../Reference/Release.md) | Repository Actions; publication also needs a signed tag and release write access |
| Status and interrupted-run recovery | Rerun failed workflow jobs; follow the shared recovery rules | Repository Actions |
| Cleanup | Delete local output and evidence directories | Local checkout |

CI keeps candidate artifacts for 14 days. The builder refuses to overwrite a
different archive. Keep local evidence outside the repository.
