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
    try:
        b=J(data).encode()
        r=urllib.request.Request(url+"/run",data=b,headers={"Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(r,timeout=12) as x:return {"ok":1,"peer":url,"value":json.loads(x.read())}
    except Exception as e:return {"ok":0,"peer":url,"error":type(e).__name__+":"+str(e)}

def semantic(v):
    st=v.get("state",{})
    return {"layer":int(st.get("layer",0)),"hee":st.get("hee"),"yuu":st.get("yuu")}

def descriptor(x):
    v=x["value"];st=v.get("state",{})
    return {"peer":x["peer"],"protocol":st.get("protocol"),"identity":st.get("identity","HU-Kleene"),"equation":v.get("fixed_point_equation"),"program_index":int(v.get("program_index",0)),"self_source_godel":int(v.get("self_source_godel",0))}

def cert_code(c):
    meta={k:v for k,v in c.items() if k not in ("consensus_godel","atgc","gc","parent_consensus_godel","peer_program_indexes")}
    n=P(int(c.get("parent_consensus_godel",0)),E(J(meta)))
    for e in c.get("peer_program_indexes",[]):n=P(n,int(e))
    return n

def valid_parent(p):
    if not isinstance(p,dict) or p.get("protocol")!="UTM-HU-Kleene-Federated-Quorum/1.1" or not p.get("accepted"):return False
    try:return cert_code(p)==int(p.get("consensus_godel"))
    except:return False

def solve(parent,inp):
    if len(PEERS)!=3:raise RuntimeError("need-exactly-3-peers")
    d=dict(inp or {})
    if parent is None:layer,pg=0,0
    else:
        if not valid_parent(parent):raise ValueError("invalid-parent-certificate")
        layer=int(parent["layer"])+1;pg=int(parent["consensus_godel"])
    d["layer"]=layer;d["parent_godel"]=pg
    raw=[call(p,d) for p in PEERS];good=[x for x in raw if x["ok"]]
    buckets={}
    for x in good:buckets.setdefault(J(semantic(x["value"])),[]).append(x)
    groups=sorted(buckets.values(),key=len,reverse=True);best=groups[0] if groups else []
    all3=len(good)==3
    accepted=(all3 and len(best)==3) or (len(good)==2 and len(best)==2)
    degraded=accepted and len(good)==2
    links=accepted and all(int(x["value"].get("state",{}).get("parent_godel",-1))==pg for x in best)
    accepted=bool(accepted and links)
    core={"protocol":"UTM-HU-Kleene-Federated-Quorum/1.1","layer":layer,"parent_consensus_godel":pg,"accepted":accepted,"healthy_peers":len(good),"matching_peers":len(best),"degraded":degraded,"policy":"semantic 3-of-3 when healthy; semantic 2-of-2 if exactly one peer unavailable; any healthy disagreement rejects","claims":{"kleene_theorem_proved":0,"global_halting_decider":0,"global_arithmetic_complete":0,"self_awareness":0}}
    if accepted:
        sem=semantic(best[0]["value"]);ds=[descriptor(x) for x in best]
        core["shared"]={"semantic":sem,"results":sem.get("yuu",{}).get("results"),"boundary":sem.get("hee",{}).get("boundary"),"parent_link":links,"peer_descriptors":[{k:v for k,v in z.items() if k not in ("program_index","self_source_godel")} for z in ds]}
        core["peer_program_indexes"]=[z["program_index"] for z in ds]
        core["peer_self_source_godels"]=[z["self_source_godel"] for z in ds]
    else:
        core["diagnostics"]=[{"peer":x["peer"],"ok":x["ok"],"error":x.get("error"),"semantic":semantic(x["value"]) if x["ok"] else None} for x in raw]
        core["peer_program_indexes"]=[]
        core["peer_self_source_godels"]=[]
    g=cert_code(core);a=a4(g)
    return {**core,"consensus_godel":g,"atgc":a,"gc":sum(c in "GC" for c in a)}

def selftest_result():
    d0={"facts":[1,2,-5],"rules":[[[1,2],3],[[3],4]],"queries":[3,4,5,6]}
    c0=solve(None,d0);d1=dict(d0);d1["facts"]=[1,2,-5,6];c1=solve(c0,d1)
    stable=len(c0.get("peer_program_indexes",[]))==len(c1.get("peer_program_indexes",[])) and c0.get("peer_program_indexes")==c1.get("peer_program_indexes")
    link=c1["parent_consensus_godel"]==c0["consensus_godel"] and c1.get("shared",{}).get("parent_link")
    identities=[x.get("identity") for x in c1.get("shared",{}).get("peer_descriptors",[])]
    return {"status":"complete","ok":c0["accepted"] and c1["accepted"] and stable and link,"layer0":0,"layer1":1,"healthy0":c0["healthy_peers"],"healthy1":c1["healthy_peers"],"degraded0":c0["degraded"],"degraded1":c1["degraded"],"program_indexes_stable":stable,"parent_link":bool(link),"identities":identities,"boundary0":c0.get("shared",{}).get("boundary"),"boundary1":c1.get("shared",{}).get("boundary"),"claims":c1["claims"]}

def startup_probe():
    global PROOF
    try:
        time.sleep(1);PROOF=selftest_result();print("HU_KLEENE_FEDERATED_STARTUP "+J(PROOF),flush=True)
    except Exception as x:
        PROOF={"status":"error","error":type(x).__name__,"detail":str(x)};print("HU_KLEENE_FEDERATED_ERROR "+J(PROOF),flush=True)

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=J(o).encode();self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):return self.sendj(200,{"ok":True,"protocol":"UTM-HU-Kleene-Federated-Quorum/1.1","peers":len(PEERS),"proof_status":PROOF.get("status")})
        if self.path=="/proof":return self.sendj(200 if PROOF.get("status")=="complete" else 202,PROOF)
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path=="/selftest":return self.sendj(200,selftest_result())
            if self.path!="/solve":return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            out=solve(d.get("parent"),d.get("input",{}));return self.sendj(200 if out["accepted"] else 503,out)
        except Exception as x:self.sendj(502,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a):pass

threading.Thread(target=startup_probe,daemon=True).start()
HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
