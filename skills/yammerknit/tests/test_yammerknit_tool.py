from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "yammerknit_tool.py"
SPEC = importlib.util.spec_from_file_location("yammerknit_tool", MODULE_PATH)
assert SPEC and SPEC.loader
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


def complete_yammerknit() -> str:
    return """```
# 2026-07-29 - Test Channel - Gravity Not Filing Cabinets

Post Date: 2026-07-29
Channel: Test Channel
Title: Gravity, Not Filing Cabinets
URL: https://example.test/source
Views: N/A
Desc: A compact verification fixture.

## Executive Insight Terrain

The source distinguishes semantic gravity from topical filing. Retrieval quality follows preserved conceptual relationships. A source remains evidence while its mesh remains an authored derivative. Sigils reinforce adjacency rather than replacing language. Bridges expose inference utility across clusters. The operational pivot is to preserve both custody and semantic reach.

Bridge Highlight: custody reinforces trustworthy reuse.
Bridge Highlight: semantic adjacency enables cross-topic recall.

## Insight Clusters

### Cluster 1: Semantic Gravity

Cluster Title: Semantic Gravity
Sigil Stack: ⟨🧠🕸️🧭⟩
Semantic Shard: Meaning clusters by relational pull rather than folder labels.
Timestamp / Anchor: [00:00:01.000]
Formatted Payload: Source → shard → bridge → retrieval.
Latent Function Summary: Reframes organization as semantic topology.
Cognitive Effect: Shifts attention from labels to relationships.
RAG Echo Shard: Retrieval improves when conceptual adjacency survives chunking.
Priming Worthiness: Seed for vector retrieval design.

### Cluster 2: Custody Before Derivation

Cluster Title: Custody Before Derivation
Sigil Glyph Stack: ⟨📚🔎🧾⟩
Semantic Shard: Derived intelligence remains trustworthy only while its source is traceable.
Timestamp/Anchor: [00:00:12.500]
Formatted Payload: Original ≠ normalized ≠ artifact ≠ index.
Latent Function Mapping: Separates evidence from replaceable retrieval derivatives.
Cognitive Effect: Makes provenance operational.
RAG Echo Shard: Canonical sources anchor regenerated embeddings and indexes.
Priming Worthiness: Seed for knowledge-base stewardship.

## Relational Mesh

Semantic Gravity ⇄ Custody Before Derivation
Bridge Type: Reinforce
Effect: Retrieval power remains accountable.
Strategic Value: Enables regeneration without losing authority.

## Prompt Seeding Kit

- Contrast semantic topology with folder taxonomy.
- Find bridges between source custody and vector retrieval.

## Sigil Lexicon

- ⟨🧠🕸️🧭⟩ — conceptual gravity across a navigable mesh.
- ⟨📚🔎🧾⟩ — source authority made inspectable.
```"""


