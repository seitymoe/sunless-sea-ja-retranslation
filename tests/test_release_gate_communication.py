"""Offline release-status assertions; synthetic/metadata-only, no game data access.

These checks protect the important distinction between a public prerelease,
an open Draft PR, and an unfinished P0 runtime/compatibility investigation.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseGateCommunicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gates = (ROOT / "RELEASE_GATES_ja.md").read_text(encoding="utf-8")
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.status = json.loads((ROOT / "RELEASE_STATUS.json").read_text(encoding="utf-8"))

    def test_current_public_version_is_prerelease_not_stable(self):
        self.assertIn("v2026.10.19-k26.3-rc3", self.gates)
        self.assertIn("公開済みプレリリース", self.gates)
        self.assertIn("PR #9はDraft・未マージ", self.gates)
        self.assertIn("安定版への昇格は保留", self.gates)
        self.assertNotIn("RC3の現在状態：非公開draft", self.gates)
        self.assertNotIn("最新公開テスト版: v2026.10.19-k26.2", self.gates)

    def test_RC3_static_coverage_is_distinct_from_gameplay_qa(self):
        self.assertEqual(self.manifest["changed_text_fields"], 28073)
        self.assertEqual(self.status["translation_changes"], 28073)
        self.assertIn("差分28,073", self.gates)
        self.assertFalse(self.status["runtime_AB_test_completed"])
        self.assertFalse(self.status["runtime_causation_proven"])
        self.assertTrue(self.status["is_prerelease"])
        self.assertIn("原本英語・旧K25・RC3", self.gates)

    def test_old_release_status_snapshot_explicitly_dated(self):
        self.assertIn(self.status["checked_at_utc"], self.gates)
        self.assertIn("歴史的スナップショット", self.gates)
        self.assertEqual(self.status["release_tag"], "v2026.10.19-k26.3-rc3")
        self.assertEqual(self.status["previous_public_release_tag"], "v2026.10.19-k26.2")

    def test_commerce_and_runtime_blocks_not_misrepresented_as_fixed(self):
        for phrase in ("QEffectOnEnter", "QEffectOverTime", "旧K25相当", "RC3が失敗した証拠ではない", "Steam Cloud"):
            self.assertIn(phrase, self.gates)
        self.assertIn("Windows互換性", self.gates)
        self.assertIn("ユーザーの明示許可", self.gates)


if __name__ == "__main__":
    unittest.main()
