# Contributing

Changes belong to the artifact that owns their behavior. Describe the observable
change and include focused regression evidence. Preserve user configuration,
external dependencies and credentials.

## Validation

CI runs `python3 -m unittest discover -s tests -p 'test_*.py'` and `python3 scripts/build_package.py OUTPUT_DIRECTORY` on Python 3.13 and 3.11; run both before opening a pull request. Build an archive with `scripts/build-package.sh OUTPUT_DIRECTORY` and inspect its file list. GUI checks use disposable, explicitly authorized targets.

Deterministic source admission checks use the explicit host/plugin revisions and
external output directory described in [Host integration](docs/Reference/HostIntegration.md).
Keep their evidence outside this repository. Native GUI acceptance is separate;
a fixture success does not establish vendor permissions or mode compatibility.

## Documentation

The [documentation index](docs/README.md) links current architecture
and reference material. Agent work routes live in AGENTS.md; public usage lives
in the root README. GitHub collaboration files belong in .github/ and contributor
policy belongs in root governance files.

Contributions are licensed under this repository's [LICENSE](LICENSE),
FSL-1.1-ALv2.
