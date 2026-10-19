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
    def test_changelog_states_seven_name_only_fix(self):
        release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
        self.assertEqual(sorted(release["protected_Dock_name_quality_ids"]),[231,102969,108290,108651])
        self.assertEqual(sorted(release["protected_QEffect_quality_ids"]),[102025,102029,111067])
        self.assertEqual(len(set(release["protected_Dock_name_quality_ids"]) | set(release["protected_QEffect_quality_ids"])),7)
    def test_a_stranger_dock_quality_keeps_original_internal_name(self):
        qualities=json.loads((ROOT/"delta/entities/qualities.json").read_text())
        self.assertNotIn([104,"Name"], [p for p,v in qualities])
        manifest=json.loads((ROOT/"manifest.json").read_text())
        self.assertEqual(manifest["changed_text_fields"],28073)
        status=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
        self.assertEqual(status["hardcoded_Dock_quality_name_lookups_checked"],4)
        self.assertTrue(status["upstream_Addressed_As_case_mismatch_unresolved"])
    def test_rc3_readmes_match_manifest_and_still_block_stable(self):
        release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
        manifest=json.loads((ROOT/"manifest.json").read_text())
        readme=(ROOT/"README.md").read_text()
        guide=(ROOT/"README_ja.md").read_text()
        for content in (readme,guide):
            self.assertIn("K26.3 RC3", content)
            self.assertIn("28,073", content)
            self.assertIn("EditorMode", content)
            self.assertIn("未完了", content)
        self.assertEqual(manifest["changed_text_fields"], 28073)
        self.assertEqual(len(release["protected_QEffect_quality_ids"]), 3)
        self.assertEqual(len(release["protected_Dock_name_quality_ids"]), 4)
        self.assertTrue(release["is_prerelease"])
        self.assertFalse(release["runtime_AB_test_completed"])
    def test_dock_editor_only_names_not_claimed_as_normal_game_fix(self):
        guide=(ROOT/"README_ja.md").read_text()
        readme=(ROOT/"README.md").read_text()
        self.assertIn("EditorMode=true", guide)
        self.assertIn("EditorMode=true", readme)
        self.assertIn("QEffect", guide)
        self.assertIn("QEffect", readme)
        self.assertIn("原作", guide)
if __name__=="__main__":unittest.main()
