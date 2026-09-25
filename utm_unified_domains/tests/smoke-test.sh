#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for f in "$ROOT"/utm/*.sh "$ROOT"/domains/*.sh "$ROOT"/tools/*.sh;do sh -n "$f";done
echo '[1/4] shell syntax: OK'
# UTM compiler+kernel
ENVF=$(mktemp);sh "$ROOT/utm/TMCC.sh" "$ROOT/examples/domain-control.tm">"$ENVF";. "$ENVF";rm -f "$ENVF"
S=$(mktemp);rm -f "$S";GPROGRAM="$GPROGRAM" INPUT=EVPC CMD=run TM_STATE="$S" sh "$ROOT/utm/UTM.sh">/tmp/utm_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/utm_smoke.out'));assert x['halt'] and x['tape']=='EVPC';print('[2/4] UTM control program: OK')
PY
rm -f "$S" /tmp/utm_smoke.out
# Trader one step in isolated state
S=$(mktemp);rm -f "$S";LOG_TM_STATE="$S" N=1 CMD=step sh "$ROOT/domains/Trader_42.sh">/tmp/trader_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/trader_smoke.out'));assert x['CG'] and x['C'];print('[3/4] Trader_42 core: OK')
PY
rm -f "$S" /tmp/trader_smoke.out
# Music tiny render
D=$(mktemp -d);(cd "$D";printf 'test\n0.5\n'|sh "$ROOT/domains/music-generator.sh">out;test -s music_*.wav)
rm -rf "$D";echo '[4/4] Music WAV render: OK'
echo 'OCR/TTS: syntax checked; runtime dependencies are tesseract + espeak-ng or espeak (+ pdftoppm for PDF).'
echo 'Cosmic: syntax checked only because the restored legacy file self-reexecutes and rewrites itself by design.'
