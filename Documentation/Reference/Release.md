# Release

This guide covers publishing an accepted package through
[`release.yml`](../../.github/workflows/release.yml) and notifying the official
plugin catalog. [Versioning and Release](../Architecture/VersioningAndRelease.md)
owns this repository's version and acceptance rules. The organization's
[VERSIONING.md](https://github.com/computer-mcp/.github/blob/master/VERSIONING.md)
and [release workflow guide](https://github.com/computer-mcp/.github/blob/master/Documentation/Reference/PluginRelease.md)
own the shared release contents, immutability and recovery contract.

## Prerequisite

Before the first release, the repository owner must enable GitHub release
immutability in repository settings. The release workflow checks that setting
before any Release write and refuses publication if it is disabled or cannot
be verified. Enabling it does not lock previously published releases; an
existing public release must itself be immutable to be accepted by the workflow.

## Publish

1. Confirm that `version` in `computer-mcp-plugin.toml` has not been released
   and that the reviewed `master` commit has a successful `push` run of
   `ci.yml`, including its `computer-use-plugin-<commit>` artifact.
2. Dispatch `release.yml` with `ref` set to that full commit SHA and `publish`
   set to `false` (the default). The workflow rebuilds with
   `Scripts/build-package.sh` and compares the archive bytes with the exact CI
   artifact. Inspect the `plugin-release-<run-id>-<attempt>` Actions artifact:
   `assets/` contains `computer-use.zip`, `release-receipt.json` and `SHA256SUMS`.
   An untagged dry run reports the signed annotated tag still required for
   publication.
3. Rebuild the same commit with `Scripts/build-package.sh <output-directory>`
   and confirm it matches the dry-run archive. Validate and install that exact
   archive with the selected Computer MCP host, and confirm native catalog
   discovery with the installed vendor client. GUI checks use a disposable,
   explicitly authorized target.
4. Create a signed annotated tag `vX.Y.Z` on the accepted commit and push it.
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

## Catalog notification

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

The website's notification action is pinned to a reviewed full commit. Publish
that website commit first, then update the pin here when adopting a change to
the notification contract.

## Retry

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
