#!/usr/bin/env python3
"""Deterministic custody, validation, and subtitle helpers for Yammerknits."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

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
    source_hash = sha256_bytes(original)
    record_id = make_record_id(post_date, channel, title, source_hash)
    ensure_record_absent(workspace, record_id)

    final_dir = workspace / "sources" / record_id
    staging_root = workspace / ".staging"
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
    checks: dict[str, bool] = {}
    errors: list[str] = []
    stripped = text.strip()

    checks["utf8_replacement_character_absent"] = "\ufffd" not in text
    checks["codefenced_wrapper"] = stripped.startswith("```") and stripped.endswith("```")
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
    checks["at_least_two_clusters"] = len(cluster_starts) >= 2

    cluster_blocks: list[str] = []
    for index, start in enumerate(cluster_starts):
        end = cluster_starts[index + 1].start() if index + 1 < len(cluster_starts) else len(cluster_area)
        cluster_blocks.append(cluster_area[start.start() : end])

    for field_name, pattern in CLUSTER_FIELDS.items():
        if field_name == "cluster_title":
            present = bool(cluster_blocks)
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
    checks["executive_terrain_five_to_eight_sentences"] = 5 <= sentence_count <= 8
    checks["executive_terrain_two_to_three_bridge_highlights"] = (
        2 <= bridge_highlights <= 3
    )

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

    for name, passed in checks.items():
        if not passed:
            errors.append(name)

    encoded = text.encode("utf-8")
    return {
        "schema": "yammerknit.validation.v1",
        "tool": {"name": "yammerknit_tool", "version": TOOL_VERSION},
        "checked_at": utc_now(),
        "artifact": artifact_path,
        "artifact_sha256": artifact_sha256 or sha256_bytes(encoded),
        "valid": not errors,
        "checks": checks,
        "errors": errors,
    }


def validate_path(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
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


def revision_manifests(workspace: Path, record_id: str) -> list[dict[str, object]]:
    root = workspace / "revisions" / record_id
    manifests: list[dict[str, object]] = []
    for path in sorted(root.glob("*/revision-manifest.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        value["_manifest_path"] = path
        manifests.append(value)
    return sorted(
        manifests,
        key=lambda value: (str(value.get("created_at", "")), str(value.get("revision_id", ""))),
    )


def inspect_record(workspace: Path, record_id: str) -> dict[str, object]:
    source_manifest = workspace / "sources" / record_id / "source-manifest.json"
    base_artifact = workspace / "artifacts" / record_id / "yammerknit.md"
    base_manifest = workspace / "artifacts" / record_id / "artifact-manifest.json"
    if not source_manifest.is_file():
        raise YammerknitError(f"Source record does not exist: {source_manifest}")
    revisions = revision_manifests(workspace, record_id)
    if revisions:
        latest = revisions[-1]
        latest_path = Path(latest["_manifest_path"]).parent / "yammerknit.md"
        current = {
            "kind": "revision",
            "revision_id": latest["revision_id"],
            "artifact": str(latest_path),
            "artifact_sha256": latest["artifact_sha256"],
        }
    elif base_artifact.is_file() and base_manifest.is_file():
        current = {
            "kind": "base",
            "artifact": str(base_artifact),
            "artifact_sha256": sha256_path(base_artifact),
        }
    else:
        current = None
    return {
        "schema": "yammerknit.record-status.v1",
        "record_id": record_id,
        "source_manifest": str(source_manifest),
        "base_artifact_present": base_artifact.is_file(),
        "revision_count": len(revisions),
        "current": current,
    }


def store_artifact(
    artifact: Path, workspace: Path, record_id: str, revision: bool
) -> dict[str, object]:
    source_manifest = workspace / "sources" / record_id / "source-manifest.json"
    if not source_manifest.is_file():
        raise YammerknitError(f"Source record does not exist: {source_manifest}")

    receipt = validate_path(artifact)
    if not receipt["valid"]:
        raise YammerknitError(
            "Artifact failed structural validation: " + ", ".join(receipt["errors"])
        )

    artifact_bytes = artifact.read_bytes()
    if revision:
        base_artifact = workspace / "artifacts" / record_id / "yammerknit.md"
        if not base_artifact.is_file():
            raise YammerknitError("Cannot create a revision before the base artifact exists.")
        previous = revision_manifests(workspace, record_id)
        if previous:
            parent = {
                "kind": "revision",
                "revision_id": previous[-1]["revision_id"],
                "artifact_sha256": previous[-1]["artifact_sha256"],
            }
        else:
            parent = {
                "kind": "base",
                "artifact_sha256": sha256_path(base_artifact),
            }
        revision_id = (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + sha256_bytes(artifact_bytes)[:10]
        )
        target_dir = workspace / "revisions" / record_id / revision_id
        if target_dir.exists():
            raise YammerknitError(f"Refusing to overwrite existing path: {target_dir}")
        staging_root = workspace / ".staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix="revision-", dir=staging_root))
        staged_revision = stage / revision_id
        staged_revision.mkdir()
        try:
            target = staged_revision / "yammerknit.md"
            target.write_bytes(artifact_bytes)
            receipt["artifact"] = "yammerknit.md"
            (staged_revision / "validation.json").write_text(
                dump_json(receipt), encoding="utf-8", newline="\n"
            )
            revision_manifest = {
                "schema": "yammerknit.revision-manifest.v1",
                "record_id": record_id,
                "revision_id": revision_id,
                "created_at": utc_now(),
                "artifact_sha256": sha256_bytes(artifact_bytes),
                "artifact": "yammerknit.md",
                "validation_receipt": "validation.json",
                "parent": parent,
                "tool": {"name": "yammerknit_tool", "version": TOOL_VERSION},
            }
            (staged_revision / "revision-manifest.json").write_text(
                dump_json(revision_manifest), encoding="utf-8", newline="\n"
            )
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_revision, target_dir)
        finally:
            shutil.rmtree(stage, ignore_errors=True)
            cleanup_empty_directory(staging_root)
        return {
            "status": "revision-created",
            "record_id": record_id,
            "revision_id": revision_id,
            "artifact": str(target_dir / "yammerknit.md"),
            "manifest": str(target_dir / "revision-manifest.json"),
            "validation": str(target_dir / "validation.json"),
        }

    target_dir = workspace / "artifacts" / record_id
    if target_dir.exists():
        raise YammerknitError(f"Refusing to overwrite existing path: {target_dir}")
    target_dir.mkdir(parents=True)
    try:
        target = target_dir / "yammerknit.md"
        target.write_bytes(artifact_bytes)
        receipt["artifact"] = "yammerknit.md"
        receipt_path = target_dir / "validation.json"
        receipt_path.write_text(dump_json(receipt), encoding="utf-8", newline="\n")
        artifact_manifest = {
            "schema": "yammerknit.artifact-manifest.v1",
            "record_id": record_id,
            "created_at": utc_now(),
            "source_manifest": (
                Path("..") / ".." / "sources" / record_id / "source-manifest.json"
            ).as_posix(),
            "artifact_sha256": sha256_bytes(artifact_bytes),
            "artifact": "yammerknit.md",
            "validation_receipt": "validation.json",
            "tool": {"name": "yammerknit_tool", "version": TOOL_VERSION},
        }
        (target_dir / "artifact-manifest.json").write_text(
            dump_json(artifact_manifest), encoding="utf-8", newline="\n"
        )
    except Exception:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise

    return {
        "status": "artifact-created",
        "record_id": record_id,
        "artifact": str(target_dir / "yammerknit.md"),
        "manifest": str(target_dir / "artifact-manifest.json"),
        "validation": str(target_dir / "validation.json"),
    }


def normalize_vtt_text(vtt: str) -> str:
    lines = vtt.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cues: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        match = VTT_TIMING.search(lines[index])
        if not match:
            index += 1
            continue
        start = match.group("start")
        index += 1
        payload: list[str] = []
        while index < len(lines) and lines[index].strip():
            cleaned = html.unescape(VTT_TAG.sub("", lines[index]))
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned:
                payload.append(cleaned)
            index += 1
        text = re.sub(r"\s+", " ", " ".join(payload)).strip()
        if text and (not cues or cues[-1][1] != text):
            cues.append((start, text))
        index += 1
    return "\n".join(f"[{start}] {text}" for start, text in cues) + ("\n" if cues else "")


def validate_youtube_url(url: str) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    allowed = {
        "youtu.be",
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    }
    if parsed.scheme not in {"http", "https"} or host not in allowed:
        raise YammerknitError("Expected one http(s) YouTube video URL.")


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
    validate_youtube_url(url)
    if not languages.strip():
        raise YammerknitError("At least one subtitle language is required.")

    resolved_backend = shutil.which(backend) if not Path(backend).is_file() else backend
    if not resolved_backend:
        raise YammerknitError(
            "yt-dlp is not available. Install it separately or supply transcript text."
        )

    staging_root = workspace / ".staging"
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
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise YammerknitError(
                f"Subtitle acquisition failed with exit {completed.returncode}: {detail[-1200:]}"
            )

        unexpected_media = [
            str(path) for path in stage.iterdir() if path.suffix.lower() in MEDIA_EXTENSIONS
        ]
        if unexpected_media:
            raise YammerknitError(
                "Acquisition boundary failed: audiovisual media appeared in staging."
            )
        subtitles = sorted(stage.glob("*.vtt"), key=lambda path: (len(path.name), path.name))
        if not subtitles:
            raise YammerknitError(
                "No VTT subtitles were available. Supply transcript text instead."
            )

        raw_path = subtitles[0]
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
                "Removed VTT markup and consecutive duplicate cues",
                "Rendered timestamped UTF-8 text as source.txt",
            ],
            extra={
                "video_id": metadata.get("video_id"),
                "languages_requested": languages,
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
    source = Path(args.source).resolve()
    original = source.read_bytes()
    normalized = decode_source(original).replace("\r\n", "\n").replace("\r", "\n")
    return create_source_record(
        workspace=Path(args.workspace).resolve(),
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
    receipt = validate_path(Path(args.artifact).resolve())
    if args.receipt:
        write_new_text(Path(args.receipt).resolve(), dump_json(receipt))
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
            Path(args.artifact).resolve(),
            Path(args.workspace).resolve(),
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
            Path(args.artifact).resolve(),
            Path(args.workspace).resolve(),
            args.record_id,
            True,
        )
    )

    inspect = subparsers.add_parser(
        "inspect-record", help="Report the current artifact and revision chain."
    )
    inspect.add_argument("--workspace", required=True)
    inspect.add_argument("--record-id", required=True)
    inspect.set_defaults(
        handler=lambda args: inspect_record(
            Path(args.workspace).resolve(), args.record_id
        )
    )

    normalize = subparsers.add_parser("normalize-vtt", help="Normalize a VTT transcript.")
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--output", required=True)
    normalize.set_defaults(
        handler=lambda args: _normalize_vtt_command(
            Path(args.input).resolve(), Path(args.output).resolve()
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
            workspace=Path(args.workspace).resolve(),
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
