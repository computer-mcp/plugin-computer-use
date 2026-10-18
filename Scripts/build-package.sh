#!/bin/sh
set -eu
plugin_directory=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$plugin_directory/Scripts/build_package.py" "$@"
