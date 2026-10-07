#!/usr/bin/env python3
"""Build the complete Yammerknit customer kit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import stat
import re
import tempfile
import zipfile
from pathlib import Path

VERSION = "0.1.0"
PRODUCT_ROOT = f"yammerknit-v{VERSION}"
CUSTOMER_ZIP = f"Yammerknit-v{VERSION}.zip"
CUSTOMER_SHA256 = f"Yammerknit-v{VERSION}.sha256"
CLAUDE_ZIP = f"yammerknit-v{VERSION}.zip"
FIXED_ZIP_TIME = (2026, 7, 30, 0, 0, 0)
RUNTIME_EXCLUDES = {"tests", "__pycache__"}

ROOT_DOCUMENTS = (
    "START-HERE.md",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "HOST-MATRIX.md",
    "LICENSE.md",
    "PRIVACY.md",
    "PROVENANCE.md",
    "SUPPORT.md",
    "TERMS.md",
)
PLUGIN_DOCUMENTS = (
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "PRIVACY.md",
    "SUPPORT.md",
    "TERMS.md",
)


def load_json(path: Path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    def reject(value):
        raise ValueError("Non-finite JSON number")
    def floating(value):
        number = float(value)
        return number if math.isfinite(number) else reject(value)
    return json.loads(safe_path(path).read_text("utf-8"), object_pairs_hook=pairs, parse_constant=reject, parse_float=floating)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_bytes(archive: zipfile.ZipFile, source: Path, archive_name: str) -> None:
    info = zipfile.ZipInfo(archive_name.replace("\\", "/"), FIXED_ZIP_TIME)
    info.create_system = 0
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0x20
    archive.writestr(info, source.read_bytes())


def safe_path(path: Path) -> Path:
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise RuntimeError(f"Linked/reparse input is unsupported: {part}")
    return path.resolve()


def portable_tree(root: Path) -> None:
    safe_path(root)
    seen = set()
    for directory, folders, files in os.walk(root, followlinks=False):
        for name in folders + files:
            target = Path(directory) / name
            safe_path(target)
            if (re.search(r'[<>:"/\\|?*\x00-\x1f]', name) or name.endswith((".", " "))
                    or name.split(".", 1)[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1,10)), *(f"LPT{i}" for i in range(1,10))}):
                raise RuntimeError(f"Nonportable source name: {name}")
            key = target.relative_to(root).as_posix().casefold()
            if key in seen:
                raise RuntimeError(f"Case-colliding source name: {key}")
            seen.add(key)


def files_beneath(root: Path) -> list[Path]:
    portable_tree(root)
    return sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.relative_to(root).as_posix().lower())


def source_inputs(repo: Path) -> list[Path]:
    inputs = [repo / name for name in ROOT_DOCUMENTS] + [repo / ".gitattributes"]
    for folder in ("skills", "assets", ".codex-plugin", "customer-docs"):
        inputs.extend(p for p in files_beneath(repo / folder) if "__pycache__" not in p.parts)
    inputs.extend(repo / "verification" / name for name in ("build_release.py", "audit_release.py"))
    for path in inputs:
        safe_path(path)
        if not path.is_file():
            raise RuntimeError(f"Required source input missing: {path}")
    return sorted(set(inputs), key=lambda p: p.relative_to(repo).as_posix())


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in files_beneath(root):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(path)))
        digest.update(b"\n")
    return digest.hexdigest()


def runtime_files(skill_root: Path, *, include_openai_agent: bool) -> list[Path]:
    files: list[Path] = []
    for path in skill_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_root)
        if any(part in RUNTIME_EXCLUDES for part in relative.parts):
            continue
        if not include_openai_agent and relative.parts[:1] == ("agents",):
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.as_posix().lower())


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def build_codex_plugin(repo: Path, destination: Path) -> None:
    copy_file(
        repo / ".codex-plugin" / "plugin.json",
        destination / ".codex-plugin" / "plugin.json",
    )
    for name in ("icon.png", "Stunspot Icon.ico", "yammerknit-readme-hero.png"):
        copy_file(repo / "assets" / name, destination / "assets" / name)
    for name in PLUGIN_DOCUMENTS:
        copy_file(repo / name, destination / name)

    skill_root = repo / "skills" / "yammerknit"
    for path in runtime_files(skill_root, include_openai_agent=True):
        copy_file(
            path,
            destination / "skills" / "yammerknit" / path.relative_to(skill_root),
        )


def build_claude_skill(repo: Path, destination: Path) -> None:
    skill_root = repo / "skills" / "yammerknit"
    entries = [
        (path, f"yammerknit/{path.relative_to(skill_root).as_posix()}")
        for path in runtime_files(skill_root, include_openai_agent=False)
    ]
    with zipfile.ZipFile(destination, "w") as archive:
        for source, name in sorted(entries, key=lambda item: item[1].lower()):
            zip_bytes(archive, source, name)


def build_release_manifest(customer_root: Path) -> dict[str, object]:
    manifest_path = customer_root / "release-manifest.json"
    files = [
        {
            "path": path.relative_to(customer_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files_beneath(customer_root)
        if path != manifest_path
    ]
    codex_root = customer_root / "codex-plugin" / "yammerknit"
    claude_zip = customer_root / "claude" / CLAUDE_ZIP
    return {
        "schema": "yammerknit.customer-release.v1",
        "product": "Yammerknit",
        "version": VERSION,
        "visibility": "public",
        "public_submission": False,
        "customer_object": CUSTOMER_ZIP,
        "top_level_directory": PRODUCT_ROOT,
        "distributions": {
            "codex_plugin": {
                "path": "codex-plugin/yammerknit",
                "file_count": len(files_beneath(codex_root)),
                "tree_sha256": tree_digest(codex_root),
            },
            "claude_skill": {
                "path": f"claude/{CLAUDE_ZIP}",
                "bytes": claude_zip.stat().st_size,
                "sha256": sha256(claude_zip),
            },
        },
        "files": files,
    }


def build_customer_tree(repo: Path, customer_root: Path) -> dict[str, object]:
    for name in ROOT_DOCUMENTS:
        if name == "START-HERE.md":
            start_here = (repo / name).read_text(encoding="utf-8")
            (customer_root / name).write_text(
                start_here.replace("customer-docs/", "docs/").replace("(skills/", "(codex-plugin/yammerknit/skills/"),
                encoding="utf-8",
                newline="\n",
            )
        else:
            copy_file(repo / name, customer_root / name)
    for path in files_beneath(repo / "customer-docs"):
        destination = customer_root / "docs" / path.relative_to(repo / "customer-docs")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(path.read_text("utf-8").replace("../skills/", "../codex-plugin/yammerknit/skills/"), encoding="utf-8", newline="\n")
    for name in ("icon.png", "Stunspot Icon.ico", "yammerknit-readme-hero.png"):
        copy_file(repo / "assets" / name, customer_root / "assets" / name)

    build_codex_plugin(repo, customer_root / "codex-plugin" / "yammerknit")
    claude_dir = customer_root / "claude"
    claude_dir.mkdir(parents=True)
    build_claude_skill(repo, claude_dir / CLAUDE_ZIP)

    # Include the exact bounded build closure, not local archives or user workspaces.
    for source in source_inputs(repo):
        copy_file(source, customer_root / "source" / source.relative_to(repo))
    marketplace = {"name": "yammerknit-local", "interface": {"displayName": "Yammerknit Local"},
                   "plugins": [{"name": "yammerknit", "source": {"source": "local", "path": "./codex-plugin/yammerknit"},
                                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}]}
    market_path = customer_root / ".agents/plugins/marketplace.json"
    market_path.parent.mkdir(parents=True)
    market_path.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8", newline="\n")

    checksum_text = (
        f"{sha256(claude_dir / CLAUDE_ZIP)}  claude/{CLAUDE_ZIP}\n"
        f"{tree_digest(customer_root / 'codex-plugin' / 'yammerknit')}"
        "  codex-plugin/yammerknit/\n"
    )
    (customer_root / "SHA256SUMS.txt").write_text(
        checksum_text, encoding="utf-8", newline="\n"
    )
    manifest = build_release_manifest(customer_root)
    (customer_root / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def archive_customer_tree(customer_root: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w") as archive:
        for path in files_beneath(customer_root):
            name = f"{customer_root.name}/{path.relative_to(customer_root).as_posix()}"
            zip_bytes(archive, path, name)


def build(repo: Path, output_dir: Path) -> dict[str, object]:
    repo, output_dir = safe_path(repo), safe_path(output_dir)
    source_inputs(repo)  # Reject links and nonportable names before any output publication.
    plugin_manifest = load_json(repo / ".codex-plugin/plugin.json")
    if not isinstance(plugin_manifest, dict) or plugin_manifest.get("version") != VERSION:
        raise RuntimeError("Plugin and builder versions differ")
    if output_dir.exists():
        raise RuntimeError("Choose a new output directory; existing output is preserved")
    if output_dir == repo or repo in output_dir.parents and output_dir.parts[len(repo.parts):len(repo.parts)+1] in [("skills",), ("customer-docs",), ("assets",), (".codex-plugin",)]:
        raise RuntimeError("Output must not be inside a build input tree")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="yammerknit-build-", dir=output_dir.parent) as temp:
        publish = Path(temp) / "bundle"
        publish.mkdir()
        customer_root = publish / PRODUCT_ROOT
        customer_root.mkdir()
        manifest = build_customer_tree(repo, customer_root)
        archive = publish / CUSTOMER_ZIP
        archive_customer_tree(customer_root, archive)
        customer_sha = sha256(archive)
        (publish / CUSTOMER_SHA256).write_text(f"{customer_sha}  {CUSTOMER_ZIP}\n", encoding="utf-8", newline="\n")
        if output_dir.exists():
            raise RuntimeError("Destination appeared during build; refusing overwrite")
        os.rename(publish, output_dir)
    final_root, final_zip = output_dir / PRODUCT_ROOT, output_dir / CUSTOMER_ZIP
    return {"schema": "yammerknit.public-release.v2", "version": VERSION, "visibility": "public",
            "customer_zip": str(final_zip), "customer_zip_sha256": customer_sha,
            "customer_root": str(final_root), "customer_tree_sha256": tree_digest(final_root),
            "customer_file_count": len(files_beneath(final_root)), "manifest": manifest}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory; never replaces an existing release.")
    args = parser.parse_args()
    repo = safe_path(args.repo)
    output = (
        safe_path(args.output_dir)
        if args.output_dir
        else repo / "release" / VERSION
    )
    try:
        result = build(repo, output)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"Build failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
