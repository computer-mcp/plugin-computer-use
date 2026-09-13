# Computer Use package

## Scope and structure

The manifest contributes the native Computer Use MCP entry and a portable
observe–act–verify skill. The vendor owns the executable and caller compatibility;
the host owns registration, workspace/profile grants and dependency bindings.
Skills are guidance resources and do not run during installation or reading.

The dependency declares a command name and an application bundle locator. The
host uses its explicit binding first, then PATH, then macOS application lookup;
the selected executable remains vendor-owned. The bundle identifier and contained
helper path describe the vendor layout, not a machine-specific installation
directory. Discovery does not establish signing identity or GUI caller trust.

## Distribution and safety

The package builder validates regular files and bounded input, rejects links and
special files, and emits deterministic ZIP bytes. The shipped contents are the
manifest, manuals, license and notices, architecture documentation and skill tree. Agent execution
state and source-level test helpers stay with the checkout.

The MCP connection goes directly to the vendor. Native AX remains a diagnostic
and fallback facility; uncertain actions require observation before another
write. A handshake or tool catalog proves neither GUI access nor successful
observation/action/verification.

The builder uses Python's standard library. Vendor installation, upgrades,
permissions and credentials remain external to this package.

The repository validation workflow verifies package boundaries and reproducible
bytes on a non-GUI runner, retaining a ZIP and digest receipt with read-only
repository permissions. GUI acceptance and authorized publication have separate
evidence and approval requirements; neither follows from a successful package job.
