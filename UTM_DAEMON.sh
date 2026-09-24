#!/usr/bin/env bash
# UTM.sh resident loop — default 1s (step + periodic replay-reconstruct)
# UTM.sh has no CMD=reconstruct; every RECON_EVERY cycles the daemon replays the
# resident trace from reset via the GPROGRAM (Goedel-number) decode path and checks
# q/h/t/tape equality (CF) plus a full CMD=run certificate.
# KILL switch: touch "$WORKDIR/KILL" (or set UTM_KILL=1) to stop the loop.
set -u
INTERVAL="${1:-${UTM_INTERVAL:-1}}"
LOG="${UTM_LOG:-UTM_daemon.log}"
DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd || pwd)"
SCRIPT="${UTM_SCRIPT:-$DIR/UTM.sh}"
RAW_URL="https://raw.githubusercontent.com/letsgo0226/UTM.sh/main/UTM.sh"
WORKDIR="${UTM_WORKDIR:-$DIR/run}"
RECON_EVERY="${UTM_RECON_EVERY:-3}"
# Demo machine: binary increment (1011 -> 1100 in 8 transitions, halts in state 2)
PROG='0,0,0,0,R;0,1,0,1,R;0,_,1,_,L;1,1,1,0,L;1,0,2,1,L;1,_,2,1,L'
INPUT='1011'
GP='18284878286518279513985250418655129376649753247703229330837858803422355442844616233826387890720893742448012298419318058456087779774715707084658'
export UTM_GP="$GP"
mkdir -p "$WORKDIR"
if [[ ! -f "$SCRIPT" ]]; then
  command -v curl >/dev/null || exit 127
  SCRIPT="${TMPDIR:-/tmp}/UTM.sh"
  curl -fsSL "$RAW_URL" -o "$SCRIPT" || exit 1
fi
command -v python3 >/dev/null || exit 127
utm() { (cd "$WORKDIR" && env "$@" bash "$SCRIPT"); }
echo "{\"daemon\":\"UTM\",\"interval\":$INTERVAL,\"recon_every\":$RECON_EVERY,\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" | tee -a "$LOG"
utm TM_STATE=utm.json PROGRAM="$PROG" INPUT="$INPUT" CMD=reset >/dev/null 2>&1 || { echo "{\"status\":\"run_fail\",\"mode\":\"reset\"}" >>"$LOG"; exit 1; }
CYCLE=0
EPISODE=0
while true; do
  if [[ -e "$WORKDIR/KILL" || "${UTM_KILL:-0}" == "1" ]]; then
    echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"status\":\"killed\"}" >>"$LOG"; exit 0
  fi
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  OUT=$(mktemp)
  CYCLE=$((CYCLE+1))
  if utm TM_STATE=utm.json PROGRAM="$PROG" CMD=step >"$OUT" 2>"${OUT}.err"; then
    if SNAP=$(python3 - "$OUT" <<'PY'
import json,os,sys
o=json.load(open(sys.argv[1]))
T={0:("0",0,"1011"),1:("0",1,"1011"),2:("0",2,"1011"),3:("0",3,"1011"),4:("0",4,"1011"),
   5:("1",3,"1011"),6:("1",2,"1010"),7:("1",1,"1000"),8:("2",0,"1100")}
t=o.get("t")
ok=(isinstance(t,int) and t in T
    and (o.get("q"),o.get("h"),o.get("tape"))==T[t]
    and isinstance(o.get("halt"),bool)
    and (not o["halt"] or (t==8 and o["q"]=="2" and o["tape"]=="1100"))
    and o.get("GPROGRAM")==os.environ["UTM_GP"])
if not ok: sys.exit(2)
print(json.dumps({"q":o["q"],"h":o["h"],"t":t,"halt":o["halt"],"tape":o["tape"],"C":True,"open":1},separators=(",",":")))
PY
)
    then
      echo "{\"ts\":\"$TS\",\"status\":\"pass\",\"mode\":\"step\",\"episode\":$EPISODE} $SNAP" >>"$LOG"
      if (( CYCLE % RECON_EVERY == 0 )); then
        RDIR=$(mktemp -d)
        CUR_T=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["t"])' "$OUT")
        (cd "$RDIR" && TM_STATE=r.json GPROGRAM="$GP" INPUT="$INPUT" CMD=reset bash "$SCRIPT" >r.out \
          && for ((i=0;i<CUR_T;i++)); do TM_STATE=r.json GPROGRAM="$GP" CMD=step bash "$SCRIPT" >r.out || exit 1; done \
          && TM_STATE=x.json GPROGRAM="$GP" INPUT="$INPUT" CMD=reset bash "$SCRIPT" >/dev/null \
          && TM_STATE=x.json GPROGRAM="$GP" CMD=run bash "$SCRIPT" >x.out) 2>/dev/null
        RC=$?
        if (( RC == 0 )) && RSNAP=$(python3 - "$OUT" "$RDIR/r.out" "$RDIR/x.out" <<'PY'
import json,os,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); x=json.load(open(sys.argv[3]))
K=("q","h","t","tape")
CF=[a[k] for k in K]==[b[k] for k in K] and b["GPROGRAM"]==os.environ["UTM_GP"]
CR=(x["q"],x["h"],x["t"],x["halt"],x["tape"])==("2",0,8,True,"1100") and x["GPROGRAM"]==os.environ["UTM_GP"]
if not (CF and CR): sys.exit(2)
print(json.dumps({"t":a["t"],"CF":CF,"CR":CR,"C":True,"open":1},separators=(",",":")))
PY
)
        then echo "{\"ts\":\"$TS\",\"status\":\"pass\",\"mode\":\"reconstruct\"} $RSNAP" >>"$LOG"
        else echo "{\"ts\":\"$TS\",\"status\":\"assert_fail\",\"mode\":\"reconstruct\",\"rc\":$RC}" >>"$LOG"
        fi
        rm -rf "$RDIR"
      fi
      if grep -q '"halt":true' "$OUT"; then
        EPISODE=$((EPISODE+1))
        utm TM_STATE=utm.json PROGRAM="$PROG" INPUT="$INPUT" CMD=reset >/dev/null 2>&1 \
          || echo "{\"ts\":\"$TS\",\"status\":\"run_fail\",\"mode\":\"reset\"}" >>"$LOG"
      fi
    else echo "{\"ts\":\"$TS\",\"status\":\"assert_fail\",\"mode\":\"step\"}" >>"$LOG"
    fi
  else echo "{\"ts\":\"$TS\",\"status\":\"run_fail\",\"mode\":\"step\"}" >>"$LOG"
  fi
  rm -f "$OUT" "${OUT}.err"
  sleep "$INTERVAL"
done
