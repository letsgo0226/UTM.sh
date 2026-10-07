import json,os,subprocess,sys
from http.server import BaseHTTPRequestHandler,HTTPServer

hasattr(sys,"set_int_max_str_digits") and sys.set_int_max_str_digits(0)
D=os.path.dirname(os.path.abspath(__file__))
K=os.path.join(D,"UTM_HU_KLEENE_BRIDGE_2K_oneline.sh")

def direct_phi(e,d):
    F=set(map(int,d.get("facts",[])));R=d.get("rules",[])
    changed=True
    while changed:
        changed=False
        for r in R:
            p=list(map(int,r[0]));z=int(r[1])
            if all(x in F for x in p) and z not in F:
                F.add(z);changed=True
    Q=list(map(int,d.get("queries",[])))
    v={str(q):("PROVED" if q in F else "REFUTED" if -q in F else "UNRESOLVED") for q in Q}
    B=[q for q in Q if v[str(q)]=="UNRESOLVED"]
    return {"self_godel":e,"hee":{"closure":sorted(F),"boundary":B},"yuu":{"results":v}}

def run(d):
    e=os.environ.copy();e["HU_INPUT"]=json.dumps(d,separators=(",",":"))
    p=subprocess.run(["bash",K],env=e,text=True,capture_output=True,timeout=20)
    if p.returncode: raise RuntimeError(p.stderr[-2000:])
    return json.loads(p.stdout)

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=json.dumps(o,separators=(",",":")).encode();self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):
            return self.sendj(200,{"ok":True,"protocol":"UTM-HU-Kleene-Bridge/1.0","semantics":"concrete-quine-derived-self-index","claims":{"kleene_theorem_proved":False,"global_halting_decider":False,"global_arithmetic_complete":False,"self_awareness":False}})
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path=="/selftest":
                d={"facts":[1,2,-5],"rules":[[[1,2],3],[[3],4]],"queries":[3,4,5,6]}
                x=run(d);e=int(x["program_index"]);phi=direct_phi(e,d);s=x["state"]
                ok=(e==int(x["self_source_godel"])==int(s["self_godel"]) and s["hee"]==phi["hee"] and s["yuu"]==phi["yuu"] and x["fixed_point_equation"]=="P(x)=Phi(program_index,x)")
                return self.sendj(200,{"ok":ok,"program_index_digits":len(str(e)),"equation":x["fixed_point_equation"],"results":s["yuu"]["results"],"boundary":s["hee"]["boundary"],"claims":x["claims"]})
            if self.path!="/run": return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            return self.sendj(200,run(d))
        except Exception as x:
            self.sendj(400,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a): pass

HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
