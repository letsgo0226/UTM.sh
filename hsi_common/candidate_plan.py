#!/usr/bin/env python3
"""HSI stage-2 *proposal-only* source synchronization planner.

A verified drift audit can lead to a narrowly bounded candidate replacement
plan from the declared UTM source. The output is metadata, NOT a diff:
private target file contents never enter public PRs or artifacts.

This cannot create code, write to a repository, call Railway, or trade.
A plan is neither evidence the UTM version is better nor permission to apply.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

from self_deploy_monitor import BRANCH, FILES, MAX_FILE_BYTES, REPOS, fetch_content

PROTOCOL = "HSI-3SYS-CANDIDATE-PLAN/0.2"
VALID_SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_CANDIDATES = (len(REPOS) - 1) * len(FILES)


class PlanHeld(ValueError):
    """A bounded proposal could not be supported by complete evidence."""


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _observed_sha(audit: dict, path: str, repo: str) -> str:
    try:
        value = audit["observations_sha256"][path][repo]
    except (KeyError, TypeError) as exc:
        raise PlanHeld("incomplete_observations") from exc
    if not isinstance(value, str) or not VALID_SHA256.fullmatch(value):
        raise PlanHeld("invalid_sha256_or_unavailable_evidence")
    return value


def generate_plan(audit: dict, read_source=fetch_content) -> dict:
    """Generate immutable-looking review metadata; never perform any mutation."""
    base = {
        "protocol": PROTOCOL,
        "source_branch": BRANCH,
        "canonical_source": REPOS[0],
        "status": "HOLD",
        "candidates": [],
        "checks": {
            "syntax_only": True,
            "behavior_tests_passed": False,
            "independent_security_review": False,
            "platform_authorized": False,
            "staging_deployed": False,
        },
        "permitted_actions": ["review_candidate_metadata"],
        "requires_human_approval": True,
        "may_modify_source": False,
        "may_deploy": False,
        "may_trade": False,
        "private_source_included": False,
        "limitations": (
            "Metadata-only replacement proposals; byte hash + Python syntax checks "
            "do not establish behavioral equivalence or safety. "
            "Never treat the canonical source as automatically correct."
        ),
    }
    try:
        if not isinstance(audit, dict):
            raise PlanHeld("audit_not_object")
        if audit.get("branch") != BRANCH or audit.get("repos") != list(REPOS):
            raise PlanHeld("unexpected_source_scope")
        if audit.get("files") != list(FILES):
            raise PlanHeld("unexpected_file_scope")
        if audit.get("fetch_errors") or audit.get("hsi_formal_gate", {}).get("closed") is not True:
            raise PlanHeld("unverified_or_incomplete_audit")
        status = audit.get("status")
        if status not in {"IN_SYNC", "REVIEW_REQUIRED"}:
            raise PlanHeld("audit_not_admissible")
        mismatches = []
        for path in FILES:
            digests = [_observed_sha(audit, path, repo) for repo in REPOS]
            if len(set(digests)) > 1:
                mismatches.append(path)
        if audit.get("mismatches") != mismatches:
            raise PlanHeld("mismatch_list_disagrees_with_observations")
        if status == "IN_SYNC" and not mismatches:
            base["status"] = "NO_CHANGE"
            return base
        if status != "REVIEW_REQUIRED" or not mismatches:
            raise PlanHeld("audit_status_inconsistent")

        candidates = []
        for path in mismatches:
            source_sha = _observed_sha(audit, path, REPOS[0])
            try:
                data = read_source(REPOS[0], path)
            except Exception as exc:
                raise PlanHeld("canonical_source_unavailable") from exc
            if not isinstance(data, bytes) or len(data) > MAX_FILE_BYTES:
                raise PlanHeld("canonical_source_exceeds_limit")
            if sha256(data) != source_sha:
                raise PlanHeld("canonical_source_changed_after_audit")
            try:
                source_text = data.decode("utf-8", errors="strict")
                ast.parse(source_text, filename=path)
            except (UnicodeDecodeError, SyntaxError) as exc:
                raise PlanHeld("canonical_source_failed_static_syntax") from exc

            for target in REPOS[1:]:
                old_digest = _observed_sha(audit, path, target)
                if old_digest != source_sha:
                    candidates.append({
                        "target_repo": target,
                        "target_ref": BRANCH,
                        "target_path": path,
                        "expected_target_sha256": old_digest,
                        "proposed_source_repo": REPOS[0],
                        "proposed_source_ref": BRANCH,
                        "proposed_source_path": path,
                        "proposed_source_sha256": source_sha,
                        "proposal_kind": "REVIEW_SOURCE_PARITY",
                        "safety": "Do not apply until source semantics and downstream impact are independently reviewed.",
                    })
        if not candidates or len(candidates) > MAX_CANDIDATES:
            raise PlanHeld("candidate_count_exceeds_allowed_bounds")
        base["status"] = "CANDIDATES_READY_FOR_REVIEW"
        base["candidates"] = candidates
        base["checks"]["source_sha256_and_syntax_only"] = True
        return base
    except PlanHeld as exc:
        base["reason"] = str(exc)
        return base


def markdown_report(plan: dict) -> str:
    rows = [
        "# HSI stage-2 bounded synchronization candidates", "",
        f"**Decision:** {plan['status']}", "",
        "These are **proposal records, not patches and not approved changes**.",
        "Target source bytes are never copied to this report.", "",
        "| Target | File | Expected target SHA-256 | Proposed source SHA-256 |",
        "|---|---|---|---|",
    ]
    for candidate in plan["candidates"]:
        rows.append("| \`{target_repo}\` | \`{target_path}\` | \`{expected_target_sha256}\` | \`{proposed_source_sha256}\` |".format(**candidate))
    if plan.get("reason"):
        rows.append(f"\nHold reason: \`{plan['reason']}\`")
    rows.extend([
        "", "Before any change: inspect both versions privately, review the exact",
        "diff in the destination repository, run independent unit and integration",
        "tests in a credential-free sandbox, evaluate security and data persistence,",
        "obtain explicit approval, deploy via the platform's authorized workflow,",
        "perform health checks, and preserve a safe rollback path.",
        "",
        "**No writes, merges, Railway changes, API-key grants, or trading actions**",
        "are performed by this planner.",
    ])
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()
    try:
        audit = json.loads(args.audit.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"HOLD: unreadable audit ({type(exc).__name__})", file=sys.stderr)
        return 2
    plan = generate_plan(audit)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_out.write_text(markdown_report(plan), encoding="utf-8")
    print(json.dumps({"status": plan["status"], "count": len(plan["candidates"]), "reason": plan.get("reason")}))
    return 0 if plan["status"] == "CANDIDATES_READY_FOR_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
