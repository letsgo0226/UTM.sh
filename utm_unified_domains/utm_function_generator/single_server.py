from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from core import run_trace
from single_function import (
    certificate,
    manifest,
    portable_projection,
    single_function_bundle,
    verify_bundle,
    verify_candidate,
    verify_certificate,
)

PORT = int(os.getenv("PORT", "8080"))
MAX_BODY = 131072


def send_json(handler: BaseHTTPRequestHandler, code: int, obj) -> None:
    data = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if self.path in ("/", "/manifest"):
            return send_json(self, 200, manifest())
        if self.path == "/health":
            return send_json(self, 200, {"ok": True, "service": "utm-function-generator", "protocol": manifest()["protocol"]})
        return send_json(self, 404, {"error": "not-found"})

    def _body(self):
        n = int(self.headers.get("Content-Length", "0"))
        if n < 0 or n > MAX_BODY:
            raise ValueError("request body too large")
        value = json.loads(self.rfile.read(n) or b"{}")
        if not isinstance(value, dict):
            raise ValueError("request body must be a JSON object")
        return value

    def _machine_args(self, body):
        return dict(
            program=body.get("program", ""),
            input_text=body.get("input", ""),
            start=str(body.get("start", "0")),
            blank=str(body.get("blank", "_")),
            limit=int(body.get("limit", 64)),
        )

    def do_POST(self):
        try:
            body = self._body()
            if self.path == "/encode":
                return send_json(self, 200, certificate(body.get("payload")))
            if self.path == "/verify":
                return send_json(self, 200, verify_certificate(body.get("payload"), body.get("godel")))
            if self.path == "/utm/trace":
                return send_json(self, 200, run_trace(**self._machine_args(body)))
            if self.path in ("/function/single", "/function/compile"):
                return send_json(self, 200, single_function_bundle(**self._machine_args(body)))
            if self.path == "/function/portable":
                return send_json(self, 200, portable_projection(**self._machine_args(body)))
            if self.path == "/function/verify":
                args = self._machine_args(body)
                return send_json(self, 200, verify_bundle(body.get("bundle", {}), **args))
            if self.path == "/candidate/verify":
                return send_json(self, 200, verify_candidate(body.get("candidate", {})))
            return send_json(self, 404, {"error": "not-found"})
        except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as e:
            return send_json(self, 400, {"error": str(e)})


if __name__ == "__main__":
    print(json.dumps({"event": "utm_single_function_ready", "port": PORT, "protocol": manifest()["protocol"]}, separators=(",", ":")), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
