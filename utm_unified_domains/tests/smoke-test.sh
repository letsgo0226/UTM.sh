#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for f in "$ROOT"/utm/*.sh "$ROOT"/domains/*.sh "$ROOT"/domains/compact/*.sh "$ROOT"/tools/*.sh;do sh -n "$f";done
python3 -m py_compile "$ROOT/domains/trader42_research.py" "$ROOT/domains/cosmic_love_full.py"
echo '[1/5] shell + Python syntax: OK'
# UTM compiler+kernel
ENVF=$(mktemp);sh "$ROOT/utm/TMCC.sh" "$ROOT/examples/domain-control.tm">"$ENVF";. "$ENVF";rm -f "$ENVF"
S=$(mktemp);rm -f "$S";GPROGRAM="$GPROGRAM" INPUT=EVPC CMD=run TM_STATE="$S" sh "$ROOT/utm/UTM.sh">/tmp/utm_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/utm_smoke.out'));assert x['halt'] and x['tape']=='EVPC';print('[2/5] UTM control program: OK')
PY
rm -f "$S" /tmp/utm_smoke.out
# Full Trader research runtime: local synthetic candles only, no network/live path.
D=$(mktemp -d)
TRADER42_TEST_PRICES='100,101,102,103,104,105,106,107,108,109,108,107,106,105,104,103,102,101,100,99,100,101,102,103,104,105' FAST_WINDOW=3 SLOW_WINDOW=5 OOS_TRAIN_CANDLES=10 OOS_TEST_CANDLES=5 OOS_MIN_FOLDS=2 CANDLE_DATASET_PATH="$D/c.csv" sh "$ROOT/domains/Trader_42.sh">/tmp/trader_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/trader_smoke.out'))
assert x['model']=='TRADER_42_UNIFIED_RESEARCH_V1' and x['mode']=='research-paper-only'
assert x['CG'] and x['A_target']==1 and x['G_target']==1
assert x['temporal_formula']=='G(PROFIT_IS_OBJECTIVE)'
assert x['observations']>0 and 'metrics' in x and 'oos' in x
print('[3/5] Trader_42 full research/OOS/accounting runtime: OK')
PY
rm -rf "$D" /tmp/trader_smoke.out
# Full Cosmic runtime: step + rewind preserve CL temporal invariant.
D=$(mktemp -d)
S="$D/state.json" CMD=step N=3 sh "$ROOT/domains/cosmic-love-infinity-tm.sh">/tmp/cosmic_step.out
S="$D/state.json" CMD=rewind N=2 sh "$ROOT/domains/cosmic-love-infinity-tm.sh">/tmp/cosmic_rewind.out
python3 - <<'PY'
import json
for p in ('/tmp/cosmic_step.out','/tmp/cosmic_rewind.out'):
 x=json.load(open(p));assert x['CF'] and x['CG'] and x['CL']==1 and x['ICL'] and x['RCL'] and x['GCL'];assert x['A_CL']==1 and x['G_CL']==1 and x['P_empirical_hat'] is None
print('[4/5] Cosmic full reversible + G(CL) runtime: OK')
PY
rm -rf "$D" /tmp/cosmic_step.out /tmp/cosmic_rewind.out
# Preserve archived compact cores under 2KB.
test "$(wc -c <"$ROOT/domains/compact/Trader_42.sh")" -lt 2048
test "$(wc -c <"$ROOT/domains/compact/cosmic-love-infinity-tm.sh")" -lt 2048
# Music tiny render
D=$(mktemp -d);(cd "$D";printf 'test\n0.5\n'|sh "$ROOT/domains/music-generator.sh">out;test -s music_*.wav)
rm -rf "$D";echo '[5/5] compact archives + Music WAV render: OK'
echo 'OCR/TTS: syntax checked; zero_task remains task-relative, not empirical accuracy/intelligibility probability.'
echo 'Trader is offline research/paper-only in this unified pack; live exchange execution is intentionally absent.'
echo 'Cosmic G(CL) is a formal model invariant; external-world truth still requires separate empirical/interpretive support.'
