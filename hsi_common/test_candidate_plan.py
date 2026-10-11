"""Credential-free, isolated unit tests for HSI stage-2 candidate planner."""
from __future__ import annotations

import hashlib
import unittest

from candidate_plan import generate_plan, markdown_report
from self_deploy_monitor import BRANCH, FILES, REPOS


GOOD = {
    "core.py": b"def certify(x):\n    return int(x > 0)\n",
    "server.py": b"def serve():\n    return 200\n",
    "test_core.py": b"def test_case():\n    assert True\n",
}
OTHER = {
    "core.py": b"def certify(x):\n    return int(x >= 0)\n",
    "server.py": b"def serve():\n    return 201\n",
    "test_core.py": b"def test_case():\n    assert False\n",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fake_audit(changes=None, unavailable=False):
    changes = changes or {}
    observed = {}
    for path in FILES:
        name = path.rsplit("/", 1)[-1]
        observed[path] = {
            repo: digest(changes.get((repo, path), GOOD[name]))
            for repo in REPOS
        }
    mismatches = [p for p in FILES if len(set(observed[p].values())) > 1]
    return {
        "branch": BRANCH,
        "repos": list(REPOS),
        "files": list(FILES),
        "status": "REVIEW_REQUIRED" if mismatches else "IN_SYNC",
        "observations_sha256": observed,
        "mismatches": mismatches,
        "fetch_errors": [{"reason": "HTTPError:404"}] if unavailable else [],
        "hsi_formal_gate": {"closed": True},
    }


def source_reader(repo, path):
    if repo != REPOS[0]:
        raise AssertionError("Planner must never reread private target bytes")
    return GOOD[path.rsplit("/", 1)[-1]]


class CandidateTests(unittest.TestCase):
    def test_no_source_drift_creates_no_candidate(self):
        plan = generate_plan(fake_audit(), read_source=source_reader)
        self.assertEqual(plan["status"], "NO_CHANGE")
        self.assertFalse(plan["may_deploy"])
        self.assertEqual(plan["candidates"], [])

    def test_drift_proposes_metadata_for_one_private_target(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]})
        plan = generate_plan(audit, read_source=source_reader)
        self.assertEqual(plan["status"], "CANDIDATES_READY_FOR_REVIEW")
        self.assertEqual(len(plan["candidates"]), 1)
        candidate = plan["candidates"][0]
        self.assertEqual(candidate["target_repo"], REPOS[1])
        self.assertEqual(candidate["proposed_source_sha256"], digest(GOOD["core.py"]))
        self.assertEqual(candidate["expected_target_sha256"], digest(OTHER["core.py"]))
        self.assertFalse(plan["private_source_included"])
        self.assertFalse(plan["may_modify_source"])
        self.assertFalse(plan["may_trade"])
        self.assertTrue(plan["requires_human_approval"])

    def test_multiple_drift_targets_bounded(self):
        path = FILES[1]
        audit = fake_audit({
            (REPOS[1], path): OTHER["server.py"],
            (REPOS[2], path): OTHER["server.py"],
        })
        plan = generate_plan(audit, read_source=source_reader)
        self.assertEqual(len(plan["candidates"]), 2)
        self.assertEqual(plan["status"], "CANDIDATES_READY_FOR_REVIEW")

    def test_private_code_never_appears_in_manifest(self):
        secret_marker = b"PRIVATE_PSEUDO_TOKEN_012345"
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): secret_marker})
        plan = generate_plan(audit, read_source=source_reader)
        serialized = str(plan) + markdown_report(plan)
        self.assertNotIn("PRIVATE_PSEUDO_TOKEN", serialized)
        self.assertEqual(plan["status"], "CANDIDATES_READY_FOR_REVIEW")

    def test_stale_source_blocks_all_candidates(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]})
        plan = generate_plan(audit, read_source=lambda r, p: b"def changed(): pass\n")
        self.assertEqual(plan["status"], "HOLD")
        self.assertEqual(plan["reason"], "canonical_source_changed_after_audit")
        self.assertEqual(plan["candidates"], [])

    def test_unavailable_target_holds(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]}, unavailable=True)
        plan = generate_plan(audit, read_source=source_reader)
        self.assertEqual(plan["status"], "HOLD")
        self.assertEqual(plan["candidates"], [])

    def test_role_scope_mismatch_holds(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]})
        audit["repos"] = ["attacker/source"] + audit["repos"][1:]
        plan = generate_plan(audit, read_source=source_reader)
        self.assertEqual(plan["status"], "HOLD")

    def test_invalid_observation_sha_holds(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]})
        audit["observations_sha256"][path][REPOS[1]] = "UNAVAILABLE"
        plan = generate_plan(audit, read_source=source_reader)
        self.assertEqual(plan["status"], "HOLD")
        self.assertEqual(plan["candidates"], [])

    def test_not_approved_when_hsi_formal_gate_fails(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]})
        audit["hsi_formal_gate"]["closed"] = False
        plan = generate_plan(audit, read_source=source_reader)
        self.assertEqual(plan["status"], "HOLD")

    def test_invalid_canonical_syntax_holds(self):
        path = FILES[0]
        broken = b"def oops(:\n"
        audit = fake_audit({
            (REPOS[0], path): broken,
            (REPOS[1], path): OTHER["core.py"],
        })
        plan = generate_plan(
            audit, read_source=lambda r, p: broken if p == path else source_reader(r, p)
        )
        self.assertEqual(plan["status"], "HOLD")
        self.assertEqual(plan["reason"], "canonical_source_failed_static_syntax")

    def test_mismatches_are_not_self_certifying(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]})
        audit["mismatches"] = []
        plan = generate_plan(audit, read_source=source_reader)
        self.assertEqual(plan["status"], "HOLD")

    def test_no_arbitrary_source_code_is_executed(self):
        path = FILES[0]
        audit = fake_audit({(REPOS[1], path): OTHER["core.py"]})
        calls = []

        def read_source(repo, file):
            calls.append((repo, file))
            return source_reader(repo, file)

        plan = generate_plan(audit, read_source=read_source)
        self.assertEqual(plan["status"], "CANDIDATES_READY_FOR_REVIEW")
        self.assertEqual(calls, [(REPOS[0], path)])
        self.assertFalse(plan["checks"]["behavior_tests_passed"])


if __name__ == "__main__":
    unittest.main()
