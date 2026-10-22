"""Everlife Open: safe, read-only HTTP registry. Never executes submitted code."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from registry import build

DATA = build()
SOURCE = "https://github.com/letsgo0226/UTM.sh/tree/everlife-open-sdg-v1/research/everlife-open"
ROUTES = {
    "/": {"service": "everlife-open", "status": "formal_research_only", "routes": ["/health", "/v1/registry", "/v1/manifest", "/openapi.json", "/llms.txt"]},
    "/health": {"status": "ok", "research_model": "synthetic", "not_medical_or_veterinary_advice": True},
    "/v1/registry": DATA,
    "/v1/manifest": {"schema": "Everlife-Open-Manifest/1.0", "registry": "/v1/registry", "openapi": "/openapi.json", "discovery": "/llms.txt", "source": SOURCE,
                     "evidence_scope": "bounded synthetic computation; no human or veterinary efficacy",
                     "governance": "readonly, human-authorized deployments and shutdown"},
    "/openapi.json": {
        "openapi": "3.0.3", "info": {"title": "Everlife Open Research Registry", "version": "1.0.0",
            "description": "Verified bounded symbolic model, not a medical or veterinary treatment."},
        "paths": {p: {"get": {"summary": summary, "responses": {"200": {"description": "Read-only content"}}}}
                  for p, summary in [("/health", "Liveness"), ("/v1/registry", "Synthetic research record"), ("/v1/manifest", "Machine metadata"), ("/llms.txt", "AI crawler guidance")]},
    },
    "/llms.txt": ("# Everlife Open\n"
                 "Read-only, reproducible G257/ATGC GSH/GSSG-inspired formal research.\n"
                 "Registry: /v1/registry\nOpenAPI: /openapi.json\n"
                 "Human, cat and dog research fields are not evidence of treatment efficacy.\n"
                 "No universal halting solver, immortality, or physical zero entropy is claimed.\n"
                 "No clinical or veterinary dosing or unauthorized deployments.\n"
                 "Source: " + SOURCE + "\n"),
    "/robots.txt": "User-agent: *\nAllow: /\n",
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._respond(send_body=True)

    def do_HEAD(self):
        self._respond(send_body=False)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _respond(self, send_body):
        path = urlsplit(self.path).path
        value = ROUTES.get(path)
        if value is None:
            body, content_type, status = b'{"error":"not_found"}', "application/json; charset=utf-8", 404
        elif isinstance(value, str):
            body, content_type, status = value.encode("utf-8"), "text/plain; charset=utf-8", 200
        else:
            body = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            content_type, status = "application/json; charset=utf-8", 200
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=300" if status == 200 else "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def do_POST(self):
        self.send_error(405, "Read-only service")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
