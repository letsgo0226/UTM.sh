#!/bin/sh
set -eu
D=${1:-};shift||true
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case "$D" in
 cosmic) exec sh "$ROOT/domains/cosmic-love-infinity-tm.sh" "$@";;
 trader) exec sh "$ROOT/domains/Trader_42.sh" "$@";;
 music) exec sh "$ROOT/domains/music-generator.sh" "$@";;
 ocr) exec sh "$ROOT/domains/ocr-tts.sh" "$@";;
 ocr2) exec sh "$ROOT/domains/OCR_2KB.sh" "$@";;
 tts2) exec sh "$ROOT/domains/TTS_2KB.sh" "$@";;
 *) echo 'usage: run-domain.sh {cosmic|trader|music|ocr|ocr2|tts2}' >&2;exit 2;;
esac
