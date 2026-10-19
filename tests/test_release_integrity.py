"""Offline CI regression checks for the release; no proprietary game assets needed."""
import collections
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
RULES = json.loads((ROOT / "ui/ui_rules.json").read_text())["entries"]
MACROS = re.compile(r"\[(?:q|v|x|d):[^\]]*\]|\{[^{}]+\}|<[^>]+>")
FORMAT = re.compile(r"(?<!\{)\{\d+[^{}]*\}(?!\})")

def digest(b):
    return hashlib.sha256(b).hexdigest()

class ReleaseStaticTests(unittest.TestCase):
    def test_checksum_manifest(self):
        entries = json.loads((ROOT / "CHECKSUMS.json").read_text())
        self.assertIsInstance(entries, list)
        recorded = set()
        for item in entries:
            name = item["path"]
            self.assertNotIn(name, recorded)
            recorded.add(name)
            self.assertNotIn("..", Path(name).parts)
            self.assertFalse(Path(name).is_absolute())
            b = (ROOT/name).read_bytes()
            self.assertEqual(item["sha256"], digest(b), name)
            self.assertEqual(item["bytes"], len(b), name)
        # CHECKSUMS covers distributed payloads, not CI/workspace PM documents.
        originals = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()
                     and ".git" not in p.parts and ".github" not in p.parts
                     and "tests" not in p.parts and "tools" not in p.parts
                     and "__pycache__" not in p.parts
                     and p.name not in {"CHECKSUMS.json", ".gitignore", "RELEASE_GATES_ja.md"}}
        self.assertTrue(originals.issubset(recorded), originals-recorded)

    def test_patch_only_has_no_original_game_binaries(self):
        self.assertTrue(MANIFEST["requires_original_english_game_files"])
        self.assertFalse(MANIFEST["contains_original_game_binaries_or_JSON_trees"])
        self.assertTrue(MANIFEST["unofficial"])
        for p in ROOT.rglob("*"):
            if p.is_file() and ".git" not in p.parts:
                self.assertNotIn(p.suffix.lower(), {".dll", ".exe", ".assets", ".bundle", ".save"})
                self.assertNotIn(p.name, {"Autosave.json", "Autosave_fallback.json"})

    def test_delta_consistency_and_no_nontext_entries(self):
        self.assertEqual(MANIFEST["format"], "sunless-sea-ja-patch-only-v1")
        self.assertEqual(len(MANIFEST["files"]), 10)
        n = 0
        for filename, rec in MANIFEST["files"].items():
            p = Path(filename)
            self.assertFalse(p.is_absolute())
            self.assertNotIn("..", p.parts)
            self.assertEqual(p.suffix, ".json")
            self.assertRegex(rec["source_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(rec["target_canonical_json_sha256"], r"^[0-9a-f]{64}$")
            patch = json.loads((ROOT/"delta"/p).read_text())
            self.assertEqual(len(patch), rec["changed_text_fields"])
            seen = set()
            for item in patch:
                self.assertEqual(len(item), 2)
                path, value = item
                self.assertIsInstance(path, list)
                self.assertTrue(path)
                self.assertTrue(all(type(x) in (str, int) for x in path))
                self.assertIsInstance(value, str)
                self.assertNotIn(tuple(path), seen)
                seen.add(tuple(path))
            n += len(patch)
        self.assertEqual(n, 28073)
        self.assertEqual(n, MANIFEST["changed_text_fields"])

    def test_ui_translates_only_safe_context(self):
        self.assertEqual(len(RULES), 529)
        badtypes = ("DefaultControlSchemes", "InputController",
                    "Sunless.Game.ApplicationProviders.ExchangeProvider",
                    "Sunless.Game.UI.Exchanges.AvailabilityPanel",
                    "FailBetter.Core.Utility.MoneyDescription")
        seen = set()
        for rule in RULES:
            key = (rule["assembly"],rule["type"],rule["method"],rule["english"])
            self.assertNotIn(key, seen)
            seen.add(key)
            self.assertIn(rule["assembly"], ("Failbetter.Core.dll", "Sunless.Game.dll"))
            self.assertFalse(any(x in rule["type"] for x in badtypes), rule["type"])
            self.assertNotIn(rule["english"], {"Stack Item", "BUY", "SELL", "Load", "Save", "Main Menu"})
            self.assertNotEqual(rule["english"], rule["japanese"])
            datecase = (rule["english"]=="{0:MMMM} {1}{2}, {0:yyyy}" and
                        rule["japanese"]=="{0:yyyy}年{0:MM}月{1}日")
            self.assertTrue(
                collections.Counter(MACROS.findall(rule["english"])) ==
                collections.Counter(MACROS.findall(rule["japanese"])) or datecase,
                rule["english"])
            fmt1 = sorted(FORMAT.findall(rule["english"]))
            fmt2 = sorted(FORMAT.findall(rule["japanese"]))
            self.assertTrue(fmt1==fmt2 or datecase, rule["english"])
        self.assertEqual(len(RULES), MANIFEST["ui"]["translation_rules"])
        self.assertEqual(MANIFEST["ui"]["translated_managed_string_instructions"], 552)

class InstallerFailClosedTests(unittest.TestCase):
    def fixture(self, tmp):
        base=tmp/"original";base.mkdir()
        rel=tmp/"distribution";(rel/"delta/entities").mkdir(parents=True)
        (base/"entities").mkdir()
        payload=[{"Id":565,"Name":"Carrow's Naval Surplus","Cost":5,
                  "SellPrice":1,"Quality":{"Id":110431},"Enabled":True}]
        raw=json.dumps(payload,ensure_ascii=False,indent=2).encode()
        (base/"entities/exchanges.json").write_bytes(raw)
        modified=json.loads(raw);modified[0]["Name"]="キャロウ海軍放出品店"
        japanese=(json.dumps(modified,ensure_ascii=False,indent=2)+"\n").encode()
        manifest={"format":"sunless-sea-ja-patch-only-v1","files":{"entities/exchanges.json":{
            "source_sha256":digest(raw),"target_canonical_json_sha256":digest(japanese),
            "changed_text_fields":1}}}
        (rel/"manifest.json").write_text(json.dumps(manifest))
        (rel/"delta/entities/exchanges.json").write_text(
            json.dumps([[[0,"Name"],"キャロウ海軍放出品店"]],ensure_ascii=False))
        (rel/"apply_text_patch.py").write_bytes((ROOT/"apply_text_patch.py").read_bytes())
        return base,rel,payload,modified
    def run_installer(self, base, rel, output):
        return subprocess.run([sys.executable,str(rel/"apply_text_patch.py"),"--game-data",str(base),
                               "--output",str(output)],capture_output=True,text=True,timeout=20)
    def test_names_translate_prices_and_game_original_do_not(self):
        with tempfile.TemporaryDirectory() as p:
            base,rel,orig,target=self.fixture(Path(p));out=Path(p)/"out"
            proc=self.run_installer(base,rel,out)
            self.assertEqual(proc.returncode,0,proc.stderr)
            actual=json.loads((out/"japanese_translation/entities/exchanges.json").read_text())
            self.assertEqual(actual,target)
            self.assertEqual(actual[0]["Cost"],5)
            self.assertEqual(actual[0]["SellPrice"],1)
            self.assertEqual(json.loads((base/"entities/exchanges.json").read_text()),orig)
    def test_mismatching_game_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            base,rel,_,_=self.fixture(Path(p));out=Path(p)/"out"
            (base/"entities/exchanges.json").write_text("[]")
            x=self.run_installer(base,rel,out)
            self.assertNotEqual(x.returncode,0)
            self.assertIn("Wrong game version",x.stderr)
            self.assertFalse(out.exists())
    def test_output_inside_game_original_is_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            base,rel,_,_=self.fixture(Path(p))
            x=self.run_installer(base,rel,base/"addon")
            self.assertNotEqual(x.returncode,0)
            self.assertIn("Output may not be inside",x.stderr)
            self.assertFalse((base/"addon").exists())

if __name__ == "__main__":
    unittest.main()
