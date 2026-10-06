from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json,os
from core import PROTOCOL,evaluate,transition,encode_payload,manifest
MAX=262144
class H(BaseHTTPRequestHandler):
    def sendj(self,n,x):
        b=json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
        self.send_response(n);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def body(self):
        n=int(self.headers.get("Content-Length","0"))
        if n<0 or n>MAX:raise ValueError("body too large")
        return json.loads(self.rfile.read(n) or b"{}")
    def do_GET(self):
        if self.path=="/health":self.sendj(200,{"ok":True,"protocol":PROTOCOL})
        elif self.path=="/manifest":self.sendj(200,manifest())
        else:self.sendj(404,{"error":"not-found"})
    def do_POST(self):
        try:
            d=self.body()
            if self.path=="/evaluate":r=evaluate(d)
            elif self.path=="/transition":r=transition(d)
            elif self.path=="/encode":r=encode_payload(d.get("payload"))
            else:self.sendj(404,{"error":"not-found"});return
            self.sendj(200,r)
        except (ValueError,TypeError,json.JSONDecodeError) as e:self.sendj(400,{"error":str(e),"protocol":PROTOCOL})
    def log_message(self,fmt,*args):print("%s - - [%s] %s"%(self.address_string(),self.log_date_time_string(),fmt%args))
ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
