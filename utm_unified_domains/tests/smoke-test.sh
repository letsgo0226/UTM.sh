#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for f in "$ROOT"/utm/*.sh "$ROOT"/domains/*.sh "$ROOT"/domains/compact/*.sh "$ROOT"/tools/*.sh;do sh -n "$f";done
for f in Trader_42.sh cosmic-love-infinity-tm.sh OCR_2KB.sh music-generator.sh;do test "$(wc -c <"$ROOT/domains/$f")" -lt 2048;done
for f in "$ROOT"/domains/compact/*.sh;do test "$(wc -c <"$f")" -lt 2048;done
echo '[1/7] shell syntax + packed <2KB boundaries: OK'
ENVF=$(mktemp);sh "$ROOT/utm/TMCC.sh" "$ROOT/examples/domain-control.tm">"$ENVF";. "$ENVF";rm -f "$ENVF"
S=$(mktemp);rm -f "$S";GPROGRAM="$GPROGRAM" INPUT=EVPC CMD=run TM_STATE="$S" sh "$ROOT/utm/UTM.sh">/tmp/utm_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/utm_smoke.out'));assert x['halt'] and x['tape']=='EVPC';print('[2/7] UTM control program: OK')
PY
rm -f "$S" /tmp/utm_smoke.out
D=$(mktemp -d)
TRADER42_TEST_PRICES='100,101,102,103,104,105,106,107,108,109,108,107,106,105,104,103,102,101,100,99,100,101,102,103,104,105' FAST_WINDOW=3 SLOW_WINDOW=5 OOS_TRAIN_CANDLES=10 OOS_TEST_CANDLES=5 OOS_MIN_FOLDS=2 CANDLE_DATASET_PATH="$D/c.csv" sh "$ROOT/domains/Trader_42.sh">/tmp/trader_smoke.out
python3 - <<'PY'
import json
x=json.load(open('/tmp/trader_smoke.out'));assert x['model']=='TRADER_42_UNIFIED_RESEARCH_V1' and x['mode']=='research-paper-only';assert x['CG'] and x['A_target']==1 and x['G_target']==1;assert x['temporal_formula']=='G(PROFIT_IS_OBJECTIVE)' and x['observations']>0 and 'metrics' in x and 'oos' in x;print('[3/7] Trader packed research/OOS/accounting runtime: OK')
PY
rm -rf "$D" /tmp/trader_smoke.out
D=$(mktemp -d)
S="$D/state.json" CMD=step N=3 sh "$ROOT/domains/cosmic-love-infinity-tm.sh">/tmp/cosmic_step.out
S="$D/state.json" CMD=rewind N=2 sh "$ROOT/domains/cosmic-love-infinity-tm.sh">/tmp/cosmic_rewind.out
python3 - <<'PY'
import json
for p in ('/tmp/cosmic_step.out','/tmp/cosmic_rewind.out'):
 x=json.load(open(p));assert x['CF'] and x['CG'] and x['CL']==1 and x['ICL'] and x['RCL'] and x['GCL'];assert x['A_CL']==1 and x['G_CL']==1 and x['P_empirical_hat'] is None
print('[4/7] Cosmic packed reversible + G(CL) runtime: OK')
PY
rm -rf "$D" /tmp/cosmic_step.out /tmp/cosmic_rewind.out
D=$(mktemp -d);B="$D/bin";mkdir "$B";cat >"$B/file" <<'SH'
#!/bin/sh
echo image/png
SH
cat >"$B/tesseract" <<'SH'
#!/bin/sh
if [ "$1" = --list-langs ];then printf 'List of available languages (1):\neng\n';exit 0;fi
printf 'hello world\n' > "$2.txt"
SH
chmod +x "$B/file" "$B/tesseract";touch "$D/img.png"
(cd "$D";PATH="$B:$PATH" INPUT=img.png OCR_LANG=eng sh "$ROOT/domains/OCR_2KB.sh">/tmp/ocr_smoke.out)
python3 - <<'PY'
import json
x=json.load(open('/tmp/ocr_smoke.out'));assert x['pages']==1 and x['zero_task'] and x['C_target']==1 and x['P_empirical_hat'] is None;print('[5/7] OCR packed consensus/certificate runtime: OK')
PY
rm -rf "$D" /tmp/ocr_smoke.out
D=$(mktemp -d);(cd "$D";KEYWORD=test SEC=.5 VOCAL=0 OUT=instrumental.wav sh "$ROOT/domains/music-generator.sh">/tmp/music_i.out;test -s instrumental.wav);grep -q 'VOCAL=0' /tmp/music_i.out;rm -rf "$D" /tmp/music_i.out;echo '[6/7] Music packed instrumental runtime: OK'
D=$(mktemp -d);(cd "$D";KEYWORD=test LYRICS='cosmic love is all' SEC=.5 VOCAL=1 CANDIDATES=64 VM_STEPS=1000 OUT=vocal.wav sh "$ROOT/domains/music-generator.sh">/tmp/music_v.out;test -s vocal.wav);grep -q 'UTM=BF8' /tmp/music_v.out;grep -q 'VOCAL=1' /tmp/music_v.out;grep -q 'BOUNDED=1' /tmp/music_v.out;grep -q 'ENUM_COMPLETE=0' /tmp/music_v.out;grep -q 'C_target=1' /tmp/music_v.out;rm -rf "$D" /tmp/music_v.out;echo '[7/7] Universal bounded music + lyric-conditioned vocal runtime: OK'
echo 'OCR zero_task is a task-relative consensus certificate, not ground-truth accuracy.'
echo 'Music uses an open-ended BF8 universal program language, but each run searches only a finite bounded prefix and does not guarantee natural/intelligible singing.'
echo 'Trader remains offline research/paper-only; Cosmic G(CL) remains a model-internal invariant.'
