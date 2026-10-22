"""Authenticated read-only Railway GraphQL probe; optional and fail closed.

GitHub Actions: provide a scoped observer token ONLY on an approved workflow.
No Railway mutations, no PII, no full project metadata or secrets in output.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://backboard.railway.com/graphql/v2"
SCHEMA = "Everlife-Railway-Observation/1.0"
QUERY = """query ProjectState($id: String!) {
  project(id: $id) {
    name
    services {
      edges {
        node {
          name
          serviceInstances {
            edges { node { latestDeployment { status } } }
          }
        }
      }
    }
  }
}"""


def summarize(data):
    if not isinstance(data, dict) or data.get("errors"):
        raise ValueError("Railway GraphQL response returned errors")
    project = (data.get("data") or {}).get("project")
    if not isinstance(project, dict):
        raise ValueError("Railway project response is missing")
    edges = (project.get("services") or {}).get("edges", [])
    if not isinstance(edges, list) or len(edges) > 128:
        raise ValueError("unexpected service count")
    counts = {}
    for edge in edges:
        instances = ((edge or {}).get("node") or {}).get("serviceInstances") or {}
        for entry in instances.get("edges", []):
            status = (((entry or {}).get("node") or {}).get("latestDeployment") or {}).get("status", "UNKNOWN")
            if status not in {"SUCCESS","FAILED","CRASHED","SKIPPED","REMOVED","QUEUED","BUILDING","DEPLOYING",
                              "INITIALIZING","WAITING","NEEDS_APPROVAL","SLEEPING","UNKNOWN"}:
                status = "UNKNOWN"
            counts[status] = counts.get(status, 0) + 1
    return {"source": "RAILWAY_AUTHENTICATED_GRAPHQL_READ", "status": "OBSERVED",
            "service_instance_counts_by_deployment_status": counts,
            "service_count": len(edges),
            "note": "This is an observation of the specified project, not verified service health or readiness."}


def collect(token, project_id, *, kind="oauth"):
    if not token or not project_id:
        return {"source": "none", "status": "NOT_CONFIGURED", "service_count": None}
    if not isinstance(project_id, str) or len(project_id) > 64 or not all(c in "abcdef0123456789-" for c in project_id.lower()):
        return {"source":"none","status":"INVALID_PROJECT_SCOPE","service_count":None}
    headers = {"Content-Type": "application/json", "User-Agent": "Everlife-Open-Readonly/1.0"}
    if kind == "project":
        headers["Project-Access-Token"] = token
    else:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(
        URL,
        data=json.dumps({"query": QUERY, "variables": {"id": project_id}}).encode(),
        headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            if response.status != 200:
                raise ValueError("Railway non-200")
            raw = response.read(128 * 1024 + 1)
            if len(raw) > 128 * 1024:
                raise ValueError("Railway response exceeds read bound")
            result = summarize(json.loads(raw))
    except (ValueError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        # Do not place exception messages in public output; they may contain request details.
        result = {"source": "RAILWAY_AUTHENTICATED_GRAPHQL_READ",
                  "status": "UNAVAILABLE", "service_count": None}
    result["observed_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return result


if __name__ == "__main__":
    result = collect(os.getenv("RAILWAY_OBSERVER_TOKEN", ""),
                     os.getenv("RAILWAY_OBSERVER_PROJECT_ID", ""),
                     kind=os.getenv("RAILWAY_OBSERVER_TOKEN_KIND", "oauth"))
    destination = Path(__file__).resolve().parent/"public"/"railway-observation.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload={"schema":SCHEMA, "observation":result, "writes_performed":0,
             "trading_interactions":0, "deployed":False}
    destination.write_text(json.dumps(payload, indent=2,sort_keys=True)+"\n")
    print(json.dumps({"probe_status":result["status"],"writes_performed":0}))
