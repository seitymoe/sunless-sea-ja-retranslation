"""Release metadata must never overclaim runtime equivalence or QA outcomes."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReleaseMetadataTests(unittest.TestCase):
    def test_candidate_runtime_not_misidentified_as_previous_build(self):
        release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
        manifest=json.loads((ROOT/"manifest.json").read_text())
        self.assertEqual(manifest.get("runtime_equivalent_to"),release.get("runtime_equivalent_to"))
        self.assertIsNone(manifest["runtime_equivalent_to"])
        self.assertFalse(release["runtime_AB_test_completed"])
        self.assertEqual(release["full_game_and_commerce_regression"],"not_completed")
        self.assertTrue(release["is_prerelease"])
    def test_unverified_price_not_marked_as_an_independent_K263_pass(self):
        release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
        self.assertIn("not_gameplay_verified",release["price_display"]["status"])
        self.assertFalse(release["runtime_causation_proven"])
    def test_changelog_states_six_name_only_fix(self):
        release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
        self.assertEqual(sorted(release["protected_Dock_name_quality_ids"]),[102969,108290,108651])
        self.assertEqual(sorted(release["protected_QEffect_quality_ids"]),[102025,102029,111067])
if __name__=="__main__":unittest.main()
