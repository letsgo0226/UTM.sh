import json,os,urllib.request,functools,sys,threading,time
from http.server import BaseHTTPRequestHandler,HTTPServer

hasattr(sys,"set_int_max_str_digits") and sys.set_int_max_str_digits(0)
PEERS=[x.rstrip("/") for x in os.getenv("HU_PEERS","").split(",") if x.strip()]
J=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
E=lambda s:functools.reduce(lambda n,b:n*257+b+1,s.encode(),1)
PROOF={"status":"pending"}

def a4(n):
    b=bin(n)[2:]
    if len(b)&1:b="0"+b
    m={"00":"A","01":"T","10":"G","11":"C"}
    return "".join(m[b[i:i+2]] for i in range(0,len(b),2)) or "A"

def call(url,data):
    b=J(data).encode()
    r=urllib.request.Request(url+"/run",data=b,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(r,timeout=20) as x:return json.loads(x.read())

def valid_parent(p):
    if not isinstance(p,dict) or p.get("protocol")!="UTM-HU-Consensus/1.0" or not p.get("unanimous"): return False
    try:
        core={k:v for k,v in p.items() if k not in ("consensus_godel","atgc","gc")}
        return E(J(core))==int(p.get("consensus_godel"))
    except: return False

def solve(parent,inp):
    if len(PEERS)!=3: raise RuntimeError("need-exactly-3-peers")
    d=dict(inp or {})
    if parent is not None:
        if not valid_parent(parent): raise ValueError("invalid-parent-certificate")
        d["layer"]=int(parent["layer"])+1
        d["parent_godel"]=int(parent["consensus_godel"])
    rs=[call(p,d) for p in PEERS]
    ok=len({J(x) for x in rs})==1
    core={"protocol":"UTM-HU-Consensus/1.0","layer":int(d.get("layer",0)),"parent_consensus_godel":int(d.get("parent_godel",0)),"unanimous":ok,"peer_count":3,"peer_godels":[x.get("godel") for x in rs],"claims":{"global_halting_decider":0,"global_arithmetic_complete":0,"self_awareness":0}}
    if ok:
        x=rs[0]
        core["shared"]={"godel":x.get("godel"),"self_godel":x.get("state",{}).get("self_godel"),"results":x.get("state",{}).get("yuu",{}).get("results"),"boundary":x.get("state",{}).get("hee",{}).get("boundary"),"lift_required":x.get("lift_required"),"parent_godel":x.get("state",{}).get("parent_godel")}
    g=E(J(core));a=a4(g)
    return {**core,"consensus_godel":g,"atgc":a,"gc":sum(c in "GC" for c in a)}

def selftest_result():
    a={"facts":[1,2,-5],"rules":[[[1,2],3],[[3],4]],"queries":[3,4,5,6]}
    c0=solve(None,a);b=dict(a);b["facts"]=[1,2,-5,6];c1=solve(c0,b)
    link=c1["parent_consensus_godel"]==c0["consensus_godel"] and c1.get("shared",{}).get("parent_godel")==c0["consensus_godel"]
    return {"status":"complete","ok":c0["unanimous"] and c1["unanimous"] and link,"layer0":c0["layer"],"layer1":c1["layer"],"parent_link":link,"results0":c0.get("shared",{}).get("results"),"results1":c1.get("shared",{}).get("results"),"boundary0":c0.get("shared",{}).get("boundary"),"boundary1":c1.get("shared",{}).get("boundary"),"claims":c1["claims"]}

def startup_probe():
    global PROOF
    try:
        time.sleep(1);PROOF=selftest_result();print("HU_STARTUP_SELFTEST "+J(PROOF),flush=True)
    except Exception as x:
        PROOF={"status":"error","error":type(x).__name__,"detail":str(x)};print("HU_STARTUP_SELFTEST_ERROR "+J(PROOF),flush=True)

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=J(o).encode();self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"): return self.sendj(200,{"ok":True,"protocol":"UTM-HU-Consensus/1.0","peers":len(PEERS),"claims":{"global_halting_decider":0,"global_arithmetic_complete":0,"self_awareness":0}})
        if self.path=="/proof": return self.sendj(200,PROOF)
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path=="/selftest": return self.sendj(200,selftest_result())
            if self.path!="/solve": return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            return self.sendj(200,solve(d.get("parent"),d.get("input",{})))
        except Exception as x:
            self.sendj(502,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a): pass

threading.Thread(target=startup_probe,daemon=True).start()
HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
