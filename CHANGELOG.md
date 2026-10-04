# Changelog

All notable user-visible changes to the Computer Use plugin are documented here.

## Unreleased

- Declare Computer MCP 1.1.0, the first host that reads plugin manifests, as the
  minimum host.

## 1.0.0 — 2026-09-13

- First release: a declaration-only plugin that registers the vendor's installed
  Computer Use MCP client directly, with dependency discovery and
  observe–act–verify Skills. No proxy, vendor binary or installer is included.
- Bundled and separately installed copies use the same manifest and host
  authorization; installation grants no system or tool permissions.
