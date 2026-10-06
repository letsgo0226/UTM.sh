import json,os,urllib.request,functools
from http.server import BaseHTTPRequestHandler,HTTPServer

PEERS=[x.rstrip("/") for x in os.getenv("RCD_PEERS","").split(",") if x.strip()]
J=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
E=lambda s:functools.reduce(lambda n,b:n*257+b+1,s.encode(),1)

def call(url,data):
    b=J(data).encode()
    r=urllib.request.Request(url+"/run",data=b,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(r,timeout=20) as x:return json.loads(x.read())

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=J(o).encode();self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):return self.sendj(200,{"ok":True,"protocol":"RCD-Triple-Consensus/1.0","peers":len(PEERS),"claims":{"global_halting_decider":0,"global_arithmetic_complete":0,"resolves_boundary":0}})
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        if self.path!="/consensus":return self.sendj(404,{"error":"not-found"})
        try:
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            if len(PEERS)!=3:return self.sendj(503,{"error":"need-exactly-3-peers","peers":len(PEERS)})
            rs=[call(p,d) for p in PEERS];cs=[J(x) for x in rs];ok=len(set(cs))==1
            cert={"protocol":"RCD-Triple-Consensus/1.0","unanimous":ok,"peer_count":3,"peer_godels":[x.get("godel") for x in rs],"claims":{"global_halting_decider":0,"global_arithmetic_complete":0,"resolves_boundary":0}}
            if ok:
                x=rs[0];layer=int(x.get("state",{}).get("layer",0))
                cert["shared"]={"godel":x.get("godel"),"gc":x.get("gc"),"boundary":x.get("state",{}).get("boundary"),"lift_required":x.get("lift_required")}
                cert["next_candidate"]={"layer":layer+1,"parent_godel":x.get("godel"),"inherited_boundary":x.get("state",{}).get("boundary"),"status":"validated-boundary-only"}
            cert["consensus_godel"]=E(J(cert))
            q=cert["consensus_godel"];a="";A="ATGC"
            while q:a=A[q%4]+a;q//=4
            cert["atgc"]=a or "A";cert["gc"]=sum(c in "GC" for c in cert["atgc"])
            self.sendj(200,cert)
        except Exception as x:self.sendj(502,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a):pass

HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
