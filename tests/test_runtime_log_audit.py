"""Synthetic-only checks for the read-only runtime log evidence collector.

No real Sunless Sea files, proprietary game data, or user saves are required.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "audit_runtime_log.py"
SPEC = importlib.util.spec_from_file_location("sunless_runtime_log_audit", TOOL)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def exception(name: str, *frames: str) -> bytes:
    return (name + ": synthetic error\n" + "\n".join("  at " + f for f in frames) + "\n\n").encode()


class RuntimeLogAuditContractTests(unittest.TestCase):
    def test_qeffect_entry_counts_and_suppresses_raw_logs(self):
        sample = exception("NullReferenceException", "FailBetter.Core.Character.internalEnactQEffect ()",
                           "Sunless.Game.Phenomena.QualityEffects.QEffectOnEnter.ApplyQEffects ()")
        sample += b"Player Name: Private Captain\nSave path: /Users/private/Steam/Autosave.json\n"
        result = AUDIT.summarize_text(sample, "Player.log")
        self.assertEqual(result["exception_count"], 1)
        self.assertEqual(result["qeffect_on_enter_exceptions"], 1)
        self.assertEqual(result["other_exceptions"], 0)
        self.assertNotIn("Private Captain", json.dumps(result))
        self.assertNotIn("/Users/private", json.dumps(result))
        self.assertNotIn("Autosave.json", json.dumps(result))
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["bytes"], len(sample))

    def test_exit_over_time_and_other_are_counted_separately(self):
        raw = b"".join((
            exception("NullReferenceException", "Sunless.Game.Phenomena.QualityEffects.QEffectOnExit.ApplyQEffects ()"),
            exception("ArgumentException", "Sunless.Game.Phenomena.QualityEffects.QEffectOverTime.ApplyQEffects ()"),
            exception("InvalidOperationException", "Sunless.Game.Scripts.Setup.GameInit.Start ()"),
        ))
        result = AUDIT.summarize_text(raw, "Player-prev.log")
        self.assertEqual(result["exception_count"], 3)
        self.assertEqual(result["qeffect_on_exit_exceptions"], 1)
        self.assertEqual(result["qeffect_over_time_exceptions"], 1)
        self.assertEqual(result["other_exceptions"], 1)

    def test_buy_and_sell_tooltip_exceptions_and_transactions(self):
        raw = b"".join((
            exception("NullReferenceException", "Sunless.Game.Entities.InputController.GetTooltipValue ()",
                      "Sunless.Game.UI.Exchanges.AvailabilityPanel.FormatBuyButton ()"),
            exception("NullReferenceException", "Sunless.Game.Entities.InputController.GetTooltipValue ()",
                      "Sunless.Game.UI.Exchanges.AvailabilityPanel.FormatSellButton ()"),
            exception("InvalidOperationException", "Sunless.Game.ApplicationProviders.ExchangeProvider.Buy ()"),
            exception("InvalidOperationException", "Sunless.Game.ApplicationProviders.ExchangeProvider.Sell ()"),
        ))
        r = AUDIT.summarize_text(raw, "Player.log")
        self.assertEqual(r["exception_count"], 4)
        self.assertEqual(r["merchant_tooltip_exceptions"], 2)
        self.assertEqual(r["exchange_transaction_exceptions"], 2)
        self.assertEqual(r["other_exceptions"], 0)

    def test_unrelated_tooltip_error_is_not_mistaken_for_merchant(self):
        r = AUDIT.summarize_text(exception("NullReferenceException",
              "Sunless.Game.Entities.InputController.GetTooltipValue ()",
              "Sunless.Game.UI.HUD.ContextButton.UpdateContent ()"), "Player.log")
        self.assertEqual(r["merchant_tooltip_exceptions"], 0)
        self.assertEqual(r["other_exceptions"], 1)

    def test_multiple_signal_in_one_stack_is_one_exception(self):
        sample = exception("NullReferenceException",
                           "Sunless.Game.Phenomena.QualityEffects.QEffectOnEnter.ApplyQEffects ()",
                           "Sunless.Game.ApplicationProviders.ExchangeProvider.Buy ()")
        r = AUDIT.summarize_text(sample, "Player.log")
        self.assertEqual(r["exception_count"], 1)
        self.assertEqual(r["qeffect_on_enter_exceptions"], 1)
        self.assertEqual(r["exchange_transaction_exceptions"], 1)
        self.assertEqual(r["other_exceptions"], 0)

    def test_prefab_failure_detected_but_normal_prefab_mentions_ignored(self):
        raw = (b"PrefabManager ready\nFailed to find prefab for UI\n"
               b"Some prefab asset is missing\nPrefab registered successfully\n")
        r = AUDIT.summarize_text(raw, "Player.log")
        self.assertEqual(r["prefab_load_error_lines"], 2)
        self.assertEqual(r["exception_count"], 0)

    def test_exception_text_not_at_start_of_line_is_not_a_header(self):
        raw = b"2026-10-22: NullReferenceException mentioned in an old comment\n"
        r = AUDIT.summarize_text(raw, "Player.log")
        self.assertEqual(r["exception_count"], 0)

    def test_two_log_files_use_separate_hashes_and_do_not_claim_runtime_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            curr = root / "Player.log"
            prev = root / "Player-prev.log"
            curr.write_bytes(exception("NullReferenceException", "Sunless.Game.ApplicationProviders.ExchangeProvider.Buy ()"))
            prev.write_bytes(b"clean historical log\n")
            before = (curr.read_bytes(), prev.read_bytes())
            summary = AUDIT.summarize_paths([curr, prev])
            self.assertEqual(summary["schema"], "sunless-sea-runtime-log-audit-v1")
            self.assertIn("NOT_GAMEPLAY_PASS", summary["status"])
            self.assertEqual([x["exception_count"] for x in summary["files"]], [1, 0])
            self.assertNotEqual(summary["files"][0]["sha256"], summary["files"][1]["sha256"])
            self.assertEqual((curr.read_bytes(), prev.read_bytes()), before)

    def test_missing_and_unapproved_filenames_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "missing"):
                AUDIT.summarize_paths([root / "Player.log"])
            (root / "Autosave.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "Only Player.log"):
                AUDIT.summarize_paths([root / "Autosave.json"])

    def test_symlink_and_dangling_symlink_are_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            real = root / "private-target.txt"
            real.write_text("secret")
            link = root / "Player.log"
            try:
                link.symlink_to(real)
            except (NotImplementedError, OSError):
                self.skipTest("No symlink permission on this platform")
            with self.assertRaisesRegex(ValueError, "Symlink"):
                AUDIT.summarize_paths([link])
            link.unlink()
            link.symlink_to(root / "missing")
            with self.assertRaisesRegex(ValueError, "Symlink"):
                AUDIT.summarize_paths([link])

    def test_directory_named_player_log_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Player.log"
            path.mkdir()
            with self.assertRaises((ValueError, OSError)):
                AUDIT.summarize_paths([path])

    def test_size_cap_blocks_excessive_log_read(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Player.log"
            path.write_bytes(b"x" * 15)
            with self.assertRaisesRegex(ValueError, "size limit"):
                AUDIT.summarize_paths([path], max_bytes=14)
            self.assertEqual(AUDIT.summarize_paths([path], max_bytes=15)["files"][0]["bytes"], 15)

    def test_log_list_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Player.log"
            path.write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "At least one"):
                AUDIT.summarize_paths([])
            with self.assertRaisesRegex(ValueError, "10 logs"):
                AUDIT.summarize_paths([path] * 11)
            with self.assertRaisesRegex(ValueError, "Invalid read limit"):
                AUDIT.summarize_paths([path], max_bytes=0)

    def test_cli_success_and_failures_never_echo_raw_player_text(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            valid = root / "Player.log"
            valid.write_bytes(exception("NullReferenceException", "Sunless.Game.ApplicationProviders.ExchangeProvider.Sell ()")
                              + b"Private Captain: Sensitive Log Content\n")
            cli = subprocess.run([sys.executable, str(TOOL), str(valid)],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(cli.returncode, 0, cli.stderr)
            self.assertEqual(json.loads(cli.stdout)["files"][0]["exchange_transaction_exceptions"], 1)
            self.assertNotIn("Sensitive Log Content", cli.stdout)
            self.assertNotIn("Sensitive Log Content", cli.stderr)
            failure = subprocess.run([sys.executable, str(TOOL), str(root / "Autosave.json")],
                                     capture_output=True, text=True, timeout=10)
            self.assertEqual(failure.returncode, 2)
            self.assertIn("LOG_AUDIT_FAILED", failure.stderr)
            self.assertFalse(failure.stdout)


if __name__ == "__main__":
    unittest.main()
