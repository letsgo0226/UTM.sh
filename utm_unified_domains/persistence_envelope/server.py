from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from core import (
    certificate,
    deployment_catalog,
    fleet_verify,
    manifest,
    verify_adapter,
    verify_certificate,
    verify_handoff,
    verify_policy,
    verify_recovery,
    verify_state,
    verify_transition,
)

PORT = int(os.getenv("PORT", "8080"))
MAX_BODY = 262144


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
            return send_json(self, 200, {"ok": True, "service": "utm-persistence-envelope", "protocol": manifest()["protocol"]})
        if self.path == "/catalog":
            return send_json(self, 200, deployment_catalog())
        return send_json(self, 404, {"error": "not-found"})

    def _body(self):
        n = int(self.headers.get("Content-Length", "0"))
        if n < 0 or n > MAX_BODY:
            raise ValueError("request body too large")
        obj = json.loads(self.rfile.read(n) or b"{}")
        if not isinstance(obj, dict):
            raise ValueError("body must be a JSON object")
        return obj

    def do_POST(self):
        try:
            body = self._body()
            if self.path == "/verify/state":
                return send_json(self, 200, verify_state(body))
            if self.path == "/verify/transition":
                return send_json(self, 200, verify_transition(body))
            if self.path == "/verify/handoff":
                return send_json(self, 200, verify_handoff(body))
            if self.path == "/verify/recovery":
                return send_json(self, 200, verify_recovery(body))
            if self.path == "/verify/policy":
                return send_json(self, 200, verify_policy(body))
            if self.path == "/adapter/verify":
                return send_json(self, 200, verify_adapter(str(body.get("adapter", "")), body.get("payload", {})))
            if self.path == "/fleet/verify":
                return send_json(self, 200, fleet_verify(body))
            if self.path == "/certificate":
                return send_json(self, 200, certificate(body.get("payload")))
            if self.path == "/certificate/verify":
                return send_json(self, 200, verify_certificate(body.get("payload"), body.get("godel")))
            return send_json(self, 404, {"error": "not-found"})
        except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as e:
            return send_json(self, 400, {"error": str(e)})


if __name__ == "__main__":
    print(json.dumps({"event": "utm_persistence_envelope_ready", "port": PORT, "protocol": manifest()["protocol"]}, separators=(",", ":")), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
