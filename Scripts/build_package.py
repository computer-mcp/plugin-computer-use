"""Build this declarative plugin from owned source without external dependencies."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tomllib
import zipfile


def package_bytes(root):
    paths = [root / name for name in (
        "README.md", "CONTRIBUTING.md", "computer-mcp-plugin.toml", "LICENSE",
        "THIRD_PARTY_NOTICES.md", "ThirdPartyNotices.txt")]
    pending = [root / "skills", root / "Documentation"]
    entries = 0
    while pending:
        path = pending.pop()
        entries += 1
        if entries > 512:
            raise ValueError("Package contains too many entries")
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            with os.scandir(path) as children:
                for child in children:
                    if len(pending) + entries >= 512:
                        raise ValueError("Package contains too many entries")
                    pending.append(Path(child.path))
        elif stat.S_ISREG(mode):
            paths.append(path)
        else:
            raise ValueError(f"Package source must not contain links or special files: {path}")

    contents = {}
    total = 0
    for path in sorted(paths):
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError(f"Package source must be a regular file: {path}")
        with path.open("rb") as source:
            data = source.read(1_048_577)
        total += len(data)
        if len(data) > 1_048_576 or total > 8_388_608:
            raise ValueError("Package source exceeds its size limit")
        contents[path.relative_to(root).as_posix()] = data

    declaration = tomllib.loads(contents["computer-mcp-plugin.toml"].decode("utf-8"))
    if declaration["id"] != "computer-use":
        raise ValueError("Unexpected plugin identity")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in contents.items():
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(entry, data)
    return output.getvalue(), declaration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    data, declaration = package_bytes(Path(__file__).resolve().parent.parent)
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / "computer-use.zip"
    if artifact.exists() or artifact.is_symlink():
        if (artifact.is_symlink() or not artifact.is_file()
                or artifact.stat().st_size != len(data) or artifact.read_bytes() != data):
            raise ValueError("Output already exists with different contents; use an empty directory")
    else:
        with artifact.open("xb") as destination:
            destination.write(data)
    print(json.dumps({"id": declaration["id"], "version": declaration["version"],
                      "archive": str(artifact), "sha256": hashlib.sha256(data).hexdigest()},
                     sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
