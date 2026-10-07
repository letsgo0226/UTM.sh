import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from core import PROTOCOL, evaluate, verify_certificate, selftest

SYSTEM_ID=os.getenv("SYSTEM_ID","Trader_42-Guard")

class H(BaseHTTPRequestHandler):
    def sendj(self, code, obj):
        body=json.dumps(obj,separators=(",",":")).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/","/health"):
            return self.sendj(200,{
                "ok":True,
                "protocol":PROTOCOL,
                "system_id":SYSTEM_ID,
                "mode":"guard-only",
                "live_execution":False,
                "principle":"signal forms candidate; risk/TM/GC gate may only allow candidate or fail-closed to HOLD"
            })
        if self.path=="/selftest":
            z=selftest();z["system_id"]=SYSTEM_ID
            return self.sendj(200 if z["ok"] else 500,z)
        return self.sendj(404,{"error":"not-found"})

    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length","0"))
            d=json.loads(self.rfile.read(n) or b"{}")
            if self.path=="/evaluate":
                out=evaluate(d.get("candidate",d),int(d.get("critical_gc",15)))
                out["system_id"]=SYSTEM_ID
                return self.sendj(200,out)
            if self.path=="/verify":
                out=verify_certificate(
                    d.get("candidate",{}),
                    str(d.get("atgc","")),
                    int(d.get("critical_gc",15))
                )
                out["system_id"]=SYSTEM_ID
                return self.sendj(200,out)
            if self.path=="/selftest":
                z=selftest();z["system_id"]=SYSTEM_ID
                return self.sendj(200 if z["ok"] else 500,z)
            return self.sendj(404,{"error":"not-found"})
        except Exception as exc:
            return self.sendj(400,{"error":type(exc).__name__,"detail":str(exc)})

    def log_message(self,*args):
        pass

HTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
