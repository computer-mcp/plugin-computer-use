# Computer Use Plugin

A declarative Computer MCP package that connects to the vendor's native
Computer Use MCP server and supplies observation/action verification guidance.
It contains no proxy, vendor executable, installer or running skill service.

## Requirements

Use a Computer MCP host with plugin support and a vendor-supported Computer Use
client. The client must provide its `mcp` entry point. The host checks its search
path, then locates the declared installed application by bundle identifier.
Supply the actual executable through the host's dependency binding when the
vendor installation is not discoverable by either method. An explicit binding
takes precedence. The vendor owns installation, updates and caller compatibility.

The host starts new plugins disabled. Review the `native` MCP contribution,
explicitly choose its tool whitelist or all-tools exposure, and retain the
appropriate caller/profile permissions. Enabling the package does not override
those permissions. A successful MCP handshake or tools listing does not prove
that observation or actions work.

For first-use verification, choose a disposable, authorized target: read its
state, perform one harmless action, then read and verify the result. Diagnose
permission or caller-trust failures through supported vendor/system flows.
Native AX remains available for diagnostics and appropriate fallback. An
uncertain write must be observed before any further action, never automatically
replayed through AX.

## Package

Run `Scripts/build-package.sh OUTPUT_DIRECTORY` to produce `computer-use.zip`.
The archive contains this manual, contributor and architecture documentation,
the license and third-party notices, the manifest and the skill directory. Build
output excludes Git metadata, local test evidence and external executables.
The build requires Python 3.11 or later's standard library; it installs nothing and
produces deterministic archive bytes from the same inputs.

`.github/workflows/validate.yml` runs the package tests and retains the ZIP and
SHA-256 receipt on pull requests, pushes and manual runs. This declaration-only
job runs independently of macOS and never starts the vendor client. Its workflow
artifacts are not a public plugin release or proof of GUI compatibility.

Install the archive through the host's Plugins page or management CLI using its
declared ID/version and the SHA-256 emitted by the build. A local development
registration can point at this checkout instead. Local ownership or a bundled
source label is not a verified GitHub publisher or artifact signature.

Host state belongs outside this package. Uninstalling an installed version must
not delete the vendor client, this development checkout, or saved host grants.

The [repository documentation](Documentation/README.md) describes the package
architecture; the [contributor guide](CONTRIBUTING.md) covers validation.

## License

Computer MCP-owned code and resources use the
[Computer MCP Source-Visible License 1.0](LICENSE). Source visibility is not an
open-source license. See [third-party notices](THIRD_PARTY_NOTICES.md) for the
external vendor client's separate ownership and terms.
