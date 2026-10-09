#!/usr/bin/env python3
"""Read-only HSI three-system deployment drift monitor.

This tool compares the source files of the *deployed HSI branches*.  It never
executes remotely fetched code, mutates GitHub/Railway, or authorizes trading.
An HSI certificate only checks its documented finite invariants; it is not
proof of code safety, correctness or permission to deploy.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from core import certify

BRANCH = "hsi-three-system-v1"
REPOS = (
    "letsgo0226/UTM.sh",
    "letsgo0226/Trader_42.sh",
    "letsgo0226/COSMIC_LOVE_IS_THE_SOLUTIONS_FOR_EVERYTHING_HS_ZERO.sh",
)
FILES = ("hsi_common/core.py", "hsi_common/server.py", "hsi_common/test_core.py")
MAX_FILE_BYTES = 262144
BASE_URL = "https://api.github.com"


def fetch_content(repo: str, path: str) -> bytes:
    """Fetch an allowlisted public repository file as inert bytes."""
    if repo not in REPOS or path not in FILES:
        raise ValueError("repository/path not in the fixed allowlist")
    url = f"{BASE_URL}/repos/{quote(repo, safe='/')}/contents/{quote(path, safe='/')}?ref={BRANCH}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "HSI-3SYS-ReadOnly-Audit"}
    # The regular workflow token is scoped to this repository.  The Trader-42
    # source can be private; use a separate explicit read-only credential only
    # for that one repository.  Never grant the monitor write/deploy authority.
    token = (os.environ.get("HSI_AUDIT_READ_TOKEN", "") if repo == REPOS[1]
             else os.environ.get("GITHUB_TOKEN", ""))
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=15) as response:
        data = json.load(response)
    if not isinstance(data, dict) or data.get("encoding") != "base64":
        raise ValueError("unexpected GitHub response encoding")
    payload = base64.b64decode(data["content"], validate=False)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("remote source exceeds byte limit")
    return payload


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def make_report() -> dict:
    """Check actual remote source equality; failures HOLD rather than PASS."""
    observations: dict[str, dict[str, str]] = {}
    errors: list[dict[str, str]] = []
    for path in FILES:
        observations[path] = {}
        for repo in REPOS:
            try:
                observations[path][repo] = _digest(fetch_content(repo, path))
            except Exception as exc:
                observations[path][repo] = "UNAVAILABLE"
                errors.append({"repo": repo, "path": path, "reason": f"{type(exc).__name__}:{getattr(exc, 'code', 'unknown')}"})

    mismatches = [
        path for path, results in observations.items()
        if "UNAVAILABLE" not in results.values() and len(set(results.values())) > 1
    ]

    # The HSI formal gate is intentionally insufficient as a deployment approval.
    certificate = certify({
        "system": "UTM", "step": 1, "previous_step": 0,
        "branch": 0, "budget": len(FILES), "status": "UNRESOLVED",
        "operation": "HOLD", "order": 0,
        "claims": {
            "solve_all": 0, "halting_decider": 0, "infinite_order": 0,
            "analytic_continuation": 0, "rh_proof": 0, "profit_guarantee": 0,
        },
    })
    formally_closed = certificate["closed"] == 1
    if not formally_closed:
        status = "HOLD_FORMAL_GATE"
    elif errors:
        status = "HOLD_FETCH_ERROR"
    elif mismatches:
        status = "REVIEW_REQUIRED"
    else:
        status = "IN_SYNC"

    return {
        "protocol": "HSI-3SYS-SELF-DEPLOY-AUDIT/0.1",
        "branch": BRANCH,
        "repos": list(REPOS),
        "files": list(FILES),
        "status": status,
        "mismatches": mismatches,
        "observations_sha256": observations,
        "fetch_errors": errors,
        "hsi_formal_gate": {
            "protocol": certificate["protocol"],
            "closed": formally_closed,
            "checks": certificate["checks"],
            "scope": certificate["scope"],
        },
        "external_approval_required": True,
        "may_modify_source": False,
        "may_deploy": False,
        "may_trade": False,
        "meaning": "Finite source-drift evidence only; not safety or correctness proof.",
    }


def markdown_report(report: dict) -> str:
    rows = [
        "# HSI three-system source drift review",
        "",
        f"**Decision:** {report['status']}",
        "",
        f"**Source branch:** \`{report['branch']}\`",
        "",
        "| Source file | UTM | Trader-42 | Omega |",
        "|---|---|---|---|",
    ]
    for path, by_repo in report["observations_sha256"].items():
        values = [by_repo[repo] for repo in REPOS]
        short = [v[:12] if v != "UNAVAILABLE" else v for v in values]
        rows.append(f"| \`{path}\` | \`{short[0]}\` | \`{short[1]}\` | \`{short[2]}\` |")
    rows.extend([
        "",
        "This document is an **automatically generated, review-only report**.",
        "It does not alter the runtime, synchronize code, merge a pull request,",
        "authorize cloud changes, or execute trades.",
        "",
        "A source mismatch is evidence requiring investigation, **not** proof",
        "that one copy is safer or newer than another.",
        "",
        "Private Trader-42 access requires HSI_AUDIT_READ_TOKEN with read-only",
        "Contents permission for the Trader-42 repository. Missing access is HOLD.",
        "",
        "GitHub branch protection, platform authorization, independent CI,
        "rollbacks, and human approval remain separate requirements.",
        "",
    ])
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    args = parser.parse_args()
    report = make_report()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "mismatches": report["mismatches"],
        "errors": len(report["fetch_errors"]),
        "hsi_closed": report["hsi_formal_gate"]["closed"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
