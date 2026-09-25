#!/bin/sh
command -v python3>/dev/null||exit 127
[ $# -gt 0 ]||{ echo 'usage: source-godel.sh FILE...' >&2;exit 2; }
python3 -S - "$@" <<'PY'
import sys,json
sys.set_int_max_str_digits(0)
def enc(b):
 g=1
 for x in b:g=g*257+x+1
 return g
for p in sys.argv[1:]:
 b=open(p,'rb').read();g=enc(b);print(json.dumps({'file':p,'bytes':len(b),'GDOMAIN':str(g),'bits':g.bit_length()},separators=(',',':')))
PY
