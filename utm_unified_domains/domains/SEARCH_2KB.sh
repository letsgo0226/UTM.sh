#!/bin/sh
# SEARCH_2KB.sh — UTM-style web search controller
set -eu
Q=${QUERY:-${1:-}};[ -n "$Q" ]||{ echo "QUERY required" >&2;exit 2;}
S=${SITE:-youtube.com};L=${LIMIT:-8}
python3 - "$Q" "$S" "$L" <<'PY'
import sys,re,json,html,urllib.parse as P,urllib.request as U,hashlib
q,s,L=sys.argv[1],sys.argv[2],int(sys.argv[3])
A=[q,f'"{q}"','"Utrum intellectivum principium uniatur corpori ut forma" Latin pronunciation','"hic homo intelligit" Aquinas Latin','"quo primo intelligimus" Aquinas','"experitur enim unusquisque seipsum esse qui intelligit"','"Summa Theologiae" "q. 76" "a. 1" Latin','"Prima Pars" "Quaestio 76" Latin audio']
R=[];Q=[]
for st,x in enumerate(A):
 if x in Q:continue
 Q.append(x);z="site:"+s+" "+x;u="https://html.duckduckgo.com/html/?q="+P.quote(z)
 try:t=U.urlopen(U.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=12).read().decode("utf8","ignore")
 except Exception as e:print(json.dumps({"state":st,"query":z,"error":str(e)},ensure_ascii=False),file=sys.stderr);continue
 for m in re.finditer(r'href="([^"]+)"',t):
  v=html.unescape(m.group(1))
  if "uddg=" in v:v=P.parse_qs(P.urlparse(v).query).get("uddg",[v])[0]
  if s not in v or any(a["url"]==v for a in R):continue
  T=[a.lower() for a in re.findall(r"[A-Za-z]+",x) if len(a)>3]
  R.append({"state":st,"score":sum(a in v.lower() for a in T),"query":x,"url":v})
 if len(R)>=L:break
R=sorted(R,key=lambda a:(-a["score"],a["state"]))[:L]
g=int.from_bytes(hashlib.sha256("\n".join(Q).encode()).digest(),"big")
print(json.dumps({"goal":"q.76 a.1 Latin pronunciation/audio","halt":bool(R),"queries":Q,"results":R,"GPROGRAM":str(g)},ensure_ascii=False,indent=2))
PY
