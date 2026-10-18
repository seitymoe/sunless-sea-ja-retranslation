#!/usr/bin/env python3
"""Read-only QEffectOnEnter/Exit/OverTime reference extraction from owned Unity assets.

WHY:
Sunless Sea v3.0.0.31 Unity assets often lack serialized MonoBehaviour TypeTree.
UnityPy.read_typetree() is incomplete for >2,000 objects. This extractor resolves
MonoScript names from the *owned* globalgamemanagers.assets and matches the
MonoBehaviour m_Script PPtr and a length-prefixed, source-Quality.Name string.
No downloaded/proprietary data is embedded or uploaded by this tool.

Fail closed: only precise script classes and one valid English Quality.Name
within the raw serialized object count as verified references.
"""
import argparse
import collections
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

CLASSES = {"QEffectOnEnter", "QEffectOnExit", "QEffectOverTime"}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def decode_quality_names(raw, valid_names):
    """Strictly parse aligned [uint32 utf8-length][utf8 name] occurrences."""
    results = set()
    if len(raw) < 32:
        return []
    for offset in range(28, len(raw) - 7, 4):
        size = struct.unpack_from("<I", raw, offset)[0]
        if size < 2 or size > 180 or offset + 4 + size > len(raw):
            continue
        data = raw[offset + 4 : offset + 4 + size]
        try:
            name = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if name in valid_names:
            padding = (-size) % 4
            if raw[offset + 4 + size : offset + 4 + size + padding] != b"\x00" * padding:
                continue
            results.add((offset, name))
    return [{"offset": index, "QualityName": name} for index, name in sorted(results)]


def read_script_pointer(raw):
    if len(raw) < 28:
        raise ValueError("MonoBehaviour serialized body too small")
    return struct.unpack_from("<iq", raw, 16)


def get_class_map(UnityPy, managers):
    env = UnityPy.load(str(managers))
    script_map = {}
    for obj in env.objects:
        if obj.type.name != "MonoScript":
            continue
        script = obj.read()
        name = getattr(script, "m_ClassName", "")
        if name in CLASSES:
            script_map[obj.path_id] = name
    if set(script_map.values()) != CLASSES:
        raise ValueError("Missing expected QEffect script identities: " + repr(script_map))
    return script_map


def extract(UnityPy, data_folder, paths, valid_names):
    manager = data_folder / "globalgamemanagers.assets"
    if not manager.is_file():
        raise FileNotFoundError(manager)
    script_map = get_class_map(UnityPy, manager)
    refs = []
    totals = collections.Counter()
    unresolved = []
    files = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        files[path.name] = sha256(path)
        env = UnityPy.load(str(path))
        gameobjects = {o.path_id: o for o in env.objects if o.type.name == "GameObject"}
        totals["assets_scanned"] += 1
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            totals["monobehaviours_seen"] += 1
            raw = obj.get_raw_data()
            try:
                file_id, script_id = read_script_pointer(raw)
            except ValueError:
                totals["malformed_MonoBehaviour"] += 1
                continue
            if script_id not in script_map or file_id != 1:
                continue
            component = script_map[script_id]
            totals["identified_qeffects"] += 1
            matches = decode_quality_names(raw, valid_names)
            go_file, go_id = struct.unpack_from("<iq", raw, 0)
            go_name = ""
            if go_file == 0 and go_id in gameobjects:
                try:
                    go_name = gameobjects[go_id].read().m_Name
                except Exception:
                    totals["unreadable_GameObject_name"] += 1
            if len(matches) != 1:
                unresolved.append(
                    {"component": component, "asset": path.name,
                     "object": str(obj.path_id), "gameobject": go_name,
                     "candidate_matches": matches}
                )
                continue
            refs.append(
                {"component": component, "QualityName": matches[0]["QualityName"],
                 "asset": path.name, "object": str(obj.path_id),
                 "gameobject": go_name, "script_pathid": script_id,
                 "raw_utf8_string_offset": matches[0]["offset"]}
            )
            totals["verified_components"] += 1
    return refs, unresolved, dict(totals), files, script_map


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--game-data", required=True, type=Path)
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--asset", action="append", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    try:
        import UnityPy
    except ImportError as e:
        raise RuntimeError("UnityPy not installed in this Python environment") from e
    names = {r["Name"] for r in json.loads(args.original.read_text(encoding="utf-8"))}
    paths = [f.resolve() for f in args.asset]
    refs, unresolved, totals, hashes, scripts = extract(
        UnityPy, args.game_data, paths, names
    )
    if not refs:
        raise RuntimeError("No verified references; cannot declare all-safe.")
    output = {
        "status": "READ_ONLY_OWNED_ASSETS_EXACT_SCRIPT_ID_EXTRACTED",
        "format": "sunless-sea-qeffect-v1",
        "scope": "ONLY supplied assets; non-supplied bundles and scenes untested",
        "refs": len(refs),
        "unresolved": unresolved,
        "totals": totals,
        "source_assets_sha256": hashes,
        "script_id_map": scripts,
        "references": refs,
        "game_and_saves_modified": False,
        "proven_runtime_causation": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in output.items()
                      if k not in ("references", "unresolved")}, ensure_ascii=False))
    print("REFERENCES", json.dumps(refs, ensure_ascii=False))
    return 2 if unresolved else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as exc:
        print("QEFFECT_EXTRACTION_INCOMPLETE:", exc, file=sys.stderr)
        sys.exit(3)
