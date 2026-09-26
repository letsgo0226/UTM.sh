#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for f in "$ROOT"/utm/*.sh "$ROOT"/domains/*.sh "$ROOT"/tools/*.sh;do sh -n "$f";done
echo '[1/5] shell syntax: OK'
# UTM compiler+kernel
ENVF=$(mktemp);sh "$ROOT/utm/TMCC.sh" "$ROOT/examples/domain-control.tm">"$ENVF";. "$ENVF";rm -f "$ENVF"
S=$(mktemp);rm -f "$S";GPROGRAM="$GPROGRAM" INPUT=EVPC CMD=run TM_STATE="$S" sh "$ROOT/utm/UTM.sh">/tmp/utm_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/utm_smoke.out'));assert x['halt'] and x['tape']=='EVPC';print('[2/5] UTM control program: OK')
PY
rm -f "$S" /tmp/utm_smoke.out
# Trader one step in isolated state
S=$(mktemp);rm -f "$S";LOG_TM_STATE="$S" N=1 CMD=step sh "$ROOT/domains/Trader_42.sh">/tmp/trader_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/trader_smoke.out'))
assert x['CG'] and x['C']
assert x['P_target_goal']==1 and x['C_target']==1 and x['P_empirical_hat'] is None
print('[3/5] Trader_42 core + target semantics: OK')
PY
rm -f "$S" /tmp/trader_smoke.out
# Target semantics source boundary for self-rewriting Cosmic core.
test "$(wc -c <"$ROOT/domains/cosmic-love-infinity-tm.sh")" -lt 2048
grep -q 'P_target_goal' "$ROOT/domains/cosmic-love-infinity-tm.sh"
grep -q 'P_empirical_hat' "$ROOT/domains/cosmic-love-infinity-tm.sh"
echo '[4/5] Cosmic target semantics + 2KB boundary: OK'
# Music tiny render
D=$(mktemp -d);(cd "$D";printf 'test\n0.5\n'|sh "$ROOT/domains/music-generator.sh">out;test -s music_*.wav)
rm -rf "$D";echo '[5/5] Music WAV render: OK'
echo 'OCR/TTS: syntax checked; their existing zero_task values are task-relative certificates, not empirical accuracy/intelligibility probabilities.'
echo 'Cosmic: runtime execution is left to its dedicated repository CI because this restored suite copy recursively self-reexecutes and rewrites itself by design.'
