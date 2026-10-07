from __future__ import annotations
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import core

class Handler(BaseHTTPRequestHandler):
    def send_json(self,code,obj):
        body=json.dumps(obj,separators=(",",":"),ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path=="/health":
            v=core.intent_core.validate_registry(core.REGISTRY)
            return self.send_json(200 if v.get("valid") else 503,{
                "protocol":core.PROTOCOL,
                "ok":bool(v.get("valid")),
                "state_protocol":core.state_core.PROTOCOL,
                "intent_protocol":core.intent_core.PROTOCOL,
                "blue_uid":v.get("blue_uid"),
                "atom_count":v.get("atom_count"),
                "scope":"composite certificate only"
            })
        return self.send_json(404,{"error":"not found"})

    def do_POST(self):
        if self.path!="/certify":
            return self.send_json(404,{"error":"not found"})
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n<0 or n>131072: raise ValueError("body too large")
            req=json.loads(self.rfile.read(n) or b"{}")
            result=core.certify(req)
            return self.send_json(200 if result.get("closed")==1 else 422,result)
        except Exception as exc:
            return self.send_json(400,{"protocol":core.PROTOCOL,"closed":0,"error":f"{type(exc).__name__}: {exc}"})

    def log_message(self,fmt,*args):
        return

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",int(os.environ.get("PORT","8080"))),Handler).serve_forever()
