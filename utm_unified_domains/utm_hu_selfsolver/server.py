import json,os,subprocess,sys
from http.server import BaseHTTPRequestHandler,HTTPServer

hasattr(sys,"set_int_max_str_digits") and sys.set_int_max_str_digits(0)
D=os.path.dirname(os.path.abspath(__file__))
K=os.path.join(D,"UTM_HU_SELFSOLVER_2K_oneline.sh")
SELF=open(K,encoding="utf-8").read()

def run(d):
    e=os.environ.copy()
    e["HU_INPUT"]=json.dumps(d,separators=(",",":"))
    e["HU_SELF"]=SELF
    p=subprocess.run(["bash",K],env=e,text=True,capture_output=True,timeout=20)
    if p.returncode:
        raise RuntimeError(p.stderr[-2000:])
    return json.loads(p.stdout)

class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=json.dumps(o,separators=(",",":")).encode()
        self.send_response(c);self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):
            return self.sendj(200,{"ok":True,"protocol":"UTM-HU-SelfSolver/1.0","kernel_bytes":len(SELF.encode()),"semantics":"finite-Horn-closure","claims":{"global_halting_decider":False,"global_arithmetic_complete":False,"self_awareness":False}})
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            if self.path=="/selftest":
                x=run({"facts":[1,2,-5],"rules":[[[1,2],3],[[3],4]],"queries":[3,4,5,6]})
                ok=x["state"]["yuu"]["results"]=={"3":"PROVED","4":"PROVED","5":"REFUTED","6":"UNRESOLVED"} and x["state"]["self_godel"]>0
                return self.sendj(200,{"ok":ok,"protocol":x["state"]["protocol"],"results":x["state"]["yuu"]["results"],"boundary":x["state"]["hee"]["boundary"],"self_godel_digits":len(str(x["state"]["self_godel"])),"state_godel_digits":len(str(x["godel"])),"claims":x["state"]["claims"]})
            if self.path!="/run":
                return self.sendj(404,{"error":"not-found"})
            n=int(self.headers.get("Content-Length","0"))
            d=json.loads(self.rfile.read(n) or b"{}")
            return self.sendj(200,run(d))
        except Exception as x:
            self.sendj(400,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a): pass

HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
