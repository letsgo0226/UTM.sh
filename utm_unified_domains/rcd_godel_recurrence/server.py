import json,os,subprocess
from http.server import BaseHTTPRequestHandler,HTTPServer

K="/app/RCD_GODEL_RECURRENCE_2K_oneline.sh"
class H(BaseHTTPRequestHandler):
    def sendj(self,c,o):
        b=json.dumps(o,separators=(",",":")).encode();self.send_response(c);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/","/health"):return self.sendj(200,{"ok":True,"protocol":"RCD-Godel-Recurrence/1.0","kernel":"2KB-one-liner","claims":{"global_halting_decider":False,"global_arithmetic_complete":False,"resolves_boundary":False}})
        self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        if self.path!="/run":return self.sendj(404,{"error":"not-found"})
        try:
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}")
            e=os.environ.copy();e["RCD_INPUT"]=json.dumps(d,separators=(",",":"))
            p=subprocess.run(["bash",K],env=e,text=True,capture_output=True,timeout=20)
            if p.returncode:return self.sendj(500,{"error":"kernel-failed","stderr":p.stderr[-2000:]})
            self.sendj(200,json.loads(p.stdout))
        except Exception as x:self.sendj(400,{"error":type(x).__name__,"detail":str(x)})
    def log_message(self,*a):pass
HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
