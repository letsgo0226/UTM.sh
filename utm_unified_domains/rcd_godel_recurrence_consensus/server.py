import json,os,urllib.request,functools,sys
from http.server import BaseHTTPRequestHandler,HTTPServer
hasattr(sys,"set_int_max_str_digits") and sys.set_int_max_str_digits(0)
PEERS=[x.rstrip("/") for x in os.getenv("RCD_RECURRENCE_PEERS","").split(",") if x.strip()]
J=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
E=lambda s:functools.reduce(lambda n,b:n*257+b+1,s.encode(),1)

def call(url,data):
    b=J(data).encode();r=urllib.request.Request(url+"/run",data=b,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(r,timeout=20) as x:return json.loads(x.read())

def valid_parent(p):
    if not isinstance(p,dict) or p.get("protocol")!="RCD-Godel-Recurrence-Consensus/1.0" or not p.get("unanimous"):return False
    try:
        core={k:v for k,v in p.items() if k not in ("consensus_godel","atgc","gc")}
        return E(J(core))==int(p.get("consensus_godel"))
    except:return False

def step(parent,inp):
    if len(PEERS)!=3:raise RuntimeError("need-exactly-3-peers")
    if parent is None: layer,pg=0,0
    else:
        if not valid_parent(parent):raise ValueError("invalid-parent-certificate")
        layer=int(parent["layer"])+1;pg=int(parent["consensus_godel"])
    d=dict(inp or {});d["layer"]=layer;d["parent_godel"]=pg
    rs=[call(p,d) for p in PEERS];ok=len({J(x) for x in rs})==1
    core={"protocol":"RCD-Godel-Recurrence-Consensus/1.0","layer":layer,"parent_consensus_godel":pg,"unanimous":ok,"peer_count":3,"peer_godels":[x.get("godel") for x in rs],"claims":{"global_halting_decider":0,"global_arithmetic_complete":0,"resolves_boundary":0}}
    if ok:
        x=rs[0];core["shared"]={"godel":x.get("godel"),"gc":x.get("gc"),"boundary":x.get("state",{}).get("boundary"),"lift_required":x.get("lift_required"),"parent_godel":x.get("state",{}).get("parent_godel")}
    g=E(J(core));q=g;a="";A="ATGC"
    while q:a=A[q%4]+a;q//=4
    return {**core,"consensus_godel":g,"atgc":a or "A","gc":sum(c in "GC" for c in(a or "A"))}

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=J(o).encode();self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):return self.sendj(200,{"ok":True,"protocol":"RCD-Godel-Recurrence-Consensus/1.0","peers":len(PEERS),"claims":{"global_halting_decider":0,"global_arithmetic_complete":0,"resolves_boundary":0}})
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path=="/selftest":
                a={"limit":8,"machines":[{"rules":"0,A,H,A,S","input":"A"},{"rules":"0,A,0,A,R;0,_,0,_,R","input":"A"}],"sentences":[1,2,3],"proved":[1,-2]}
                c0=step(None,a);b=dict(a);b["proved"]=[1,-2,3];c1=step(c0,b)
                return self.sendj(200,{"ok":c0["unanimous"] and c1["unanimous"] and c1["parent_consensus_godel"]==c0["consensus_godel"] and c1.get("shared",{}).get("parent_godel")==c0["consensus_godel"],"layer0":c0["layer"],"layer1":c1["layer"],"step0_godel":c0["consensus_godel"],"step1_godel":c1["consensus_godel"],"step1_boundary":c1.get("shared",{}).get("boundary"),"claims":c1["claims"]})
            if self.path!="/step":return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            return self.sendj(200,step(d.get("parent"),d.get("input",{})))
        except Exception as x:self.sendj(502,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a):pass
HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
