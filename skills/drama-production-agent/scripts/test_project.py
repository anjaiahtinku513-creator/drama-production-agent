"""Regression tests for record checks. Fixture bytes are deliberately not media."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from project import inspect


class ProjectChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        fixture = b"test record fixture, not playable media"
        (self.root / "fixture.bin").write_bytes(fixture)
        digest = hashlib.sha256(fixture).hexdigest()
        self.item = {"id": "selected", "kind": "video", "state": "accepted",
                     "depends_on": [], "path": "fixture.bin", "sha256": digest,
                     "qa": [{"check": c, "result": "pass", "evidence": "synthetic test record",
                             "sha256": digest} for c in ["technical", "visual", "audio"]]}
        self.data = {"schema_version": 1, "actions": [self.item], "deliverables": ["selected"]}

    def check(self):
        (self.root / "project.json").write_text(json.dumps(self.data), encoding="utf-8")
        return inspect(self.root)

    def test_complete_records_only(self):
        self.assertTrue(self.check()["record_checks_passed"])

    def test_changed_file_invalidates_acceptance(self):
        (self.root / "fixture.bin").write_bytes(b"changed")
        self.assertFalse(self.check()["record_checks_passed"])

    def test_missing_listening_review(self):
        self.item["qa"] = self.item["qa"][:2]
        self.assertFalse(self.check()["record_checks_passed"])

    def test_unknown_submission_dependency(self):
        self.item["depends_on"] = ["source"]
        self.data["actions"].append({"id": "source", "state": "submission_unknown"})
        self.assertFalse(self.check()["record_checks_passed"])

    def test_stale_dependency(self):
        other = copy.deepcopy(self.item)
        other.update(id="source", state="stale")
        self.data["actions"].append(other)
        self.item["depends_on"] = ["source"]
        self.assertFalse(self.check()["record_checks_passed"])

    def test_failed_unused_candidate_does_not_block(self):
        self.data["actions"].append({"id": "old", "state": "failed"})
        self.assertTrue(self.check()["record_checks_passed"])

    def test_cycle_and_missing_dependency(self):
        for dependency in ["selected", "missing"]:
            self.item["depends_on"] = [dependency]
            self.assertFalse(self.check()["record_checks_passed"])

    def test_no_deliverables_is_not_success(self):
        self.data["deliverables"] = []
        self.assertFalse(self.check()["record_checks_passed"])

    def test_init_preserves_existing_project(self):
        args = [sys.executable, str(Path(__file__).with_name("project.py")), "init",
                str(self.root / "new"), "--title", "测试项目", "--mode", "static-comic"]
        first = subprocess.run(args, capture_output=True)
        manifest = self.root / "new" / "project.json"
        before = manifest.read_bytes()
        second = subprocess.run(args, capture_output=True)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 1)
        self.assertEqual(manifest.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
