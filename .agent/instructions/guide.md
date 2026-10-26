---
description: Keep the Computer Use plugin declarative, its skill portable, and its GUI verification on disposable targets.
---
# plugin-computer-use Agent Guide

## Plugin Boundaries

- Keep this a declarative plugin that connects directly to the vendor's native
  MCP implementation; package-owned guidance is not a proxy or runtime.
- Keep `skills/observe-act-verify/SKILL.md` portable and independent of a
  particular user's paths, targets, credentials or tool catalog snapshot.
- Preserve the native AX fallback and never replay an uncertain write through
  a second backend. Real GUI verification requires a disposable, authorized
  target.

## Validation

- Build the package with `scripts/build-package.sh OUTPUT_DIRECTORY`, then
  inspect it with the host's package validation and installation tests. Keep
  test evidence outside the repository.
