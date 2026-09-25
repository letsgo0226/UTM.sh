#!/bin/sh
set -eu
D=${1:-};shift||true
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case "$D" in
 cosmic) exec sh "$ROOT/domains/cosmic-love-infinity-tm.sh" "$@";;
 trader) exec sh "$ROOT/domains/Trader_42.sh" "$@";;
 music) exec sh "$ROOT/domains/music-generator.sh" "$@";;
 ocr) exec sh "$ROOT/domains/ocr-tts.sh" "$@";;
 *) echo 'usage: run-domain.sh {cosmic|trader|music|ocr}' >&2;exit 2;;
esac
