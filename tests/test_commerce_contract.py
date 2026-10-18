"""Release-specific safeguards against corrupting Sunless Sea's trade/economy.

These offline assertions are necessary but NOT a substitute for in-game BUY/SELL,
money refresh, autosave/Load, or QEffectOnEnter regression checks.
"""
import collections
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
RULES = json.loads((ROOT / "ui/ui_rules.json").read_text(encoding="utf-8"))["entries"]


class CommerceContractTests(unittest.TestCase):
    def test_every_shop_delta_targets_only_visible_name_or_description(self):
        patches = json.loads((ROOT / "delta/entities/exchanges.json").read_text(encoding="utf-8"))
        self.assertEqual(len(patches), 156)
        fields = collections.Counter()
        for path, value in patches:
            self.assertIsInstance(path, list)
            self.assertIsInstance(value, str)
            self.assertIn(path[-1], {"Name", "Description"}, path)
            self.assertIs(type(path[0]), int, path)
            if len(path) == 4:
                self.assertEqual(path[1], "Shops", path)
                self.assertIs(type(path[2]), int, path)
            else:
                self.assertEqual(len(path), 2, path)
            fields[path[-1]] += 1
        self.assertEqual(fields, {"Name": 79, "Description": 77})
        self.assertEqual(MANIFEST["files"]["entities/exchanges.json"]["changed_text_fields"], 156)

    def test_item_qualities_patch_only_display_text_never_prices_or_ids(self):
        patches = json.loads((ROOT / "delta/entities/qualities.json").read_text(encoding="utf-8"))
        allowed = {"Name", "Description", "AvailableAt",
                   "LevelDescriptionText", "ChangeDescriptionText"}
        self.assertEqual(len(patches), 2340)
        counts = collections.Counter()
        for path, value in patches:
            self.assertEqual(len(path), 2, path)
            self.assertIs(type(path[0]), int, path)
            self.assertIn(path[1], allowed, path)
            self.assertIsInstance(value, str)
            counts[path[1]] += 1
        self.assertEqual(sum(counts.values()), 2340)
        self.assertEqual(MANIFEST["files"]["entities/qualities.json"]["changed_text_fields"], 2340)

    def test_ui_rules_keep_shop_price_and_input_lookup_identities_original(self):
        forbidden_class = (
            "Sunless.Game.UI.Exchanges.",
            "Sunless.Game.ApplicationProviders.ExchangeProvider",
            "Sunless.Game.ApplicationProviders.TradeRouteProvider",
            "FailBetter.Core.Utility.MoneyDescription",
            "Sunless.Game.Dictionaries.DefaultControlSchemes",
            "Sunless.Game.Dictionaries.HotkeysDictionary",
            "Sunless.Game.Entities.InputController",
        )
        forbidden_literals = {
            "BUY", "SELL", "<b>BUY</b> (1):", "<b>BUY</b> (10):",
            "<b>SELL</b> (1):", "<b>SELL</b> (10):",
            "Stack Item", "Main Menu", "Load", "Save",
        }
        self.assertEqual(len(RULES), 529)
        for rule in RULES:
            with self.subTest(type=rule["type"], english=rule["english"]):
                self.assertFalse(rule["type"].startswith(forbidden_class), rule)
                self.assertNotIn(rule["english"], forbidden_literals)
                if rule["type"] == "Sunless.Game.ApplicationProviders.HoldProvider":
                    self.assertNotIn(rule["method"], {"Assay", "Buy", "Sell"})

    def test_release_remains_a_prerelease_until_real_game_regressions_pass(self):
        status = json.loads((ROOT / "RELEASE_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["full_game_and_commerce_regression"], "not_completed")
        self.assertEqual(status["windows_ui"], "not_verified")
        self.assertFalse(status["game_binary_or_font_in_archive"])
        self.assertEqual(status["translation_changes"], 28080)
        self.assertEqual(status["ui_rules"], 529)
        self.assertEqual(status["ui_display_replacements"], 552)
        readme = (ROOT / "README_ja.md").read_text(encoding="utf-8")
        self.assertIn("BUY / SELL", readme)
        self.assertIn("セーブ", readme)
        self.assertTrue(any(word in readme for word in ("未検証", "未確認", "未実施")))


if __name__ == "__main__":
    unittest.main()
