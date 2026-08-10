from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILD_PATH = Path(__file__).with_name("build_release.py")
SPEC = importlib.util.spec_from_file_location("build_release", BUILD_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)

EXPECTED = {
    "canonical-sop.md": "3b35a55f35aedc848ea83425b5feacd6994059fd497103cae135ae826d5504dd",
    "canonical-rupert-giles-document-guardian.txt": "ed6eeb11f4602954506b26089d23c5da466f28d32a4ea2d2f3fdb69033033b41",
    "icon.png": "fdedf2607c31ceb380c77bf0fd54bd964358216e08991a71ed61d161ef875351",
    "Stunspot Icon.ico": "77b2ea3c2f18676867ac48bd048bed3bbb9ddad13c92c000493b1e1c37c598e1",
}


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive_names(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        return set(archive.namelist())


class CanonicalCustodyTests(unittest.TestCase):
    def test_canonical_hashes(self) -> None:
        paths = {
            "canonical-sop.md": REPO / "skills/yammerknit/references/canonical-sop.md",
            "canonical-rupert-giles-document-guardian.txt": REPO
            / "skills/yammerknit/personas/canonical-rupert-giles-document-guardian.txt",
            "icon.png": REPO / "assets/icon.png",
            "Stunspot Icon.ico": REPO / "assets/Stunspot Icon.ico",
        }
        for name, path in paths.items():
            with self.subTest(name=name):
                self.assertEqual(hash_bytes(path.read_bytes()), EXPECTED[name])

    def test_vector_rag_claim_is_literal(self) -> None:
        skill = (REPO / "skills/yammerknit/SKILL.md").read_text("utf-8")
        self.assertIn("vector-RAG system", skill)
        self.assertIn("does not itself provide a vector store", skill)
        self.assertNotIn("FTS is RAG", skill)
        self.assertNotIn("lexical RAG", skill)


class PackageTests(unittest.TestCase):
    def test_one_customer_kit_contains_both_host_distributions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "release"
            result = builder.build(REPO, output)
            customer_zip = output / builder.CUSTOMER_ZIP
            customer_root = output / builder.PRODUCT_ROOT
            sha_file = output / builder.CUSTOMER_SHA256

            self.assertEqual(
                sorted(path.name for path in output.iterdir()),
                sorted(
                    [
                        builder.CUSTOMER_ZIP,
                        builder.CUSTOMER_SHA256,
                        builder.PRODUCT_ROOT,
                    ]
                ),
            )
            self.assertEqual(result["visibility"], "public")
            self.assertEqual(
                sha_file.read_text("utf-8").split()[0],
                hash_bytes(customer_zip.read_bytes()),
            )

            with zipfile.ZipFile(customer_zip) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                roots = {name.split("/", 1)[0] for name in names}
                self.assertEqual(roots, {builder.PRODUCT_ROOT})
                for info in archive.infolist():
                    self.assertEqual(info.create_system, 0)
                    self.assertFalse(info.flag_bits & 0x1)

            expected_surfaces = {
                "START-HERE.md",
                "README.md",
                "CHANGELOG.md",
                "HOST-MATRIX.md",
                "LICENSE.md",
                "PRIVACY.md",
                "PROVENANCE.md",
                "SUPPORT.md",
                "TERMS.md",
                "SHA256SUMS.txt",
                "release-manifest.json",
                "codex-plugin/yammerknit/.codex-plugin/plugin.json",
                "codex-plugin/yammerknit/skills/yammerknit/SKILL.md",
                f"claude/{builder.CLAUDE_ZIP}",
                "docs/INSTALLATION.md",
                "docs/USE-YAMMERKNIT.md",
                "docs/DATA-AND-PRIVACY.md",
                "docs/TROUBLESHOOTING.md",
                "docs/VALIDATION-AND-LIMITS.md",
            }
            observed = {
                path.relative_to(customer_root).as_posix()
                for path in customer_root.rglob("*")
                if path.is_file()
            }
            self.assertTrue(expected_surfaces <= observed)
            self.assertFalse(any("member-kit" in path for path in observed))
            self.assertFalse(any("plugin-0.1.0.zip" in path for path in observed))
            self.assertFalse(any("claude-skill" in path for path in observed))

            claude_zip = customer_root / "claude" / builder.CLAUDE_ZIP
            with zipfile.ZipFile(claude_zip) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                self.assertEqual({name.split("/", 1)[0] for name in names}, {"yammerknit"})
                self.assertIn("yammerknit/SKILL.md", names)
                self.assertNotIn("yammerknit/agents/openai.yaml", names)
                self.assertFalse(any("/tests/" in name for name in names))
                for info in archive.infolist():
                    self.assertEqual(info.create_system, 0)

            plugin_skill = customer_root / "codex-plugin/yammerknit/skills/yammerknit"
            with zipfile.ZipFile(claude_zip) as archive:
                for path in builder.runtime_files(
                    REPO / "skills" / "yammerknit", include_openai_agent=False
                ):
                    relative = path.relative_to(REPO / "skills" / "yammerknit")
                    self.assertEqual(
                        (plugin_skill / relative).read_bytes(),
                        archive.read(f"yammerknit/{relative.as_posix()}"),
                    )

            self.assertEqual(
                hash_bytes(
                    (
                        plugin_skill / "references" / "canonical-sop.md"
                    ).read_bytes()
                ),
                EXPECTED["canonical-sop.md"],
            )
            self.assertEqual(
                hash_bytes(
                    (
                        plugin_skill
                        / "personas"
                        / "canonical-rupert-giles-document-guardian.txt"
                    ).read_bytes()
                ),
                EXPECTED["canonical-rupert-giles-document-guardian.txt"],
            )

            manifest = json.loads(
                (customer_root / "release-manifest.json").read_text("utf-8")
            )
            declared = {item["path"]: item for item in manifest["files"]}
            actual_without_manifest = {
                path.relative_to(customer_root).as_posix(): path
                for path in customer_root.rglob("*")
                if path.is_file() and path.name != "release-manifest.json"
            }
            self.assertEqual(set(declared), set(actual_without_manifest))
            for relative, path in actual_without_manifest.items():
                self.assertEqual(declared[relative]["sha256"], hash_bytes(path.read_bytes()))

            for path in customer_root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".md", ".json", ".yaml", ".txt"}:
                    text = path.read_text("utf-8")
                    self.assertNotRegex(text, r"[A-Za-z]:\\Users\\")

    def test_customer_document_links_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "release"
            builder.build(REPO, output)
            root = output / builder.PRODUCT_ROOT
            link_pattern = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)#]+)(?:#[^)]+)?\)")
            failures: list[str] = []
            for page in root.rglob("*.md"):
                text = page.read_text("utf-8")
                for target in link_pattern.findall(text):
                    resolved = (page.parent / target).resolve()
                    if not resolved.exists():
                        failures.append(f"{page.relative_to(root)} -> {target}")
            self.assertEqual(failures, [])

    def test_release_builder_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "release"
            builder.build(REPO, output)
            with self.assertRaises(RuntimeError):
                builder.build(REPO, output)


if __name__ == "__main__":
    unittest.main()
