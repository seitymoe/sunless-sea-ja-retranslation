import sys
import struct
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from extract_qeffect_refs import decode_quality_names, read_script_pointer


class RawQualityReferenceTests(unittest.TestCase):
    def make_raw(self, name, file_id=1, script_id=115):
        data = bytearray(108)
        struct.pack_into("<iq", data, 0, 0, 3366)
        struct.pack_into("<iq", data, 16, file_id, script_id)
        raw = name.encode("utf-8")
        data += struct.pack("<I", len(raw))
        data += raw
        data += b"\x00" * ((-len(raw)) % 4)
        data += bytes(28)
        return bytes(data)

    def test_header_script_pointer(self):
        raw = self.make_raw("Almost Safe")
        self.assertEqual(read_script_pointer(raw), (1, 115))

    def test_exact_source_quality_name(self):
        raw = self.make_raw("Almost Safe")
        self.assertEqual(
            decode_quality_names(raw, {"Almost Safe", "Safe"}),
            [{"offset": 108, "QualityName": "Almost Safe"}],
        )

    def test_other_English_not_recognized(self):
        raw = self.make_raw("Nonexistent Quality")
        self.assertEqual(decode_quality_names(raw, {"Almost Safe"}), [])

    def test_invalid_padding_is_rejected(self):
        raw = bytearray(self.make_raw("Almost Safe"))
        raw[108 + 4 + len("Almost Safe")] = 1
        self.assertEqual(decode_quality_names(raw, {"Almost Safe"}), [])

    def test_short_header_is_rejected(self):
        with self.assertRaises(ValueError):
            read_script_pointer(bytes(4))

    def test_multi_quality_name_is_unresolved_candidate(self):
        raw = self.make_raw("Almost Safe") + struct.pack("<I", 6) + b"Terror" + bytes(2)
        matches = decode_quality_names(raw, {"Almost Safe", "Terror"})
        self.assertEqual([x["QualityName"] for x in matches], ["Almost Safe", "Terror"])


if __name__ == "__main__":
    unittest.main()
