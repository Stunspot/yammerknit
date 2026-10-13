#!/usr/bin/env python3
"""Deterministic custody, validation, and subtitle helpers for Yammerknits."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import stat
import uuid
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs

TOOL_VERSION = "0.1.0"
JSON_INDENT = 2
MEDIA_EXTENSIONS = {
    ".3gp",
    ".aac",
    ".avi",
    ".flac",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".ogg",
    ".opus",
    ".wav",
    ".webm",
}
REQUIRED_SECTIONS = (
    "Executive Insight Terrain",
    "Insight Clusters",
    "Relational Mesh",
    "Prompt Seeding Kit",
    "Sigil Lexicon",
)
REQUIRED_METADATA = ("Post Date", "Channel", "Title", "URL", "Views", "Desc")
CLUSTER_FIELDS = {
    "cluster_title": r"Cluster Title",
    "sigil_stack": r"Sigil (?:Glyph )?Stack",
    "semantic_shard": r"Semantic Shard",
    "timestamp_anchor": r"Timestamp\s*/?\s*Anchor",
    "formatted_payload": r"Formatted Payload",
    "latent_function": r"Latent Function (?:Summary|Mapping)",
    "rag_echo_shard": r"RAG Echo Shard",
    "priming_worthiness": r"Priming Worthiness",
}
VTT_TIMING = re.compile(
    r"(?P<start>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s+-->\s+"
    r"(?P<end>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})"
)
VTT_TAG = re.compile(r"<[^>]+>")
WINDOWS_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class YammerknitError(RuntimeError):
    """Expected user-facing failure."""


def safe_path(path: Path) -> Path:
    """Reject links/reparse points before resolving long/short path spelling."""
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise YammerknitError(f"Linked/reparse path is unsupported: {part}")
    return path.resolve()


def component(value: object) -> str:
    if (not isinstance(value, str) or not value or value in {".", ".."}
            or WINDOWS_FORBIDDEN.search(value) or value.endswith((" ", "."))
            or value.split(".", 1)[0].upper() in WINDOWS_RESERVED):
        raise YammerknitError("Expected a portable single-component record or file name.")
    return value


def read_object(path: Path) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise YammerknitError(f"Duplicate JSON key in {path.name}: {key}")
            result[key] = value
        return result
    def finite(value):
        raise YammerknitError(f"Non-finite JSON value in {path.name}")
    def floating(value):
        number = float(value)
        if not math.isfinite(number):
            return finite(value)
        return number
    value = json.loads(safe_path(path).read_text("utf-8"), object_pairs_hook=pairs,
                       parse_constant=finite, parse_float=floating)
    if not isinstance(value, dict):
        raise YammerknitError(f"Expected JSON object: {path.name}")
    return value


def required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise YammerknitError(f"Missing or invalid {label}")
    return value


def verified_file(directory: Path, name: object, expected: object) -> Path:
    target = safe_path(directory / component(name))
    if (not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)
            or not target.is_file() or sha256_path(target) != expected):
        raise YammerknitError(f"Missing or changed file: {target}")
    return target


@contextmanager
def record_lock(workspace: Path, record_id: str):
    locks = safe_path(workspace / ".locks")
    locks.mkdir(parents=True, exist_ok=True)
    lock = locks / (sha256_bytes(record_id.encode("utf-8")) + ".lock")
    try:
        with lock.open("x", encoding="utf-8") as handle:
            handle.write(dump_json({"pid": os.getpid(), "record_id": record_id, "started": utc_now()}))
    except FileExistsError as exc:
        raise YammerknitError(f"Record busy or interrupted: {lock}. Confirm no writer is running before removing only this lock.") from exc
    try:
        yield
    finally:
        lock.unlink()
        cleanup_empty_directory(locks)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=JSON_INDENT) + "\n"


def write_new_bytes(path: Path, data: bytes) -> None:
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(data)
    except FileExistsError as exc:
        raise YammerknitError(f"Refusing to overwrite existing path: {path}") from exc


def write_new_text(path: Path, text: str) -> None:
    write_new_bytes(path, text.encode("utf-8"))


def clean_component(value: str, fallback: str = "unknown", limit: int = 72) -> str:
    cleaned = unicodedata.normalize("NFC", value or "")
    cleaned = WINDOWS_FORBIDDEN.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    if not cleaned or cleaned.upper() == "N/A":
        cleaned = fallback
    return cleaned[:limit].rstrip(" .")


def make_record_id(post_date: str, channel: str, title: str, source_hash: str) -> str:
    parts = (
        clean_component(post_date, "undated", 20),
        clean_component(channel, "unknown-channel", 32),
        clean_component(title, "untitled", 56),
        source_hash[:10],
    )
    return " - ".join(parts)


def decode_source(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise YammerknitError("Source is not valid UTF-8 text.") from exc


def ensure_record_absent(workspace: Path, record_id: str) -> None:
    collisions = [
        workspace / "sources" / record_id,
        workspace / "artifacts" / record_id,
        workspace / "revisions" / record_id,
    ]
    existing = [str(path) for path in collisions if path.exists()]
    if existing:
        raise YammerknitError(
            "Refusing to overwrite an existing record: " + ", ".join(existing)
        )


def original_storage_name(original_filename: str | None) -> str:
    suffix = Path(original_filename or "").suffix
    if not re.fullmatch(r"\.[A-Za-z0-9]{1,10}", suffix):
        suffix = ".bin"
    return f"source.original{suffix.lower()}"


def cleanup_empty_directory(path: Path) -> None:
    try:
        path.rmdir()
    except OSError:
        pass


def create_source_record(
    *,
    workspace: Path,
    original: bytes,
    normalized: str,
    post_date: str,
    channel: str,
    title: str,
    source_kind: str,
    origin: str | None,
    url: str | None,
    acquisition_method: str,
    rights_basis: str | None,
    original_filename: str | None,
    transformations: list[str],
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    workspace = safe_path(workspace)
    source_hash = sha256_bytes(original)
    record_id = make_record_id(post_date, channel, title, source_hash)
    component(record_id)
    for area in ("sources", "artifacts", "revisions", ".staging"):
        safe_path(workspace / area / record_id)
    ensure_record_absent(workspace, record_id)

    final_dir = workspace / "sources" / record_id
    staging_root = safe_path(workspace / ".staging")
    staging_root.mkdir(parents=True, exist_ok=True)
    staging_dir = Path(tempfile.mkdtemp(prefix="record-", dir=staging_root))
    staged_record = staging_dir / record_id
    staged_record.mkdir()
    try:
        original_name = original_storage_name(original_filename)
        original_path = staged_record / original_name
        normalized_path = staged_record / "source.txt"
        original_path.write_bytes(original)
        normalized_path.write_text(normalized, encoding="utf-8", newline="\n")
        manifest: dict[str, object] = {
            "schema": "yammerknit.source-manifest.v1",
            "record_id": record_id,
            "created_at": utc_now(),
            "source_kind": source_kind,
            "origin": origin,
            "url": url,
            "acquisition_method": acquisition_method,
            "rights_basis": rights_basis,
            "original_filename": original_filename,
            "files": {
                "original": original_name,
                "normalized": "source.txt",
            },
            "post_date": post_date,
            "channel": channel,
            "title": title,
            "transformations": transformations,
            "hashes": {
                original_name: sha256_path(original_path),
                "source.txt": sha256_path(normalized_path),
            },
            "tool": {"name": "yammerknit_tool", "version": TOOL_VERSION},
        }
        if extra:
            manifest["acquisition"] = extra
        (staged_record / "source-manifest.json").write_text(
            dump_json(manifest), encoding="utf-8", newline="\n"
        )
        final_dir.parent.mkdir(parents=True, exist_ok=True)
        if final_dir.exists():
            raise YammerknitError(f"Refusing to overwrite existing path: {final_dir}")
        os.replace(staged_record, final_dir)
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)
        cleanup_empty_directory(staging_root)

    return {
        "status": "created",
        "record_id": record_id,
        "source_directory": str(final_dir),
        "manifest": str(final_dir / "source-manifest.json"),
        "source_sha256": source_hash,
    }


def section_body(text: str, heading: str, next_heading: str | None = None) -> str:
    end = rf"(?=^#+\s*{re.escape(next_heading)}\s*$)" if next_heading else r"\Z"
    match = re.search(
        rf"(?ims)^#+\s*{re.escape(heading)}\s*$\s*(?P<body>.*?){end}",
        text,
    )
    return match.group("body").strip() if match else ""


def nonempty_field(block: str, label_pattern: str) -> bool:
    for line in block.splitlines():
        plain = line.replace("**", "")
        if re.match(rf"(?i)^[ \t]*{label_pattern}[ \t]*:[ \t]*\S.*$", plain):
            return True
    return False


def nonempty_labeled_block(block: str, label_pattern: str) -> bool:
    lines = block.splitlines()
    for index, line in enumerate(lines):
        plain = line.replace("**", "")
        match = re.match(
            rf"(?i)^[ \t]*{label_pattern}[ \t]*:[ \t]*(?P<value>.*)$", plain
        )
        if not match:
            continue
        if match.group("value").strip():
            return True
        for candidate in lines[index + 1 :]:
            stripped = candidate.strip()
            if not stripped:
                continue
            plain_candidate = stripped.replace("**", "")
            if stripped.startswith("#") or any(
                re.match(rf"(?i)^{pattern}[ \t]*:", plain_candidate)
                for pattern in CLUSTER_FIELDS.values()
            ):
                return False
            return True
    return False


def markdown_table_has_value(section: str, column_name: str) -> bool:
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in section.splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    for index, header in enumerate(rows):
        matching_columns = [
            column_index
            for column_index, value in enumerate(header)
            if value.casefold() == column_name.casefold()
        ]
        if not matching_columns:
            continue
        for row in rows[index + 1 :]:
            if all(re.fullmatch(r":?-{3,}:?", value) for value in row):
                continue
            for column_index in matching_columns:
                if column_index < len(row) and row[column_index].strip():
                    return True
    return False


def nonempty_field_or_table_column(
    section: str, label_pattern: str, column_name: str
) -> bool:
    return nonempty_field(section, label_pattern) or markdown_table_has_value(
        section, column_name
    )


def valid_windows_header(text: str) -> bool:
    match = re.search(
        r"(?m)^#\s+(?P<date>.+?)\s+-\s+(?P<channel>.+?)\s+-\s+(?P<title>.+?)\s*$",
        text,
    )
    if not match:
        return False
    components = [match.group("date"), match.group("channel"), match.group("title")]
    for component in components:
        cleaned = component.strip()
        if (
            not cleaned
            or WINDOWS_FORBIDDEN.search(cleaned)
            or cleaned.endswith((" ", "."))
            or cleaned.upper() in WINDOWS_RESERVED
        ):
            return False
    return True


def validate_text(
    text: str,
    artifact_path: str | None = None,
    artifact_sha256: str | None = None,
) -> dict[str, object]:
    physical_hash = artifact_sha256 or sha256_bytes(text.encode("utf-8"))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    checks: dict[str, bool] = {}
    errors: list[str] = []
    stripped = text.strip()

    checks["utf8_replacement_character_absent"] = "\ufffd" not in text
    wrapper = re.match(r"^(`{3,})(?:[A-Za-z0-9_-]*)\n", stripped)
    fence = wrapper.group(1) if wrapper else ""
    checks["codefenced_wrapper"] = bool(wrapper and stripped.endswith("\n" + fence) and not re.search(r"(?m)^`{" + str(len(fence)) + r",}[ \t]*$", stripped[wrapper.end():-(len(fence)+1)]))
    checks["windows_safe_header"] = valid_windows_header(text)

    for field in REQUIRED_METADATA:
        key = f"metadata_{field.lower().replace(' ', '_')}"
        if field == "Desc":
            preface = text.split("Executive Insight Terrain", 1)[0]
            match = re.search(r"(?ims)^\s*Desc\s*:\s*(?P<value>.*)$", preface)
            checks[key] = bool(
                match and match.group("value").strip("`# \r\n\t")
            )
        else:
            checks[key] = bool(
                re.search(
                    rf"(?mi)^[ \t]*{re.escape(field)}[ \t]*:[ \t]*\S.*$",
                    text,
                )
            )

    for section in REQUIRED_SECTIONS:
        key = "section_" + section.lower().replace(" ", "_")
        checks[key] = bool(re.search(rf"(?mi)^#+\s*{re.escape(section)}\s*$", text))

    cluster_area_match = re.search(
        r"(?is)Insight Clusters(?P<body>.*?)(?:^|\n)#+\s*Relational Mesh",
        text,
    )
    cluster_area = cluster_area_match.group("body") if cluster_area_match else ""
    cluster_starts = list(
        re.finditer(
            r"(?mi)^#{3,}\s*(?:(?:Insight )?Cluster(?:\s+\d+)?(?:\s*[:—-].*)?|\d+\.\s+.+)$",
            cluster_area,
        )
    )
    if not cluster_starts:
        cluster_starts = list(
            re.finditer(r"(?mi)^\s*(?:\*\*)?Cluster Title(?:\*\*)?\s*:", cluster_area)
        )
    checks["at_least_one_cluster"] = len(cluster_starts) >= 1

    cluster_blocks: list[str] = []
    for index, start in enumerate(cluster_starts):
        end = cluster_starts[index + 1].start() if index + 1 < len(cluster_starts) else len(cluster_area)
        cluster_blocks.append(cluster_area[start.start() : end])

    for field_name, pattern in CLUSTER_FIELDS.items():
        if field_name == "cluster_title":
            present = bool(cluster_blocks) and all(nonempty_field(block, pattern) for block in cluster_blocks)
        elif field_name == "formatted_payload":
            present = bool(cluster_blocks) and all(
                nonempty_labeled_block(block, pattern) for block in cluster_blocks
            )
        else:
            present = bool(cluster_blocks) and all(
                nonempty_field(block, pattern) for block in cluster_blocks
            )
        checks[f"cluster_{field_name}"] = present

    executive = section_body(text, "Executive Insight Terrain", "Insight Clusters")
    bridge_pattern = (
        r"(?mi)^[ \t]*(?:[-*][ \t]*)?(?:\*\*)?"
        r"Bridge Highlight(?:[ \t]+[—–-][ \t]+[^:\r\n*]+)?"
        r"[ \t]*:(?:\*\*)?[ \t]*\S.*$"
    )
    bridge_match = re.search(bridge_pattern, executive)
    prose = executive[: bridge_match.start()] if bridge_match else executive
    sentence_count = len(re.findall(r"[.!?](?=\s|$)", prose))
    bridge_highlights = len(re.findall(bridge_pattern, executive))
    checks["executive_terrain_present"] = bool(prose.strip())
    checks["executive_bridge_highlights_or_single_cluster"] = bridge_highlights >= 1 or len(cluster_blocks) == 1

    relational_mesh = section_body(text, "Relational Mesh", "Prompt Seeding Kit")
    checks["relational_mesh_has_relationship"] = bool(
        re.search(r"(?:⇄|<->|Source Cluster|Target Cluster)", relational_mesh)
    )
    checks["relational_mesh_has_bridge_type"] = nonempty_field_or_table_column(
        relational_mesh, r"Bridge Type", "Bridge Type"
    )
    checks["relational_mesh_has_strategic_value"] = nonempty_field_or_table_column(
        relational_mesh, r"Strategic Value", "Strategic Value"
    )

    titles = set()
    for block in cluster_blocks:
        match = re.search(r"(?mi)^\s*Cluster Title\s*:\s*(.+)$", block.replace("**", ""))
        if match:
            titles.add(match.group(1).strip())
        titles.update(re.findall(r"⟨[^\n⟩]+⟩", block))
    bridges = []
    mesh_lines = relational_mesh.replace("**", "").splitlines()
    for i, line in enumerate(mesh_lines):
        if ("⇄" in line or "<->" in line) and not line.lstrip().startswith("|"):
            ends = re.split(r"⇄|<->", line.strip(), maxsplit=1)
            stop = next((j for j in range(i+1, len(mesh_lines)) if "⇄" in mesh_lines[j] or "<->" in mesh_lines[j]), len(mesh_lines))
            body = "\n".join(mesh_lines[i+1:stop])
            bridges.append(all(e.strip() in titles for e in ends) and all(nonempty_field(body, label) for label in ("Bridge Type", "(?:Relationship )?Effect", "Strategic Value")))
    tables = [[c.strip() for c in line.strip().strip("|").split("|")] for line in mesh_lines if line.strip().startswith("|")]
    if tables:
        header = tables[0]
        for row in tables[1:]:
            if all(re.fullmatch(r":?-{3,}:?", c) for c in row):
                continue
            mapping = dict(zip(header, row))
            pair = mapping.get("Source ⇄ Target", "")
            ends = re.split(r"⇄|<->", pair)
            bridges.append(len(ends) == 2 and all(e.strip() in titles for e in ends) and bool(mapping.get("Bridge Type")) and bool(mapping.get("Relationship Effect", mapping.get("Effect"))) and bool(mapping.get("Strategic Value")))
    no_bridge = not bridges and len(cluster_blocks) == 1 and bool(re.search(r"(?i)no (?:supported |cross-cluster )?bridge", relational_mesh))
    checks["all_bridges_resolve_and_have_type_effect_value"] = (bool(bridges) and all(bridges)) or no_bridge
    if no_bridge:
        for name in ("relational_mesh_has_relationship", "relational_mesh_has_bridge_type", "relational_mesh_has_strategic_value"):
            checks[name] = True

    prompt_kit = section_body(text, "Prompt Seeding Kit", "Sigil Lexicon")
    checks["prompt_seeding_kit_has_multiple_seeds"] = (
        len(re.findall(r"(?m)^\s*[-*]\s+\S.+$", prompt_kit)) >= 2
    )

    lexicon = section_body(text, "Sigil Lexicon")
    cluster_sigils = set(re.findall(r"⟨[^\n⟩]+⟩", cluster_area))
    lexicon_sigils = set(re.findall(r"⟨[^\n⟩]+⟩", lexicon))
    checks["sigil_lexicon_has_entries"] = bool(
        re.search(r"(?m)^\s*[-*]\s+\S.+$", lexicon)
    ) or markdown_table_has_value(lexicon, "Sigil Stack")
    checks["sigil_lexicon_covers_cluster_sigils"] = bool(cluster_sigils) and (
        cluster_sigils <= lexicon_sigils
    )

    defined_sigils = set()
    for line in lexicon.splitlines():
        if line.lstrip().startswith(("-", "*")):
            match = re.match(r"\s*[-*]\s*(⟨[^⟩]+⟩)\s*(?:—|–|-|:)\s*(.+)", line)
            if match and match.group(2).strip():
                defined_sigils.add(match.group(1))
        elif line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[1] and re.fullmatch(r"⟨[^⟩]+⟩", cells[0]):
                defined_sigils.add(cells[0])
    checks["sigils_have_plain_language_definitions"] = bool(cluster_sigils) and cluster_sigils <= defined_sigils

    for name, passed in checks.items():
        if not passed:
            errors.append(name)

    encoded = text.encode("utf-8")
    return {
        "schema": "yammerknit.validation.v1",
        "tool": {"name": "yammerknit_tool", "version": TOOL_VERSION},
        "checked_at": utc_now(),
        "artifact": artifact_path,
        "artifact_sha256": physical_hash,
        "valid": not errors,
        "checks": checks,
        "errors": errors,
        "scope": "Structural consistency only; source fidelity and retrieval benefit require separate review.",
        "warnings": (["SOP executive guidance is 5-8 sentences and 2-3 bridge highlights; use only as much as the source warrants."] if not (5 <= sentence_count <= 8 and 2 <= bridge_highlights <= 3) else []),
    }


def validate_path(path: Path) -> dict[str, object]:
    raw = safe_path(path).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return {
            "schema": "yammerknit.validation.v1",
            "tool": {"name": "yammerknit_tool", "version": TOOL_VERSION},
            "checked_at": utc_now(),
            "artifact": str(path),
            "artifact_sha256": sha256_bytes(raw),
            "valid": False,
            "checks": {"valid_utf8": False},
            "errors": ["valid_utf8"],
        }
    return validate_text(text, str(path), sha256_bytes(raw))


def inspect_record(workspace: Path, record_id: str | None = None) -> dict[str, object]:
    workspace = safe_path(workspace)
    if record_id is None:
        rows = []
        source_root = safe_path(workspace / "sources")
        for directory in sorted(source_root.iterdir() if source_root.exists() else [], key=lambda p: p.name.casefold()):
            try:
                status = inspect_record(workspace, directory.name)
                rows.append(status)
            except (YammerknitError, OSError, ValueError) as exc:
                rows.append({"record_id": directory.name, "health": "error", "current": None, "error": str(exc)})
        return {"schema": "yammerknit.inventory.v1", "records": rows,
                "scope": "Local custody inventory; no semantic search or embedding execution."}
    component(record_id)
    source_dir = safe_path(workspace / "sources" / record_id)
    source_manifest = source_dir / "source-manifest.json"
    source = read_object(source_manifest)
    if source.get("schema") != "yammerknit.source-manifest.v1" or source.get("record_id") != record_id:
        raise YammerknitError("Source manifest identity mismatch")
    files, hashes = source.get("files"), source.get("hashes")
    if not isinstance(files, dict) or not isinstance(hashes, dict):
        raise YammerknitError("Source manifest files/hashes must be objects")
    for role in ("original", "normalized"):
        name = component(files.get(role))
        verified_file(source_dir, name, hashes.get(name))
    if files["original"] == files["normalized"]:
        raise YammerknitError("Original and normalized source must remain distinct")
    binding = {"source_manifest_sha256": sha256_path(source_manifest), "hashes": hashes}
    warnings = []
    nodes = {}
    base_dir = safe_path(workspace / "artifacts" / record_id)
    revision_root = safe_path(workspace / "revisions" / record_id)
    candidates = []
    if base_dir.exists():
        candidates.append(("base", base_dir, "artifact-manifest.json"))
    if revision_root.exists():
        for directory in sorted(revision_root.iterdir()):
            safe_path(directory)
            if not directory.is_dir():
                raise YammerknitError("Unexpected non-directory in revision chain")
            if directory.name == "base":
                raise YammerknitError("Revision identity cannot alias the base artifact")
            candidates.append((component(directory.name), directory, "revision-manifest.json"))
    for key, directory, manifest_name in candidates:
        manifest = read_object(directory / manifest_name)
        kind = "artifact" if key == "base" else "revision"
        if manifest.get("schema") != f"yammerknit.{kind}-manifest.v1" or manifest.get("record_id") != record_id:
            raise YammerknitError("Artifact manifest identity mismatch")
        if key != "base" and manifest.get("revision_id") != key:
            raise YammerknitError("Revision directory and identity disagree")
        target = verified_file(directory, manifest.get("artifact"), manifest.get("artifact_sha256"))
        receipt = read_object(directory / component(manifest.get("validation_receipt")))
        checks = receipt.get("checks")
        if (receipt.get("schema") != "yammerknit.validation.v1" or receipt.get("valid") is not True
                or receipt.get("artifact_sha256") != manifest["artifact_sha256"]
                or receipt.get("artifact") != manifest["artifact"] or receipt.get("errors") != []
                or not isinstance(checks, dict) or not checks or any(v is not True for v in checks.values())):
            raise YammerknitError("Validation receipt contradicts or does not bind the stored artifact")
        if "source_binding" in manifest:
            if manifest["source_binding"] != binding:
                raise YammerknitError("Artifact source binding is stale")
        else:
            warnings.append(f"{key}: legacy source binding unavailable; present source hashes checked, historical authorship not established")
        if key == "base":
            expected = f"../../sources/{record_id}/source-manifest.json"
            if manifest.get("source_manifest") != expected:
                raise YammerknitError("Base source reference does not name this record")
        nodes[key] = {"manifest": manifest, "artifact": str(target)}
    if nodes and "base" not in nodes:
        raise YammerknitError("Revision chain has no base artifact")
    children = {key: [] for key in nodes}
    for key, node in nodes.items():
        if key == "base":
            continue
        parent = node["manifest"].get("parent")
        if not isinstance(parent, dict) or parent.get("kind") not in ("base", "revision"):
            raise YammerknitError("Invalid revision parent")
        parent_key = "base" if parent["kind"] == "base" else component(parent.get("revision_id"))
        if (parent["kind"] == "revision" and parent_key == "base") or parent_key not in nodes or parent.get("artifact_sha256") != nodes[parent_key]["manifest"]["artifact_sha256"]:
            raise YammerknitError("Missing or mismatched revision parent")
        children[parent_key].append(key)
    chain = []
    key = "base" if nodes else None
    while key is not None:
        if key in chain or len(children[key]) > 1:
            raise YammerknitError("Revision cycle or ambiguous fork; no current artifact selected")
        chain.append(key)
        key = children[key][0] if children[key] else None
    if len(chain) != len(nodes):
        raise YammerknitError("Disconnected revision cycle; no current artifact selected")
    current = None
    if chain:
        last = chain[-1]
        current = {"kind": "base" if last == "base" else "revision", "artifact": nodes[last]["artifact"],
                   "artifact_sha256": nodes[last]["manifest"]["artifact_sha256"]}
        if last != "base":
            current["revision_id"] = last
    return {"schema": "yammerknit.record-status.v1", "health": "verified-present-bytes", "record_id": record_id,
            "title": source.get("title"), "channel": source.get("channel"), "source_manifest": str(source_manifest),
            "base_artifact_present": bool(nodes), "revision_count": max(0, len(nodes)-1), "chain": chain,
            "current": current, "source_binding": binding, "warnings": warnings,
            "limit": "Hashes detect disagreement with manifests, not coordinated tampering, source truth, semantic fidelity or model authorship."}


def store_artifact(artifact: Path, workspace: Path, record_id: str, revision: bool) -> dict[str, object]:
    workspace, artifact = safe_path(workspace), safe_path(artifact)
    component(record_id)
    with record_lock(workspace, record_id):
        status = inspect_record(workspace, record_id)
        raw = artifact.read_bytes()
        receipt = validate_text(decode_source(raw), str(artifact), sha256_bytes(raw))
        if not receipt["valid"]:
            raise YammerknitError("Artifact failed structural validation: " + ", ".join(receipt["errors"]))
        current = status["current"]
        if revision and current is None:
            raise YammerknitError("Cannot create a revision before the base artifact exists.")
        if not revision and current is not None:
            raise YammerknitError("Refusing to overwrite existing base artifact; create a revision.")
        revision_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12] if revision else None
        target_dir = safe_path(workspace / ("revisions" if revision else "artifacts") / record_id)
        if revision:
            target_dir = safe_path(target_dir / revision_id)
        if target_dir.exists():
            raise YammerknitError(f"Refusing to overwrite existing path: {target_dir}")
        stage_root = safe_path(workspace / ".staging")
        stage_root.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix="artifact-", dir=stage_root))
        candidate = stage / "record"
        candidate.mkdir()
        try:
            (candidate / "yammerknit.md").write_bytes(raw)
            receipt["artifact"] = "yammerknit.md"
            (candidate / "validation.json").write_text(dump_json(receipt), encoding="utf-8", newline="\n")
            manifest = {"schema": f"yammerknit.{'revision' if revision else 'artifact'}-manifest.v1",
                        "record_id": record_id, "created_at": utc_now(), "artifact_sha256": sha256_bytes(raw),
                        "artifact": "yammerknit.md", "validation_receipt": "validation.json",
                        "source_binding": status["source_binding"], "tool": {"name": "yammerknit_tool", "version": TOOL_VERSION}}
            if revision:
                manifest["revision_id"] = revision_id
                manifest["parent"] = {k: v for k, v in current.items() if k != "artifact"}
            else:
                manifest["source_manifest"] = f"../../sources/{record_id}/source-manifest.json"
            name = "revision-manifest.json" if revision else "artifact-manifest.json"
            (candidate / name).write_text(dump_json(manifest), encoding="utf-8", newline="\n")
            # Recheck the bound source and ancestry immediately before publishing.
            if inspect_record(workspace, record_id) != status:
                raise YammerknitError("Record changed during storage; retry from inspection")
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            if target_dir.exists():
                raise YammerknitError("Destination appeared during storage")
            os.rename(candidate, target_dir)
        finally:
            shutil.rmtree(stage, ignore_errors=True)
            cleanup_empty_directory(stage_root)
    result = {"status": "revision-created" if revision else "artifact-created", "record_id": record_id,
              "artifact": str(target_dir / "yammerknit.md"), "manifest": str(target_dir / name),
              "validation": str(target_dir / "validation.json")}
    if revision:
        result["revision_id"] = revision_id
    return result


def normalize_vtt_text(vtt: str) -> str:
    """Readable cue projection, retaining distinct events; raw VTT remains primary."""
    lines = vtt.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or not re.fullmatch(r"WEBVTT(?:[ \t].*)?", lines[0]):
        raise YammerknitError("Expected a WEBVTT header")
    def seconds(stamp):
        parts = stamp.split(":")
        hours, minutes, sec = (int(parts[0]), int(parts[1]), float(parts[2])) if len(parts) == 3 else (0, int(parts[0]), float(parts[1]))
        if minutes > 59 or sec >= 60:
            raise YammerknitError("VTT timing component is out of range")
        return hours * 3600 + minutes * 60 + sec
    cues = []
    index = 1
    while index < len(lines):
        line = lines[index]
        if line.startswith(("NOTE", "STYLE", "REGION")):
            while index < len(lines) and lines[index].strip():
                index += 1
            continue
        if "-->" not in line:
            index += 1
            continue
        match = VTT_TIMING.fullmatch(line.strip().split(" align:")[0]) or re.fullmatch(VTT_TIMING.pattern + r"(?:[ \t]+[a-z]+:[^\n]+)?", line.strip())
        if not match:
            raise YammerknitError(f"Malformed VTT timing at line {index + 1}")
        start, end = match.group("start"), match.group("end")
        if seconds(end) <= seconds(start):
            raise YammerknitError("VTT cue end must follow its start")
        index += 1
        payload = []
        while index < len(lines) and lines[index].strip():
            if re.match(r"^\s*\d[\d:.]*\s*-->", lines[index]):
                raise YammerknitError(f"Missing blank separator before VTT cue at line {index + 1}; preserve the original and correct a separate copy.")
            value = re.sub(r"<v(?:\.[^ >]+)*[ \t]+([^>]+)>", lambda m: f"[{html.unescape(m.group(1))}] ", lines[index])
            # Language annotation can materially qualify a foreign-language quote.
            value = re.sub(r"<lang[ \t]+([^>]+)>", lambda m: f"[language={m.group(1)}] ", value)
            value = html.unescape(VTT_TAG.sub("", value))
            payload.append(re.sub(r"\s+", " ", value).strip())
            index += 1
        text = " ".join(p for p in payload if p)
        if text:
            cues.append(f"[{start} --> {end}] {text}")
        index += 1
    return "\n".join(cues) + ("\n" if cues else "")


def validate_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    allowed = {"youtu.be", "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
    query = parse_qs(parsed.query, keep_blank_values=True)
    if (parsed.scheme not in {"http", "https"} or host not in allowed or parsed.username is not None
            or parsed.password is not None or parsed.port is not None or "list" in query):
        raise YammerknitError("Expected one credential-free YouTube video URL, without playlist or port.")
    video_id = None
    if host == "youtu.be":
        video_id = parsed.path.removeprefix("/")
    elif parsed.path == "/watch" and len(query.get("v", [])) == 1:
        video_id = query["v"][0]
    elif re.fullmatch(r"/(?:shorts|embed|live)/[^/]+", parsed.path):
        video_id = parsed.path.rsplit("/", 1)[1]
    if not isinstance(video_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise YammerknitError("Expected a single video identity, not a channel or playlist URL.")
    return video_id


def yt_dlp_command(
    backend: str, url: str, stage: Path, languages: str
) -> list[str]:
    metadata_template = (
        "YAMMERKNIT_META\t%(id)s\t%(uploader)s\t%(upload_date)s\t"
        "%(title)s\t%(webpage_url)s"
    )
    return [
        backend,
        "--ignore-config",
        "--no-config-locations",
        "--no-plugin-dirs",
        "--no-remote-components",
        "--no-playlist",
        "--abort-on-error",
        "--skip-download",
        "--no-simulate",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        languages,
        "--sub-format",
        "vtt",
        "--no-overwrites",
        "--no-continue",
        "--no-write-info-json",
        "--no-write-comments",
        "--no-write-playlist-metafiles",
        "--no-cookies",
        "--no-cookies-from-browser",
        "--no-cache-dir",
        "--no-mark-watched",
        "--restrict-filenames",
        "--print",
        f"after_video:{metadata_template}",
        "--output",
        str(stage / "%(id)s.%(ext)s"),
        url,
    ]


def parse_acquisition_metadata(stdout: str) -> dict[str, str]:
    lines = [line for line in stdout.splitlines() if line.startswith("YAMMERKNIT_META\t")]
    if not lines:
        return {}
    parts = lines[-1].split("\t", 5)
    if len(parts) != 6:
        return {}
    _, video_id, uploader, upload_date, title, webpage_url = parts
    return {
        "video_id": video_id,
        "channel": uploader,
        "post_date": upload_date,
        "title": title,
        "url": webpage_url,
    }


def acquire_youtube(
    *,
    url: str,
    rights_basis: str | None,
    workspace: Path,
    languages: str,
    backend: str,
) -> dict[str, object]:
    video_id = validate_youtube_url(url)
    workspace = safe_path(workspace)
    if not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", languages):
        raise YammerknitError("Choose one exact subtitle language code, for example en or en-US.")

    resolved_backend = shutil.which(backend) if not Path(backend).is_file() else backend
    if not resolved_backend:
        raise YammerknitError(
            "yt-dlp is not available. Install it separately or supply transcript text."
        )

    staging_root = safe_path(workspace / ".staging")
    staging_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="youtube-", dir=staging_root))
    command = yt_dlp_command(str(resolved_backend), url, stage, languages)
    try:
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise YammerknitError(
                "Subtitle acquisition timed out after 180 seconds."
            ) from exc
        if completed.returncode != 0:
            raise YammerknitError(f"Subtitle acquisition failed with exit {completed.returncode}. Backend output is withheld because it may contain private data; supply transcript text or inspect the backend separately.")

        entries = list(stage.rglob("*"))
        for entry in entries:
            safe_path(entry)
        if any(path.suffix.lower() in MEDIA_EXTENSIONS for path in entries):
            raise YammerknitError("Acquisition boundary failed: audiovisual media appeared in staging.")
        metadata = parse_acquisition_metadata(completed.stdout)
        if metadata.get("video_id") != video_id or validate_youtube_url(metadata.get("url", "")) != video_id:
            raise YammerknitError("Acquisition metadata does not identify the requested video")
        subtitles = [path for path in entries if path.is_file() and path.suffix.lower() == ".vtt"]
        expected = stage / f"{video_id}.{languages}.vtt"
        if len(subtitles) != 1 or subtitles[0] != expected:
            raise YammerknitError("Expected one matching VTT for the requested video and language; none or ambiguous results. Supply a transcript instead.")
        raw_path = expected
        raw_bytes = raw_path.read_bytes()
        try:
            raw_text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise YammerknitError("Acquired subtitle file was not valid UTF-8.") from exc
        normalized = normalize_vtt_text(raw_text)
        if not normalized.strip():
            raise YammerknitError("The acquired VTT contained no usable transcript cues.")

        metadata = parse_acquisition_metadata(completed.stdout)
        result = create_source_record(
            workspace=workspace,
            original=raw_bytes,
            normalized=normalized,
            post_date=metadata.get("post_date") or "N/A",
            channel=metadata.get("channel") or "N/A",
            title=metadata.get("title") or "N/A",
            source_kind="youtube-subtitles",
            origin="YouTube",
            url=metadata.get("url") or url,
            acquisition_method="yt-dlp subtitle-only",
            rights_basis=rights_basis.strip() if rights_basis else None,
            original_filename=raw_path.name,
            transformations=[
                "Preserved acquired VTT bytes as source.original",
                "Rendered cue ranges, voice and language labels; retained repeated distinct cues",
                "Rendered timestamped UTF-8 text as source.txt",
            ],
            extra={
                "video_id": metadata.get("video_id"),
                "languages_requested": languages,
                "language_selected": languages,
                "subtitle_kind": "unknown: backend may supply manual or automatic captions",
                "subtitle_filename": raw_path.name,
                "backend": Path(str(resolved_backend)).name,
                "command_boundary": [
                    "--ignore-config",
                    "--no-plugin-dirs",
                    "--no-remote-components",
                    "--no-playlist",
                    "--skip-download",
                    "--write-subs",
                    "--write-auto-subs",
                    "--no-cookies",
                    "--no-cookies-from-browser",
                ],
            },
        )
        result["subtitle_file_selected"] = raw_path.name
        return result
    finally:
        shutil.rmtree(stage, ignore_errors=True)
        cleanup_empty_directory(staging_root)


def command_init_record(args: argparse.Namespace) -> dict[str, object]:
    source = safe_path(Path(args.source))
    original = source.read_bytes()
    normalized = decode_source(original).replace("\r\n", "\n").replace("\r", "\n")
    return create_source_record(
        workspace=safe_path(Path(args.workspace)),
        original=original,
        normalized=normalized,
        post_date=args.post_date,
        channel=args.channel,
        title=args.title,
        source_kind=args.source_kind,
        origin=args.origin,
        url=args.url,
        acquisition_method="user-supplied file",
        rights_basis=args.rights_basis,
        original_filename=source.name,
        transformations=[
            "Preserved supplied bytes as source.original",
            "Decoded UTF-8 and normalized line endings as source.txt",
        ],
    )


def command_validate(args: argparse.Namespace) -> dict[str, object]:
    receipt = validate_path(safe_path(Path(args.artifact)))
    if args.receipt:
        write_new_text(safe_path(Path(args.receipt)), dump_json(receipt))
    return receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preserve, validate, and organize Yammerknit records."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_record = subparsers.add_parser("init-record", help="Preserve a source record.")
    init_record.add_argument("--source", required=True)
    init_record.add_argument("--workspace", required=True)
    init_record.add_argument("--post-date", default="N/A")
    init_record.add_argument("--channel", default="N/A")
    init_record.add_argument("--title", default="N/A")
    init_record.add_argument("--source-kind", default="transcript")
    init_record.add_argument("--origin")
    init_record.add_argument("--url")
    init_record.add_argument("--rights-basis")
    init_record.set_defaults(handler=command_init_record)

    validate = subparsers.add_parser("validate", help="Validate Yammerknit structure.")
    validate.add_argument("--artifact", required=True)
    validate.add_argument("--receipt")
    validate.set_defaults(handler=command_validate)

    store = subparsers.add_parser("store-artifact", help="Store a validated artifact.")
    store.add_argument("--artifact", required=True)
    store.add_argument("--workspace", required=True)
    store.add_argument("--record-id", required=True)
    store.set_defaults(
        handler=lambda args: store_artifact(
            safe_path(Path(args.artifact)),
            safe_path(Path(args.workspace)),
            args.record_id,
            False,
        )
    )

    revise = subparsers.add_parser("revise-artifact", help="Store a new artifact revision.")
    revise.add_argument("--artifact", required=True)
    revise.add_argument("--workspace", required=True)
    revise.add_argument("--record-id", required=True)
    revise.set_defaults(
        handler=lambda args: store_artifact(
            safe_path(Path(args.artifact)),
            safe_path(Path(args.workspace)),
            args.record_id,
            True,
        )
    )

    inspect = subparsers.add_parser(
        "inspect-record", help="Report the current artifact and revision chain."
    )
    inspect.add_argument("--workspace", required=True)
    inspect.add_argument("--record-id", help="Omit to browse record titles and health.")
    inspect.set_defaults(
        handler=lambda args: inspect_record(
            safe_path(Path(args.workspace)), args.record_id
        )
    )

    normalize = subparsers.add_parser("normalize-vtt", help="Normalize a VTT transcript.")
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--output", required=True)
    normalize.set_defaults(
        handler=lambda args: _normalize_vtt_command(
            safe_path(Path(args.input)), safe_path(Path(args.output))
        )
    )

    acquire = subparsers.add_parser(
        "acquire-youtube", help="Acquire accessible YouTube subtitles only."
    )
    acquire.add_argument("--url", required=True)
    acquire.add_argument("--rights-basis")
    acquire.add_argument("--workspace", required=True)
    acquire.add_argument("--languages", default="en")
    acquire.add_argument("--yt-dlp", default="yt-dlp")
    acquire.set_defaults(
        handler=lambda args: acquire_youtube(
            url=args.url,
            rights_basis=args.rights_basis,
            workspace=safe_path(Path(args.workspace)),
            languages=args.languages,
            backend=args.yt_dlp,
        )
    )
    return parser


def _normalize_vtt_command(input_path: Path, output_path: Path) -> dict[str, object]:
    raw = input_path.read_text(encoding="utf-8-sig")
    normalized = normalize_vtt_text(raw)
    if not normalized:
        raise YammerknitError("The VTT contained no usable transcript cues.")
    write_new_text(output_path, normalized)
    return {
        "status": "normalized",
        "input": str(input_path),
        "output": str(output_path),
        "output_sha256": sha256_path(output_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except (YammerknitError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(dump_json({"status": "error", "error": str(exc)}), end="", file=sys.stderr)
        return 2
    print(dump_json(result), end="")
    if args.command == "validate" and not result["valid"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
