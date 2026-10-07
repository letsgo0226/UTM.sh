import json,math,os
from http.server import BaseHTTPRequestHandler,HTTPServer

A="ATGC"
PROTOCOL="HU-AUTO-UTM-RH-ATGC-Safe/1.0"
SYSTEM_ID=os.getenv("SYSTEM_ID","HU-AUTO-UTM")
CLAIMS={"rh_proved":0,"zeta_zero_test":0,"host_shell_exec":0,"global_halting_decider":0,"self_awareness":0}

def atgc(s):
    x="".join(A[(v>>j)&3] for v in s.encode() for j in (6,4,2,0))
    u=1
    for ch in x:u=u*4+A.index(ch)
    return x,u,sum(ch in "GC" for ch in x)

def candidate(p,g,W,T):
    w=(math.isqrt(8*p+1)-1)//2
    t=w*(w+1)//2
    b=p-t
    k=w-b+1
    c=b
    B=4*(k+1)
    q=h=0
    M={i for i,x in enumerate(W) if x=="1"}
    n=g-p+1
    z=0
    for z in range(1,n+1):
        a=int(h in M);j=2*q+a
        d=(c//pow(B,j))%B
        r=d%(k+1);d//=k+1;m=d%2;d//=2;v=d%2
        (M.add(h) if v else M.discard(h))
        h+=1 if m else -1
        q=r
        if q==k:break
    out="".join("1" if i in M else "0" for i in range(len(T)))
    if q==k and z==n and out==T:
        x,u,gc=atgc(f"{p}:{k}:{c}:{z}")
        return {"p":p,"tm":[k,c,z],"atgc":x,"uid":u,"gc":gc}
    return None

def step(g,W,T,K):
    g=int(g);K=int(K);W=str(W);T=str(T)
    if g<0 or K<0 or any(c not in "01" for c in W+T):raise ValueError("generation>=0, critical_gc>=0, binary input/target required")
    ok=[];bad=0
    for p in range(g+1):
        z=candidate(p,g,W,T)
        if z is None:continue
        if z["gc"]==K:
            z.update({"sigma":[K,2*K],"coherent":1})
            ok.append(z)
        else:bad+=1
    return {"protocol":PROTOCOL,"system_id":SYSTEM_ID,"generation":g,"input":W,"target":T,"critical_gc":K,"accepted":ok,"rejected_noncritical":bad,"invariant":"gc=K <=> log(B^gc)/log(B^(2K))=1/2","claims":CLAIMS}

def selftest():
    z=step(3,"1","0",15)
    ids=[x["uid"] for x in z["accepted"]]
    return {"ok":bool(any(x["p"]==2 and x["gc"]==15 for x in z["accepted"]) and len(ids)==len(set(ids))),"system_id":SYSTEM_ID,"protocol":PROTOCOL,"accepted":z["accepted"],"claims":CLAIMS}

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=json.dumps(o,separators=(",",":")).encode()
        self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):return self.sendj(200,{"ok":True,"protocol":PROTOCOL,"system_id":SYSTEM_ID,"critical_semantics":"Riemann-line design invariant only; not RH proof","claims":CLAIMS})
        if self.path=="/selftest":
            z=selftest();return self.sendj(200 if z["ok"] else 500,z)
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path=="/selftest":
                z=selftest();return self.sendj(200 if z["ok"] else 500,z)
            if self.path!="/step":return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            z=step(d.get("generation",0),d.get("input","1"),d.get("target","0"),d.get("critical_gc",15))
            return self.sendj(200,z)
        except Exception as e:self.sendj(400,{"error":type(e).__name__,"detail":str(e)})
    def log_message(self,*a):pass

HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
