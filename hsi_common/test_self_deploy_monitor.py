"""Unit tests for read-only HSI deployment drift detection."""
import unittest
from unittest.mock import patch

import self_deploy_monitor as monitor


class SelfDeployMonitorTests(unittest.TestCase):
    def _fake_fetch(self, changed=(), failure=()):
        def fetch(repo, path):
            if (repo, path) in failure:
                raise OSError("simulation: repository unavailable")
            if (repo, path) in changed:
                return (path + "-new-version").encode()
            return (path + "-shared-version").encode()
        return fetch

    def test_matching_sources_are_in_sync_but_not_authorized(self):
        with patch.object(monitor, "fetch_content", self._fake_fetch()):
            report = monitor.make_report()
        self.assertEqual(report["status"], "IN_SYNC")
        self.assertTrue(report["hsi_formal_gate"]["closed"])
        self.assertFalse(report["may_deploy"])
        self.assertFalse(report["may_modify_source"])
        self.assertFalse(report["may_trade"])
        self.assertTrue(report["external_approval_required"])

    def test_changed_copy_triggers_review_only(self):
        changed = {(monitor.REPOS[1], monitor.FILES[0])}
        with patch.object(monitor, "fetch_content", self._fake_fetch(changed=changed)):
            report = monitor.make_report()
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertEqual(report["mismatches"], [monitor.FILES[0]])
        self.assertFalse(report["may_deploy"])

    def test_network_failure_holds_instead_of_approving(self):
        failure = {(monitor.REPOS[2], monitor.FILES[1])}
        with patch.object(monitor, "fetch_content", self._fake_fetch(failure=failure)):
            report = monitor.make_report()
        self.assertEqual(report["status"], "HOLD_FETCH_ERROR")
        self.assertEqual(len(report["fetch_errors"]), 1)
        self.assertFalse(report["may_deploy"])

    def test_unallowlisted_sources_rejected_without_network(self):
        with self.assertRaises(ValueError):
            monitor.fetch_content("other/repo", monitor.FILES[0])
        with self.assertRaises(ValueError):
            monitor.fetch_content(monitor.REPOS[0], ".github/secrets")

    def test_report_does_not_claim_automatic_deployment(self):
        with patch.object(monitor, "fetch_content", self._fake_fetch()):
            report = monitor.make_report()
        markdown = monitor.markdown_report(report)
        self.assertIn("review-only", markdown)
        self.assertIn("human approval", markdown)
        self.assertNotIn("DEPLOYED", markdown)


if __name__ == "__main__":
    unittest.main()
