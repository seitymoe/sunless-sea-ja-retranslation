"""QEffectOnEnter internal Quality.Name lookup regression checks.

Pure synthetic fixtures: never read or redistribute a proprietary game asset.
Runtime causation requires a separate owner-approved in-game A/B test.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_qeffect_names import analyze


class QEffectIdentityTests(unittest.TestCase):
    def setUp(self):
        self.original = [
            {"Id": 101, "Name": "Southern Archipelago", "Description": "Example"},
            {"Id": 102, "Name": "Open Sea", "Description": "Example"},
        ]
        self.reference = [{"component": "QEffectOnEnter", "QualityName": "Southern Archipelago",
                           "asset": "resources.assets", "object": "12", "scene": "test"}]

    def test_unchanged_lookup_name_is_not_at_risk(self):
        localized = [dict(row) for row in self.original]
        localized[0]["Description"] = "日本語の説明"
        result = analyze(self.original, localized, self.reference)
        self.assertEqual(result["at_risk_reference_count"], 0)
        self.assertEqual(result["unresolved_reference_count"], 0)
        self.assertEqual(result["unchanged_reference_count"], 1)
        self.assertFalse(result["proven_runtime_causation"])

    def test_renamed_lookup_name_is_reported_by_stable_quality_id(self):
        localized = [dict(row) for row in self.original]
        localized[0]["Name"] = "南方群島"
        result = analyze(self.original, localized, self.reference)
        self.assertEqual(result["status"], "POSSIBLE_SCENE_LOOKUP_BREAKAGE")
        self.assertEqual(result["at_risk_reference_count"], 1)
        self.assertEqual(result["at_risk"][0]["quality_id"], 101)
        self.assertEqual(result["at_risk"][0]["source_Name"], "Southern Archipelago")
        self.assertEqual(result["at_risk"][0]["localized_Name"], "南方群島")

    def test_reference_missing_from_source_is_unresolved_not_clean(self):
        result = analyze(self.original, self.original,
                         [{"component": "QEffectOnEnter", "QualityName": "Absent Name"}])
        self.assertEqual(result["unresolved_reference_count"], 1)
        self.assertEqual(result["at_risk_reference_count"], 0)

    def test_duplicate_original_name_cannot_be_resolved_by_guess(self):
        src = [dict(r) for r in self.original]
        src[1]["Name"] = src[0]["Name"]
        result = analyze(src, src, self.reference)
        self.assertEqual(result["unresolved_reference_count"], 1)
        self.assertEqual(result["unresolved"][0]["reason"], "ambiguous original Name")

    def test_mismatched_id_set_is_rejected(self):
        localized = [dict(r) for r in self.original]
        localized[0]["Id"] = 103
        with self.assertRaises(ValueError):
            analyze(self.original, localized, self.reference)

    def test_empty_references_fail_closed(self):
        with self.assertRaises(ValueError):
            analyze(self.original, self.original, [])

    def test_non_qeffect_component_is_not_mistaken_for_scene_reference(self):
        refs = self.reference + [{"component": "OtherBehaviour", "QualityName": "Open Sea"}]
        result = analyze(self.original, self.original, refs)
        self.assertEqual(result["references_to_non_qeffect_components"], 1)
        self.assertEqual(result["unchanged_reference_count"], 1)


if __name__ == "__main__":
    unittest.main()
