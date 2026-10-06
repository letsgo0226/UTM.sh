import json,os,subprocess
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SH=ROOT/"fixed_point.sh"
PROTOCOL="CLS-Recursive-Fixed-Point/1.0"

def run_core():
    p=subprocess.run(["sh",str(SH)],capture_output=True,text=True,check=True)
    return json.loads(p.stdout)

class H(BaseHTTPRequestHandler):
    def send(self,code,body,ctype):
        b=body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path=="/health":
            return self.send(200,json.dumps({"ok":True,"protocol":PROTOCOL,"sha":False},separators=(",",":")),"application/json")
        if self.path=="/one-liner":
            return self.send(200,SH.read_text(encoding="utf-8").strip(),"text/plain; charset=utf-8")
        if self.path=="/certificate":
            try:
                return self.send(200,json.dumps(run_core(),ensure_ascii=False,separators=(",",":")),"application/json; charset=utf-8")
            except Exception as e:
                return self.send(500,json.dumps({"error":"core_failed","detail":str(e)},separators=(",",":")),"application/json")
        return self.send(404,'{"error":"not_found"}',"application/json")
    def log_message(self,*args): pass

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