class ValidationTests(unittest.TestCase):
    def test_complete_yammerknit_passes(self) -> None:
        receipt = tool.validate_text(complete_yammerknit())
        self.assertTrue(receipt["valid"], receipt["errors"])

    def test_numbered_cluster_headings_pass(self) -> None:
        artifact = complete_yammerknit().replace(
            "### Cluster 1: Semantic Gravity", "### 1. Semantic Gravity"
        ).replace(
            "### Cluster 2: Custody Before Derivation",
            "### 2. Custody Before Derivation",
        )
        receipt = tool.validate_text(artifact)
        self.assertTrue(receipt["valid"], receipt["errors"])

    def test_bold_fields_and_tables_pass(self) -> None:
        artifact = complete_yammerknit()
        for label in (
            "Sigil Stack",
            "Sigil Glyph Stack",
            "Semantic Shard",
            "Timestamp / Anchor",
            "Timestamp/Anchor",
            "Formatted Payload",
            "Latent Function Summary",
            "Latent Function Mapping",
            "RAG Echo Shard",
            "Priming Worthiness",
        ):
            artifact = artifact.replace(f"{label}:", f"**{label}:**")
        artifact = artifact.replace(
            "Bridge Highlight: custody reinforces trustworthy reuse.",
            "**Bridge Highlight — Custody:** custody reinforces trustworthy reuse.",
        ).replace(
            "Bridge Highlight: semantic adjacency enables cross-topic recall.",
            "**Bridge Highlight — Adjacency:** semantic adjacency enables cross-topic recall.",
        )
        relational = """| Source ⇄ Target | Bridge Type | Relationship Effect | Strategic Value |
|---|---|---|---|
| ⟨🧠🕸️🧭⟩ ⇄ ⟨📚🔎🧾⟩ | Reinforce | Custody preserves meaning | Enables repair |
"""
        artifact = artifact.replace(
            """Semantic Gravity ⇄ Custody Before Derivation
Bridge Type: Reinforce
Effect: Retrieval power remains accountable.
Strategic Value: Enables regeneration without losing authority.
""",
            relational,
        )
        lexicon = """| Sigil Stack | Latent Gravitational Intent | Cross-Transcript Recurrence |
|---|---|---|
| ⟨🧠🕸️🧭⟩ | conceptual gravity across a navigable mesh | N/A |
| ⟨📚🔎🧾⟩ | source authority made inspectable | N/A |
"""
        artifact = artifact.replace(
            """- ⟨🧠🕸️🧭⟩ — conceptual gravity across a navigable mesh.
- ⟨📚🔎🧾⟩ — source authority made inspectable.
""",
            lexicon,
        )
        receipt = tool.validate_text(artifact)
        self.assertTrue(receipt["valid"], receipt["errors"])

    def test_formatted_payload_may_be_a_following_block(self) -> None:
        artifact = complete_yammerknit().replace(
            "Formatted Payload: Source → shard → bridge → retrieval.",
            """**Formatted Payload:**

| Source | Derivative |
|---|---|
| Transcript | Yammerknit |""",
        ).replace(
            "Formatted Payload: Original ≠ normalized ≠ artifact ≠ index.",
            """**Formatted Payload:**

- Original
- Normalized
- Artifact
- Index""",
        )
        receipt = tool.validate_text(artifact)
        self.assertTrue(receipt["valid"], receipt["errors"])

    def test_empty_tables_do_not_satisfy_required_values(self) -> None:
        artifact = complete_yammerknit().replace(
            """Semantic Gravity ⇄ Custody Before Derivation
Bridge Type: Reinforce
Effect: Retrieval power remains accountable.
Strategic Value: Enables regeneration without losing authority.
""",
            """| Source ⇄ Target | Bridge Type | Strategic Value |
|---|---|---|
""",
        )
        receipt = tool.validate_text(artifact)
        self.assertFalse(receipt["valid"])
        self.assertIn("relational_mesh_has_bridge_type", receipt["errors"])
        self.assertIn("relational_mesh_has_strategic_value", receipt["errors"])

    def test_summary_shaped_output_is_rejected(self) -> None:
        receipt = tool.validate_text("This transcript is about semantic retrieval.")
        self.assertFalse(receipt["valid"])
        self.assertIn("codefenced_wrapper", receipt["errors"])
        self.assertIn("section_relational_mesh", receipt["errors"])

    def test_replacement_character_is_rejected(self) -> None:
        receipt = tool.validate_text(complete_yammerknit().replace("gravity", "grav\ufffdity", 1))
        self.assertFalse(receipt["valid"])
        self.assertIn("utf8_replacement_character_absent", receipt["errors"])

    def test_empty_scaffold_is_rejected(self) -> None:
        scaffold = """```
# 2026-07-29 - Channel - Title
Post Date:
Channel:
Title:
URL:
Views:
Desc:
## Executive Insight Terrain
## Insight Clusters
### Cluster 1
Cluster Title:
Sigil Stack:
Semantic Shard:
Timestamp / Anchor:
Formatted Payload:
Latent Function Summary:
RAG Echo Shard:
Priming Worthiness:
## Relational Mesh
## Prompt Seeding Kit
## Sigil Lexicon
```"""
        receipt = tool.validate_text(scaffold)
        self.assertFalse(receipt["valid"])
        self.assertIn("metadata_post_date", receipt["errors"])
        self.assertIn("at_least_two_clusters", receipt["errors"])
        self.assertIn(
            "executive_terrain_five_to_eight_sentences", receipt["errors"]
        )

    def test_windows_invalid_header_is_rejected(self) -> None:
        artifact = complete_yammerknit().replace(
            "# 2026-07-29 - Test Channel - Gravity Not Filing Cabinets",
            "# 2026-07-29 - Test Channel - Gravity: Not Filing Cabinets?",
        )
        receipt = tool.validate_text(artifact)
        self.assertFalse(receipt["valid"])
        self.assertIn("windows_safe_header", receipt["errors"])


