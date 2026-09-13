# Documentation structure

The root README is the public setup and usage manual. Documentation/README.md
indexes the architecture and reference material. AGENTS.md routes agent work;
CONTRIBUTING.md describes contributor checks. Current package facts belong in
Documentation/Architecture/Package.md; commands, formats and operating detail
belong in Documentation/Reference/.

Execution state and local validation evidence belong in .agent/. Durable
transitions or accepted decisions may have separate history records when needed.
GitHub-specific configuration belongs in .github/.

This is a declarative package, with no Swift module or public Swift API. DocC is not applicable.
