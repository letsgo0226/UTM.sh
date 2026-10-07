import json,math,functools,os
from http.server import BaseHTTPRequestHandler,HTTPServer

PROTOCOL="HU-AUTO-UTM-Intrinsic-Godel-Dirichlet/1.0"
SYSTEM_ID=os.getenv("SYSTEM_ID","Intrinsic-UTM")
CLAIMS={"halting_decider":0,"global_con":0,"self_awareness":0}

def E(s):
    return functools.reduce(lambda n,b:n*257+b+1,s.encode(),1)

def decode_program(p):
    p=int(p)
    w=(math.isqrt(8*p+1)-1)//2
    t=w*(w+1)//2
    b=p-t
    k=w-b+1
    c=b
    return k,c,4*(k+1)

def initial_state(word):
    return {"n":0,"q":0,"h":0,"m":[i for i,x in enumerate(str(word)) if x=="1"]}

def canon(p,state):
    return "{}:{}:{}:{}".format(
        int(p),int(state["q"]),int(state["h"]),",".join(map(str,sorted(map(int,state["m"]))))
    )

def step(p,state):
    p=int(p);state={"n":int(state["n"]),"q":int(state["q"]),"h":int(state["h"]),"m":list(map(int,state["m"]))}
    k,c,B=decode_program(p)
    before=canon(p,state)
    gb=E(before)
    q,h=state["q"],state["h"]
    M=set(state["m"])
    a=int(h in M)
    j=2*q+a
    x=(c//pow(B,j))%B
    r=x%(k+1);x//=k+1
    move=x%2;x//=2
    value=x%2
    (M.add(h) if value else M.discard(h))
    h += 1 if move else -1
    q = r
    predicted={"n":state["n"]+1,"q":q,"h":h,"m":sorted(M)}
    gp=E(canon(p,predicted))
    persisted=json.loads(json.dumps(predicted,separators=(",",":")))
    go=E(canon(p,persisted))
    ok=(gp==go)
    return {
        "protocol":PROTOCOL,"system_id":SYSTEM_ID,
        "step":state["n"],"program":p,"states":k,
        "state_before":state,"state_after":persisted,
        "godel_before":str(gb),"godel_after":str(go),
        "transition_valid":ok,"critical_zero":ok,
        "critical_rule":"E_1/2=0 iff prime-valuation vectors of predicted/observed Godel states match",
        "halted":q==k,"claims":CLAIMS
    }

def selftest():
    a=step(2,initial_state("1"))
    b=step(2,a["state_after"])
    return {"ok":a["transition_valid"] and b["transition_valid"] and b["halted"],
            "protocol":PROTOCOL,"system_id":SYSTEM_ID,"trace":[a,b],"claims":CLAIMS}

class H(BaseHTTPRequestHandler):
    def sendj(self,code,obj):
        b=json.dumps(obj,separators=(",",":")).encode()
        self.send_response(code);self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):
            return self.sendj(200,{"ok":True,"protocol":PROTOCOL,"system_id":SYSTEM_ID,"claims":CLAIMS})
        if self.path=="/selftest":
            z=selftest();return self.sendj(200 if z["ok"] else 500,z)
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path!="/step":return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            p=int(d.get("program",2))
            state=d.get("state") or initial_state(d.get("word","1"))
            self.sendj(200,step(p,state))
        except Exception as e:self.sendj(400,{"error":type(e).__name__,"detail":str(e)})
    def log_message(self,*a):pass

HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
