#!/usr/bin/env python3
"""Write a byte-level audit of the canonical extracted customer release."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "release" / "0.1.0" / "yammerknit-v0.1.0"
OUTPUT = Path(__file__).with_name("release-audit.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    files = sorted(
        (path for path in ROOT.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(ROOT).as_posix().lower(),
    )
    manifest = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    tree = hashlib.sha256()
    for item in manifest:
        tree.update(item["path"].encode("utf-8"))
        tree.update(b"\0")
        tree.update(bytes.fromhex(item["sha256"]))
        tree.update(b"\n")
    audit = {
        "schema_version": "cd-augment-release-audit/v1",
        "root": ROOT.name,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files),
        "tree_sha256": tree.hexdigest(),
        "manifest": manifest,
        "issues": [],
        "summary": {"errors": 0, "warnings": 0},
    }
    OUTPUT.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(audit["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
