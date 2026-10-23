<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/assets/logo/logo-dark.png">
    <img src=".github/assets/logo/logo-light.png" width="128" height="128" alt="">
  </picture>
</p>

<h1 align="center">Computer Use</h1>

<p align="center">Computer MCP family plugin for native desktop observation and actions.</p>

<p align="center">
  <a href="https://github.com/computer-mcp/plugin-computer-use/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/computer-mcp/plugin-computer-use/ci.yml?branch=master&label=CI&style=flat"></a>
  <a href=".github/workflows/ci.yml"><img alt="Python 3.11 or newer to build" src="https://img.shields.io/badge/build-Python%203.11%2B-blue?style=flat"></a>
  <a href="computer-mcp-plugin.toml"><img alt="Platform: macOS" src="https://img.shields.io/badge/platform-macOS-lightgrey?style=flat"></a>
  <a href="LICENSE"><img alt="License: FSL-1.1-ALv2" src="https://img.shields.io/badge/license-FSL--1.1--ALv2-blue?style=flat"></a>
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="skills/observe-act-verify/SKILL.md">Skill</a> ·
  <a href="docs/README.md">Documentation</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

## Overview

A declarative [Computer MCP](https://computer-mcp.github.io/) package that connects the host to
the vendor's native Computer Use MCP server and adds guidance for verifying every observation and
action. It contains no proxy, vendor executable, installer or running skill service. The vendor
owns installation, updates and caller compatibility.

## Quick look

The plugin contributes:

| Contribution | What it adds |
| --- | --- |
| `native` MCP server | The vendor client's own tools, started as `SkyComputerUseClient mcp` and exposed under the `computer-use` prefix |
| `observe-act-verify` skill | How to complete an authorized GUI task from current observations, scoped actions and post-action checks, and how to recover from stale references or uncertain results |

Install the archive in the host, review the `native` contribution, choose which tools to expose,
and enable it.

## Install

1. Build the archive: `scripts/build-package.sh OUTPUT_DIRECTORY` writes `computer-use.zip`.
2. Install it through the host's Plugins page or management CLI with its declared ID and
   version and the SHA-256 the build prints. A local development registration can point at this
   checkout instead.
3. The host starts new plugins disabled. Review the `native` MCP contribution, choose its tool
   whitelist or all-tools exposure explicitly, and keep the appropriate caller and profile
   permissions. Enabling the package does not override those permissions.

The host finds the client on its search path, then by the installed application's bundle
identifier, `com.openai.sky.CUAService`. When neither finds it, bind the actual executable in the
plugin's dependency settings; an explicit binding takes precedence.

Host state lives outside this package. Uninstalling a version does not delete the vendor client,
this development checkout or saved host grants.

## Usage

A successful MCP handshake or tools listing does not prove that observation or actions work.
Before relying on the plugin, choose a disposable, authorized target: read its state, perform one
harmless action, then read and verify the result. Diagnose permission or caller-trust failures
through the vendor's and the system's supported flows.

Native accessibility (AX) remains available for diagnostics and fallback where appropriate. An
uncertain write is observed before any further action; it is never replayed automatically
through AX.

## Requirements

- A Computer MCP host with plugin support, on macOS.
- A vendor-supported Computer Use client that provides its `mcp` entry point.
- Python 3.11 or newer (standard library only) to build the archive.

## Documentation

The archive contains this manual, the contributor and architecture documentation, the license
and third-party notices, the manifest and the skill directory; it excludes Git metadata, local
test evidence and external executables, and the same inputs produce the same bytes. The
[documentation index](docs/README.md) covers the package architecture and the
[release process](docs/Reference/Release.md).

CI runs the package tests and keeps the archive and its SHA-256 receipt on pull requests, `master`
pushes and manual runs, and repeats the tests and build on Python 3.11. It runs without macOS and
never starts the vendor client, so its artifacts are neither a public plugin release nor proof of
GUI compatibility. Local ownership or a bundled source label is not a verified GitHub publisher or
artifact signature.

## Contributing

See the [contributor guide](CONTRIBUTING.md).

## License

Computer MCP-owned code and resources use the
[Functional Source License 1.1, Apache 2.0 Future License](LICENSE) (FSL-1.1-ALv2). See the
[third-party notices](THIRD_PARTY_NOTICES.md) for the vendor client's separate ownership and
terms.