class CustodyTests(unittest.TestCase):
    def test_source_artifact_and_revision_remain_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.txt"
            original = "Speaker: semantic gravity 🕸️\r\nSecond line.\r\n".encode("utf-8")
            source.write_bytes(original)

            record = tool.create_source_record(
                workspace=root / "estate",
                original=source.read_bytes(),
                normalized=tool.decode_source(original).replace("\r\n", "\n"),
                post_date="2026-07-29",
                channel="Test Channel",
                title="Custody Test",
                source_kind="transcript",
                origin="unit test",
                url=None,
                acquisition_method="user-supplied file",
                rights_basis=None,
                original_filename=source.name,
                transformations=["line-ending normalization"],
            )
            record_id = record["record_id"]
            source_dir = root / "estate" / "sources" / record_id
            source_manifest = json.loads(
                (source_dir / "source-manifest.json").read_text("utf-8")
            )
            original_path = source_dir / source_manifest["files"]["original"]
            self.assertEqual(original_path.name, "source.original.txt")
            self.assertEqual(original_path.read_bytes(), original)
            self.assertNotEqual(
                original_path.read_bytes(),
                (source_dir / "source.txt").read_bytes(),
            )

            artifact = root / "artifact.md"
            artifact.write_text(complete_yammerknit(), encoding="utf-8")
            supplied_artifact_bytes = artifact.read_bytes()
            stored = tool.store_artifact(artifact, root / "estate", record_id, False)
            stored_bytes = Path(stored["artifact"]).read_bytes()
            self.assertEqual(stored_bytes, supplied_artifact_bytes)
            artifact_manifest = json.loads(Path(stored["manifest"]).read_text("utf-8"))
            validation = json.loads(Path(stored["validation"]).read_text("utf-8"))
            self.assertFalse(Path(artifact_manifest["source_manifest"]).is_absolute())
            self.assertEqual(validation["artifact"], "yammerknit.md")
            self.assertEqual(
                validation["artifact_sha256"], tool.sha256_bytes(stored_bytes)
            )

            revised_text = complete_yammerknit().replace(
                "Retrieval power remains accountable.",
                "Retrieval power remains accountable and reproducible.",
            )
            revision = root / "revision.md"
            revision.write_text(revised_text, encoding="utf-8")
            revised = tool.store_artifact(revision, root / "estate", record_id, True)
            self.assertEqual(Path(stored["artifact"]).read_bytes(), stored_bytes)
            self.assertEqual(Path(revised["artifact"]).read_text(encoding="utf-8"), revised_text)
            revision_manifest = json.loads(
                Path(revised["manifest"]).read_text(encoding="utf-8")
            )
            self.assertEqual(revision_manifest["parent"]["kind"], "base")
            self.assertEqual(
                revision_manifest["parent"]["artifact_sha256"],
                tool.sha256_bytes(stored_bytes),
            )
            self.assertEqual(
                revision_manifest["artifact_sha256"],
                tool.sha256_path(Path(revised["artifact"])),
            )
            status = tool.inspect_record(root / "estate", record_id)
            self.assertEqual(status["current"]["kind"], "revision")
            self.assertEqual(
                status["current"]["revision_id"], revised["revision_id"]
            )

            self.assertEqual(
                source_manifest["hashes"]["source.original.txt"],
                tool.sha256_bytes(original),
            )

    def test_record_collision_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            kwargs = dict(
                workspace=root,
                original=b"same source",
                normalized="same source",
                post_date="2026-07-29",
                channel="Channel",
                title="Title",
                source_kind="transcript",
                origin=None,
                url=None,
                acquisition_method="test",
                rights_basis=None,
                original_filename="source.txt",
                transformations=[],
            )
            first = tool.create_source_record(**kwargs)
            source_dir = Path(first["source_directory"])
            manifest = json.loads(
                (source_dir / "source-manifest.json").read_text(encoding="utf-8")
            )
            original_path = source_dir / manifest["files"]["original"]
            before = original_path.read_bytes()
            with self.assertRaises(tool.YammerknitError):
                tool.create_source_record(**kwargs)
            self.assertEqual(original_path.read_bytes(), before)

    def test_vtt_normalization_preserves_unicode_and_timestamps(self) -> None:
        vtt = """WEBVTT

00:00:01.000 --> 00:00:03.000
<c>Gravity 🕸️ gathers meaning.</c>

00:00:03.500 --> 00:00:05.000
Gravity 🕸️ gathers meaning.

00:00:05.000 --> 00:00:08.000
Custody &amp; retrieval cooperate.
"""
        normalized = tool.normalize_vtt_text(vtt)
        self.assertEqual(
            normalized,
            "[00:00:01.000] Gravity 🕸️ gathers meaning.\n"
            "[00:00:05.000] Custody & retrieval cooperate.\n",
        )


if __name__ == "__main__":
    unittest.main()
