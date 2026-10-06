from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from core import (
    PROTOCOL,
    manifest,
    program_lift,
    solve_ac,
    tensor_lift,
    verify_certificate,
)

MAX_BODY = 262144


class Handler(BaseHTTPRequestHandler):
    server_version = "UTMAnalyticLift/1.0"

    def _send(self, status: int, payload):
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > MAX_BODY:
            raise ValueError("request body too large")
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8")) if raw else {}

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "protocol": PROTOCOL})
        elif self.path == "/manifest":
            self._send(200, manifest())
        else:
            self._send(404, {"error": "not-found", "protocol": PROTOCOL})

    def do_POST(self):
        try:
            body = self._json_body()
            if self.path in ("/ac/solve", "/ac/verify"):
                result = solve_ac(body)
            elif self.path == "/lift/program":
                result = program_lift(body.get("payload"), body.get("level", 0))
            elif self.path == "/lift/tensor":
                result = tensor_lift(body.get("k"), body.get("n"))
            elif self.path == "/certificate/verify":
                result = verify_certificate(body.get("payload"), body.get("godel"))
            else:
                self._send(404, {"error": "not-found", "protocol": PROTOCOL})
                return
            self._send(200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc), "protocol": PROTOCOL})
        except Exception as exc:
            self._send(500, {"error": "internal-error", "detail": type(exc).__name__, "protocol": PROTOCOL})

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), fmt % args))


def main():
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(json.dumps({"event": "listening", "port": port, "protocol": PROTOCOL}))
    server.serve_forever()


if __name__ == "__main__":
    main()
