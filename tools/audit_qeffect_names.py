#!/usr/bin/env python3
"""Read-only QEffectOnEnter quality-name collision audit for owned Sunless Sea files.

The game resolves some scene effects through QualityRepository.GetByName(name).
Renaming a UI-visible Quality.Name may therefore break an internal scene lookup.

Use either:
  python tools/audit_qeffect_names.py --original entities/qualities.json \
      --localized japanese_translation/entities/qualities.json \
      --references qeffect_names_from_owned_assets.json --output findings.json

or (requires separately installed UnityPy):
  python tools/audit_qeffect_names.py --original ... --localized ... \
      --asset path/to/resources.assets --asset path/to/sharedassets0.assets \
      --output findings.json

Never modifies the game, assets, original JSON, addon, or saves. It does NOT
automatically fix or certify the runtime error. See Issue #2.
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def index_qualities(records, label):
    if not isinstance(records, list):
        raise ValueError(label + ": expected quality array")
    indexed = {}
    by_name = collections.defaultdict(list)
    for row in records:
        if not isinstance(row, dict) or type(row.get("Id")) is not int or not isinstance(row.get("Name"), str):
            raise ValueError(label + ": quality has no integer Id or string Name")
        ident = row["Id"]
        if ident in indexed:
            raise ValueError(label + ": duplicate Id " + str(ident))
        indexed[ident] = row
        by_name[row["Name"]].append(ident)
    return indexed, by_name


def analyze(original, localized, references):
    original_by_id, original_by_name = index_qualities(original, "original")
    local_by_id, _ = index_qualities(localized, "localized")
    if set(original_by_id) != set(local_by_id):
        raise ValueError("Quality Id list differs; cannot safely compare")
    if not isinstance(references, list) or not references:
        raise ValueError("No QEffectOnEnter references supplied: cannot infer a clean result")
    risks = []
    unresolved = []
    protected = []
    ignored = []
    for position, ref in enumerate(references):
        if not isinstance(ref, dict):
            raise ValueError("Reference at index " + str(position) + " is not an object")
        classname = ref.get("component") or ref.get("class") or "QEffectOnEnter"
        name = ref.get("QualityName", ref.get("quality_name"))
        if classname != "QEffectOnEnter":
            ignored.append({"reference_index": position, "component": classname})
            continue
        if not isinstance(name, str) or not name:
            unresolved.append({"reference_index": position, "reason": "missing QualityName"})
            continue
        ids = original_by_name.get(name, [])
        evidence = {"reference_index": position, "QualityName": name,
                    "asset": ref.get("asset"), "scene": ref.get("scene"),
                    "object": ref.get("object")}
        if len(ids) != 1:
            unresolved.append({**evidence, "reason": "not found in English qualities"
                               if not ids else "ambiguous original Name", "candidate_ids": ids})
            continue
        ident = ids[0]
        new_name = local_by_id[ident]["Name"]
        result = {**evidence, "quality_id": ident, "localized_Name": new_name,
                  "source_Name": original_by_id[ident]["Name"]}
        if new_name != name:
            risks.append({**result, "action_candidate": "Preserve original English Name, not Quality ID or mechanics"})
        else:
            protected.append(result)

    if not risks and not protected and not unresolved:
        raise ValueError("Supplied records have no QEffectOnEnter references; result cannot be clean")

    return {
        "status": "POSSIBLE_SCENE_LOOKUP_BREAKAGE" if risks else
                  "NO_RENAMED_QEFFECT_REFERENCES_IN_SUPPLIED_INPUT",
        "proven_runtime_causation": False,
        "references_examined": len(references),
        "references_to_non_qeffect_components": len(ignored),
        "at_risk_reference_count": len(risks),
        "unchanged_reference_count": len(protected),
        "unresolved_reference_count": len(unresolved),
        "at_risk": risks,
        "safe_name_matches": protected,
        "unresolved": unresolved,
        "ignored": ignored,
        "source_quality_count": len(original_by_id),
        "only_suggests_Name_reversion": True,
        "modifies_files": False,
    }


def extract_references_from_unity_assets(paths):
    """Best-effort type-tree reader. Zero hits or parse failures are NOT a PASS."""
    try:
        import UnityPy
    except ImportError as exc:
        raise RuntimeError("UnityPy unavailable; use the project's UnityPy environment or supply --references") from exc
    refs = []
    stats = {"assets_scanned": 0, "monobehaviours_seen": 0,
             "typetree_failed": 0, "unclassified_QualityName_fields": 0,
             "verified_QEffectOnEnter": 0}
    for path in paths:
        f = Path(path)
        if not f.is_file():
            raise FileNotFoundError(f)
        env = UnityPy.load(str(f))
        stats["assets_scanned"] += 1
        for item in env.objects:
            if item.type.name != "MonoBehaviour":
                continue
            stats["monobehaviours_seen"] += 1
            try:
                tree = item.read_typetree()
            except Exception:
                stats["typetree_failed"] += 1
                continue
            if not isinstance(tree, dict) or "QualityName" not in tree:
                continue
            script_name = ""
            try:
                comp = item.read()
                script = comp.m_Script.read()
                script_name = str(getattr(script, "m_ClassName",
                                     getattr(script, "name", "")))
            except Exception:
                pass
            if script_name != "QEffectOnEnter":
                # Avoid treating random QualityName fields as proven QEffect references.
                stats["unclassified_QualityName_fields"] += 1
                continue
            val = tree["QualityName"]
            if not isinstance(val, str) or not val:
                continue
            stats["verified_QEffectOnEnter"] += 1
            refs.append({"component": "QEffectOnEnter", "QualityName": val,
                         "asset": f.name, "object": str(item.path_id),
                         "scene": tree.get("m_Name")})
    return refs, stats


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--localized", required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--references", type=Path)
    source.add_argument("--asset", action="append", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise ValueError("Output exists; refusing overwrite: " + str(args.output))
    original = json.loads(args.original.read_text(encoding="utf-8-sig"))
    localized = json.loads(args.localized.read_text(encoding="utf-8-sig"))
    if args.references:
        raw = json.loads(args.references.read_text(encoding="utf-8"))
        refs = raw["references"] if isinstance(raw, dict) else raw
        extraction = {"mode": "provided references", "read_from_live_game": False}
    else:
        refs, extraction = extract_references_from_unity_assets(args.asset)
        extraction["mode"] = "owned Unity asset type-trees"
        if not refs:
            raise RuntimeError("No verified QEffectOnEnter QualityName found. "
                               "Extraction incomplete; report typetree limitations, do not call PASS: "
                               + json.dumps(extraction))
    report = analyze(original, localized, refs)
    report["source_sha256"] = sha_file(args.original)
    report["localized_sha256"] = sha_file(args.localized)
    report["reference_source"] = extraction
    report["next_step"] = ("Investigate exact scene/asset and preserve only these source Names;"
                           " test with copy of saves before touching live game."
                           " Do not mark runtime issue resolved from a static report.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k,v in report.items()
                      if k not in ("at_risk","safe_name_matches","unresolved","ignored")},
                     ensure_ascii=False))
    return 2 if report["at_risk_reference_count"] or report["unresolved_reference_count"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print("QEFFECT_AUDIT_INCOMPLETE:", exc, file=sys.stderr)
        sys.exit(3)
