# Host integration

## Declarations and authority

The package requests Screen and Desktop control for owner review. The host owns
activation, executable bindings, exposure, permission grants and execution mode.
Each call requires caller Plugin use and the resolved effects from both caller
and provider. Reading the passive skill requires Skills and Plugin use.

Native downstream names and effects have not been verified for a supported
vendor/caller combination. The manifest therefore has neither a default nor a
per-tool requirement map. The host's undeclared-tool rule requires the provider's
held sensitive permissions at their effective levels and targets, except Machine
information and Skills. It does not infer a smaller set from read-only hints.
Host minimum effects remain additive. A native effect absent from the reviewed
map cannot be proved by synthetic test names.

Sandbox settings are omitted: the draft uses the host's minimum sandbox, network
none and no configuration read exceptions. This is a declaration, not a native
compatibility result. Discovery must run projectless, writing only the provider
container and private scratch, even if an invocation later uses Full access.
Provider HOME/cache/state persist in the host-owned container. Container contents
are not permission grants. An owner must confirm the shipped mode after real
vendor state, login, configuration, network and external-write facts are known.

## Deterministic source consumer

The source-only peer in `tests/fixtures/native_mcp.c` implements bounded test
operations without using desktop APIs. Its three `fixture_*` tools are synthetic;
none is a claimed native tool name. The Swift companion first registers the
actual package unchanged, proves disabled registration and reviewed approval,
and exercises conservative requirements. Separate temporary package copies add
synthetic overrides/defaults to exercise exact-name resolution, complete default
replacement and additive host effects. Missing provider/caller effects are tested
against those explicit synthetic declarations.

The companion uses the host's existing `FixedHostFixture`, PluginStore and
permission services, plus a separate restricted consumer identity. Owner setup
and cleanup identities retain their original grants. It tests missing grants,
explicit denies, answered requests without automatic dispatch, explicit matching
retry, exposure, stale declarations, disable/revocation, discovery state and
joined process ownership. Peer logs count actual dispatches independently of
returned errors. Startup probes verify container/scratch writes and refusal of a
disposable outside write. No vendor executable, account, GUI or TCC flow is used.

Run Python checks without building the package:

```sh
python3 -B -m unittest discover -s tests -p 'test_source_declarations.py'
COMPUTER_MCP_CUA_TEST_OUTPUT="$EVIDENCE_DIRECTORY" \
  python3 -B -m unittest discover -s tests -p 'test_validate_host_source.py'
```

`EVIDENCE_DIRECTORY` must already exist outside this repository. Driver tests use
it for disposable files; absent this input, they use the system temporary area.
The package's regular build/content tests remain part of its full delivery gate.

On macOS with the host's required Swift toolchain and dependencies, run the source
consumer against two explicit clean committed source checkouts:

```sh
python3 -B scripts/validate_host_source.py \
  --host-source "$HOST_SOURCE" --host-sha "$HOST_SHA" \
  --plugin-source "$PLUGIN_SOURCE" --plugin-sha "$PLUGIN_SHA" \
  --output "$EVIDENCE_DIRECTORY/source-consumer" --timeout 900
```

Both SHA inputs must be full lowercase 40-character commits matching checkout
HEAD. The output must be new and outside both checkouts and their ancestors.
The driver checks cleanliness, exports both exact commits, copies the companion
into the exported host test target and invokes only that suite. It never edits
input source checkouts or uses an installed-App control socket. SwiftPM may need
its normal package dependencies; no vendor software is installed. Execution has
a deadline and log bound. The receipt requires fresh run-specific evidence with
nonzero executed tests and the complete case set, rather than exit status alone.

The driver removes its exported sources and build tree, retaining logs, case
results and a receipt outside the repositories. A failed or interrupted fixture
without joined-process evidence is reported as runtime cleanup unverified;
inspect any printed fixture root and host ownership records before its next run.
A passing receipt covers deterministic host integration only.

A draft with uncommitted changes is not eligible for this exact-commit driver.
A coordinator's frozen HEAD-plus-patch probe is separate evidence and must record
both the base and patch hashes; it is not a final Git candidate. Native compilation
and runtime checks remain pending until executed by the owning coordinator.

## CI and coordinated candidates

The macOS source consumer reads the full Host commit from
`.github/computer-mcp-host.sha`. It checks out
that commit from the public Computer MCP repository alongside a separate plugin
checkout. The driver verifies both clean checkouts, uses the plugin checkout's
actual HEAD, and runs the deterministic fixture. The CI validation gate requires
the source consumer alongside both Linux package jobs.

The job uploads the driver receipt, case results and logs when available. The
pinned Host commit must be reachable from the public repository for CI to check
it out. For an unpublished commit, run the driver against the local Host source.
After the coordinated Host freeze or a squash merge changes its commit, update
the pin to the accepted Host SHA and rerun the consumer before integrating the
plugin. Release pins belong to the coordinated release point.

## Signed-App native acceptance

The owner performs these checks using the compatible signed App and a disposable,
explicitly authorized target:

1. Record host/plugin revisions, vendor executable identity/version and the
   actual signed caller/helper identities. Register the candidate source, bind
   the executable and explicitly review declarations, mode and exposure.
2. Verify sandboxed native discovery. Capture supported native catalog/help or
   protocol evidence before choosing exact per-tool requirements. Record each
   tool's observed effect and the vendor/caller combination; do not copy a
   machine's paths or catalog into portable guidance.
3. Check caller and provider Screen/Desktop refusal independently. Host grants
   do not supply system privacy authorization. Answer requests through the host
   and explicitly retry matching calls; approval never dispatches a call.
4. Follow vendor/system Screen Recording and Accessibility authorization flows
   as the user. Record the responsible identity and any supported user-performed
   restart. Do not modify TCC databases or impersonate another caller.
5. Observe the target, perform one harmless authorized action, then observe and
   verify its result. If an action's outcome is uncertain, observe or stop;
   never automatically replay it through AX.
6. Record vendor state, configuration reads, network, login and external writes
   without copying credentials into evidence. Confirm the minimum sandbox if
   sufficient; otherwise the owner chooses supported container login or a
   declared Full access request from those facts. Full access does not grant
   host Screen/Desktop permission, Full Disk Access or inherited App privacy
   responsibility. Discovery still has to meet its sandbox boundary.
7. Verify revocation and the matched-group host-worktree invocation/removal
   checks at the final candidate, including joined sandboxed writers.

Deterministic fixtures do not replace this evidence or the owner's mode choice.
