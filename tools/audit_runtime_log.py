#!/usr/bin/env python3
"""Read-only, privacy-preserving Sunless Sea Player.log exception counters.

Never opens save files or game assets, never edits an input or output file.
A clean log is NOT evidence that an in-game trade, save/load or QEffect A/B test passed.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

MAX_LOG_BYTES = 16 * 1024 * 1024
EXCEPTION_HEADER = re.compile(r"^([A-Za-z0-9_.+`]*(?:Exception|Error))(?::|\s*$)")
PREFAB_ERROR = re.compile(
    r"(?:\b(?:fail(?:ed|ure)?|missing|not found)\b.{0,100}\bprefab\b"
    r"|\bprefab\b.{0,100}\b(?:fail(?:ed|ure)?|missing|not found)\b)", re.I
)


def _error_blocks(text: str) -> list[tuple[str, str]]:
    """Extract exception header + immediately adjacent managed stack, not gameplay logs."""
    lines = text.splitlines()
    blocks = []
    for start, line in enumerate(lines):
        match = EXCEPTION_HEADER.match(line.strip())
        if not match:
            continue
        block = [line]
        for stack_line in lines[start + 1 : start + 121]:
            stripped = stack_line.strip()
            if not stripped:
                break
            # Managed frames, then Unity's own logger frames, may omit leading spaces.
            if (
                stripped.startswith("at ")
                or stripped.startswith("--- End of")
                or stripped.startswith("UnityEngine.")
                or stripped.startswith("Sunless.Game.")
                or stripped.startswith("FailBetter.Core.")
            ):
                block.append(stack_line)
            else:
                break
        blocks.append((match.group(1), "\n".join(block)))
    return blocks


def summarize_text(raw: bytes, basename: str) -> dict:
    """Aggregate signals without returning player names, paths, raw exceptions or saves."""
    text = raw.decode("utf-8", errors="replace")
    blocks = _error_blocks(text)
    kinds = collections.Counter(kind for kind, _ in blocks)
    result = {
        "file": basename,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "exception_count": len(blocks),
        "exception_types": dict(sorted(kinds.items())),
        "qeffect_on_enter_exceptions": 0,
        "qeffect_on_exit_exceptions": 0,
        "qeffect_over_time_exceptions": 0,
        "merchant_tooltip_exceptions": 0,
        "exchange_transaction_exceptions": 0,
        "other_exceptions": 0,
        "prefab_load_error_lines": 0,
    }
    for _, block in blocks:
        matched = False
        for key, token in (
            ("qeffect_on_enter_exceptions", "QEffectOnEnter.ApplyQEffects"),
            ("qeffect_on_exit_exceptions", "QEffectOnExit.ApplyQEffects"),
            ("qeffect_over_time_exceptions", "QEffectOverTime.ApplyQEffects"),
        ):
            if token in block:
                result[key] += 1
                matched = True
        if ("InputController.GetTooltipValue" in block and
                ("AvailabilityPanel.FormatBuyButton" in block or
                 "AvailabilityPanel.FormatSellButton" in block)):
            result["merchant_tooltip_exceptions"] += 1
            matched = True
        if ("ExchangeProvider.Buy" in block or
                "ExchangeProvider.Sell" in block):
            result["exchange_transaction_exceptions"] += 1
            matched = True
        if not matched:
            result["other_exceptions"] += 1
    result["prefab_load_error_lines"] = sum(
        bool(PREFAB_ERROR.search(line)) for line in text.splitlines()
    )
    return result


def _read_log_without_following_links(path: Path, max_bytes: int) -> bytes:
    """Read a regular file with a hard cap; never follow named symlinks.

    O_NOFOLLOW closes the usual symlink substitution race on macOS/Linux.
    Windows checks is_symlink() but does not offer the same race guarantee.
    """
    if path.is_symlink():
        raise ValueError("Symlink game log refused: " + path.name)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ValueError("Cannot open regular game log: " + path.name) from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Non-regular game log refused: " + path.name)
        if metadata.st_size > max_bytes:
            raise ValueError("Log exceeds safe size limit: " + path.name)
        with os.fdopen(fd, "rb") as stream:
            fd = -1
            raw = stream.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError("Log grew beyond safe size limit while being read: " + path.name)
        return raw
    finally:
        if fd != -1:
            os.close(fd)


def summarize_paths(paths: list[Path], max_bytes: int = MAX_LOG_BYTES) -> dict:
    if not paths:
        raise ValueError("At least one log file is required")
    if max_bytes < 1:
        raise ValueError("Invalid read limit")
    if len(paths) > 10:
        raise ValueError("Refusing to read more than 10 logs")
    evidence = []
    for path in paths:
        if path.name not in {"Player.log", "Player-prev.log"}:
            raise ValueError("Only Player.log and Player-prev.log are accepted")
        if not path.exists() and not path.is_symlink():
            raise ValueError("Expected game log missing: " + path.name)
        raw = _read_log_without_following_links(path, max_bytes)
        evidence.append(summarize_text(raw, path.name))
    return {
        "schema": "sunless-sea-runtime-log-audit-v1",
        "status": "READ_ONLY_LOG_COUNTS_NOT_GAMEPLAY_PASS",
        "files": evidence,
        "limits": (
            "Historical logs may contain events from earlier installs. "
            "Zero exceptions does not prove working BUY/SELL, immediate Echo refresh, "
            "successful Load/Save or a same-save unmodified-game A/B test. "
            "Keep log SHA, game build, timestamps, screenshots and save-copy SHA separately."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="Player.log / Player-prev.log (read-only)")
    args = parser.parse_args(argv)
    try:
        result = summarize_paths(args.logs)
    except (OSError, ValueError) as exc:
        print("LOG_AUDIT_FAILED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
