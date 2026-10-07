from __future__ import annotations
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from core import PROTOCOL, ROLE, certify

PORT = int(os.environ.get("PORT", "8080"))

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "protocol": PROTOCOL, "role": ROLE})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/certify":
            return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n <= 0 or n > 16384:
                raise ValueError("invalid request size")
            req = json.loads(self.rfile.read(n))
            out = certify(req)
            return self._send(200 if out["closed"] else 422, out)
        except Exception as exc:
            return self._send(400, {"protocol": PROTOCOL, "closed": 0, "error": str(exc)})

    def log_message(self, fmt, *args):
        print(json.dumps({"model":"HSI_3SYS_HTTP","message":fmt % args}, separators=(",", ":")), flush=True)

if __name__ == "__main__":
    print(json.dumps({"model":"HSI_3SYS_START","protocol":PROTOCOL,"role":ROLE,"port":PORT}, separators=(",", ":")), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
