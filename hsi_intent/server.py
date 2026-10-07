from __future__ import annotations
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import core

REGISTRY=core.load_registry()

class Handler(BaseHTTPRequestHandler):
    def _send(self,code,obj):
        body=json.dumps(obj,separators=(",",":"),ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path=="/health":
            v=core.validate_registry(REGISTRY)
            return self._send(200 if v["valid"] else 503,{
                "protocol":core.PROTOCOL,
                "ok":bool(v["valid"]),
                "atom_count":v.get("atom_count",0),
                "registry_digest":v.get("registry_digest"),
                "scope":"goal-preservation certificate only"
            })
        return self._send(404,{"error":"not found"})

    def do_POST(self):
        if self.path!="/certify":
            return self._send(404,{"error":"not found"})
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n<0 or n>65536: raise ValueError("body too large")
            req=json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(req,dict): raise ValueError("body must be object")
            result=core.certify_transition(REGISTRY,req)
            return self._send(200 if result.get("closed")==1 else 422,result)
        except Exception as exc:
            return self._send(400,{"protocol":core.PROTOCOL,"closed":0,"error":f"{type(exc).__name__}: {exc}"})

    def log_message(self,fmt,*args):
        return

if __name__=="__main__":
    port=int(os.environ.get("PORT","8080"))
    ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()
