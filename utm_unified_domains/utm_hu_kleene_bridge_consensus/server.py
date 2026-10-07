import json,os,urllib.request,functools,sys,threading,time
from http.server import BaseHTTPRequestHandler,HTTPServer

hasattr(sys,"set_int_max_str_digits") and sys.set_int_max_str_digits(0)
PEERS=[x.rstrip("/") for x in os.getenv("HU_KLEENE_PEERS","").split(",") if x.strip()]
J=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
E=lambda s:functools.reduce(lambda n,b:n*257+b+1,s.encode(),1)
P=lambda a,b:(a+b)*(a+b+1)//2+b
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

def cert_code(c):
    sh=c.get("shared") or {}
    meta={k:v for k,v in c.items() if k not in ("consensus_godel","atgc","gc","parent_consensus_godel","shared")}
    sm={k:v for k,v in sh.items() if k not in ("program_index","self_source_godel")}
    return P(P(int(c.get("parent_consensus_godel",0)),int(sh.get("program_index",0))),P(int(sh.get("self_source_godel",0)),E(J({"meta":meta,"shared":sm}))))

def valid_parent(p):
    if not isinstance(p,dict) or p.get("protocol")!="UTM-HU-Kleene-Consensus/1.0" or not p.get("unanimous"): return False
    try:return cert_code(p)==int(p.get("consensus_godel"))
    except:return False

def solve(parent,inp):
    if len(PEERS)!=3: raise RuntimeError("need-exactly-3-peers")
    d=dict(inp or {})
    if parent is None: layer,pg=0,0
    else:
        if not valid_parent(parent): raise ValueError("invalid-parent-certificate")
        layer=int(parent["layer"])+1;pg=int(parent["consensus_godel"])
    d["layer"]=layer;d["parent_godel"]=pg
    rs=[call(p,d) for p in PEERS]
    same=len({J(x) for x in rs})==1
    x=rs[0] if same else {}
    st=x.get("state",{})
    link=same and int(st.get("parent_godel",-1))==pg
    ok=same and link
    core={"protocol":"UTM-HU-Kleene-Consensus/1.0","layer":layer,"parent_consensus_godel":pg,"unanimous":ok,"peer_count":3,"claims":{"kleene_theorem_proved":0,"global_halting_decider":0,"global_arithmetic_complete":0,"self_awareness":0}}
    if same:
        core["shared"]={"program_index":int(x.get("program_index",0)),"self_source_godel":int(x.get("self_source_godel",0)),"equation":x.get("fixed_point_equation"),"results":st.get("yuu",{}).get("results"),"boundary":st.get("hee",{}).get("boundary"),"parent_link":link}
    g=cert_code(core);a=a4(g)
    return {**core,"consensus_godel":g,"atgc":a,"gc":sum(c in "GC" for c in a)}

def selftest_result():
    d0={"facts":[1,2,-5],"rules":[[[1,2],3],[[3],4]],"queries":[3,4,5,6]}
    c0=solve(None,d0);d1=dict(d0);d1["facts"]=[1,2,-5,6];c1=solve(c0,d1)
    stable=c0.get("shared",{}).get("program_index")==c1.get("shared",{}).get("program_index")
    link=c1["parent_consensus_godel"]==c0["consensus_godel"] and c1.get("shared",{}).get("parent_link")
    return {"status":"complete","ok":c0["unanimous"] and c1["unanimous"] and stable and link,"layer0":0,"layer1":1,"program_index_stable":stable,"parent_link":bool(link),"equation":c1.get("shared",{}).get("equation"),"results0":c0.get("shared",{}).get("results"),"results1":c1.get("shared",{}).get("results"),"boundary0":c0.get("shared",{}).get("boundary"),"boundary1":c1.get("shared",{}).get("boundary"),"claims":c1["claims"]}

def startup_probe():
    global PROOF
    try:
        time.sleep(1);PROOF=selftest_result();print("HU_KLEENE_STARTUP_SELFTEST "+J(PROOF),flush=True)
    except Exception as x:
        PROOF={"status":"error","error":type(x).__name__,"detail":str(x)};print("HU_KLEENE_STARTUP_SELFTEST_ERROR "+J(PROOF),flush=True)

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=J(o).encode();self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"): return self.sendj(200,{"ok":True,"protocol":"UTM-HU-Kleene-Consensus/1.0","peers":len(PEERS),"proof_status":PROOF.get("status"),"claims":{"kleene_theorem_proved":0,"global_halting_decider":0,"global_arithmetic_complete":0,"self_awareness":0}})
        if self.path=="/proof": return self.sendj(200 if PROOF.get("status")=="complete" else 202,PROOF)
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path=="/proof": return self.sendj(200 if PROOF.get("status")=="complete" else 202,PROOF)
            if self.path=="/selftest": return self.sendj(200,selftest_result())
            if self.path!="/solve": return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            return self.sendj(200,solve(d.get("parent"),d.get("input",{})))
        except Exception as x:self.sendj(502,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a): pass

threading.Thread(target=startup_probe,daemon=True).start()
HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
