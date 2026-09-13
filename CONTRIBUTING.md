# Contributing

Changes belong to the artifact that owns their behavior. Describe the observable
change and include focused regression evidence. Preserve user configuration,
external dependencies and credentials.

## Validation

Run `python3 -m unittest discover -s Tests` with Python 3.11 or newer. Build an archive with `Scripts/build-package.sh OUTPUT_DIRECTORY` and inspect its file list. GUI checks use disposable, explicitly authorized targets.

## Documentation

The [documentation index](Documentation/README.md) links current architecture
and reference material. Agent work routes live in AGENTS.md; public usage lives
in the root README. GitHub collaboration files belong in .github/ and contributor
policy belongs in root governance files. Execution notes belong in .agent/.
