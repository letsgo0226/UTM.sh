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

# Deterministic bounded snapshot; no subprocess or external API requests.
from pathlib import Path
from unified_machine import simulate
UNIFIED = simulate(json.loads((Path(__file__).resolve().parent / "unified_registry.json").read_text(encoding="utf-8")))
ROUTES["/v1/unified"] = UNIFIED
ROUTES["/"]["routes"].append("/v1/unified")
ROUTES["/v1/manifest"]["unified"] = "/v1/unified"
ROUTES["/openapi.json"]["paths"]["/v1/unified"] = {
    "get": {"summary": "Bounded multi-workload logical scheduler certificate",
            "responses": {"200": {"description": "Read-only synthetic computation"}}}}
ROUTES["/llms.txt"] += "Unified virtual workload snapshot: /v1/unified\\n"
ROUTES["/v1/control"] = {
    "publication_kind": "historical_ci_snapshot_not_live",
    "data": json.loads((Path(__file__).resolve().parent / "public" / "control-plane.json").read_text(encoding="utf-8"))
}
ROUTES["/v1/railway-observation"] = {
    "publication_kind": "historical_ci_snapshot_not_live",
    "data": json.loads((Path(__file__).resolve().parent / "public" / "railway-observation.json").read_text(encoding="utf-8"))
}
ROUTES["/"]["routes"].extend(["/v1/control", "/v1/railway-observation"])
ROUTES["/v1/manifest"].update({"control": "/v1/control",
    "railway_observation": "/v1/railway-observation",
    "snapshot_notice": "Snapshots are historical CI evidence and not continuously synchronized."})
for route in ("/v1/control", "/v1/railway-observation"):
    ROUTES["/openapi.json"]["paths"][route] = {
        "get": {"summary": "Historical CI snapshot, not live state",
                "responses": {"200": {"description": "Read-only machine-readable snapshot"}}}}
ROUTES["/llms.txt"] += ("Historical event bridge: /v1/control\\n"
                        "Historical Railway observer: /v1/railway-observation\\n")


from make_manifest import create as build_integrity_manifest
ROUTES["/v1/integrity"] = {
    "publication_kind": "historical_ci_snapshot_not_live",
    "data": build_integrity_manifest()
}
ROUTES["/"]["routes"].append("/v1/integrity")
ROUTES["/v1/manifest"]["content_integrity"] = "/v1/integrity"
ROUTES["/openapi.json"]["paths"]["/v1/integrity"] = {
    "get": {"summary": "SHA256 integrity manifest for historical local research artifacts",
            "responses": {"200": {"description": "Read-only content integrity metadata"}}}}
ROUTES["/llms.txt"] += "Historical SHA256 integrity: /v1/integrity\\n"

# Plato Cave Gate: compute a bounded evidence review on server startup.
# This is a snapshot of checked research metadata, NOT AI introspection.
from epistemic_gate import review as epistemic_review
CAVE = epistemic_review(
    json.loads((Path(__file__).resolve().parent / "epistemic_claims.json").read_text(encoding="utf-8")),
    DATA,
    UNIFIED,
    ROUTES["/v1/railway-observation"]["data"],
)
ROUTES["/v1/epistemic"] = {
    "publication_kind": "startup_snapshot_not_live_empirical_proof",
    "data": CAVE
}
ROUTES["/"]["routes"].append("/v1/epistemic")
ROUTES["/v1/manifest"]["epistemic_evidence_gate"] = "/v1/epistemic"
ROUTES["/openapi.json"]["paths"]["/v1/epistemic"] = {
    "get": {"summary": "Evidence-calibrated Cave Gate report (not empirical proof)",
            "responses": {"200": {"description": "Read-only research epistemic review"}}}}
ROUTES["/llms.txt"] += "Evidence review: /v1/epistemic\\n"

# Public protocol, not a patient data store or a clinical recommendation engine.
from nutrition_study import review as nutrition_study_review
NUTRITION_SPEC = json.loads((Path(__file__).resolve().parent /
    "nutrition_cognition_odor_study.json").read_text(encoding="utf-8"))
ROUTES["/v1/nutrition-study"] = {
    "publication_kind": "public_nonpersonal_protocol_only",
    "data": nutrition_study_review(NUTRITION_SPEC)
}
ROUTES["/"]["routes"].append("/v1/nutrition-study")
ROUTES["/v1/manifest"]["nutrition_cognition_odor_protocol"] = "/v1/nutrition-study"
ROUTES["/openapi.json"]["paths"]["/v1/nutrition-study"] = {
    "get": {"summary": "Public diet, cognition and odor study protocol (not clinical data)",
            "responses": {"200": {"description": "Metadata only, no participant results"}}}}
ROUTES["/llms.txt"] += "Nutrition, brain fog and odor research protocol: /v1/nutrition-study\\n"

# Cultivated meat, fermentation and plant-based ethics: proposals, not proof.
from ethical_protein import review as ethical_protein_review
ETHICAL_PROTEIN_SPEC = json.loads((Path(__file__).resolve().parent /
    "ethical_protein_transition.json").read_text(encoding="utf-8"))
ROUTES["/v1/ethical-protein"] = {
    "publication_kind": "public_nonpersonal_research_protocol_only",
    "data": ethical_protein_review(ETHICAL_PROTEIN_SPEC)
}
ROUTES["/"]["routes"].append("/v1/ethical-protein")
ROUTES["/v1/manifest"]["ethical_protein_protocol"] = "/v1/ethical-protein"
ROUTES["/openapi.json"]["paths"]["/v1/ethical-protein"] = {
    "get": {"summary": "Nonclinical, sentience-aware protein alternatives research protocol",
            "responses": {"200": {"description": "Public research metadata only"}}}}
ROUTES["/llms.txt"] += "Ethical alternative protein research protocol: /v1/ethical-protein\\n"

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
