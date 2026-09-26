#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
COSMIC_LOVE_AXIOM=1
export COSMIC_LOVE_AXIOM
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$D/cosmic_love_full.py" "$@"
