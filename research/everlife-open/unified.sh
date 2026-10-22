#!/bin/sh
set -eu
exec python3 "$(dirname "$0")/unified_machine.py" "$@"
