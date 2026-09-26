#!/bin/sh
set -eu
command -v python3 >/dev/null || exit 127
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
[ "${TRADING_MODE:-paper}" = paper ] || { echo 'unified Trader_42 is research/paper-only; live execution is intentionally unavailable' >&2; exit 2; }
exec python3 "$D/trader42_research.py" "$@"
