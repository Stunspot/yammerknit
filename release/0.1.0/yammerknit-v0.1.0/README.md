# Yammerknit

Yammerknit turns a transcript or document into a reusable semantic mesh for embedding and retrieval in a vector-RAG system. Rupert Giles governs source custody and document integrity; Sam Walker's canonical Yammerknit SOP governs the artifact itself.

This is the public, source-available repository for Yammerknit. [Read the complete documentation](https://stunspot.github.io/yammerknit/) or download the ready-to-use product as one file: [Yammerknit-v0.1.0.zip](https://github.com/Stunspot/yammerknit/raw/refs/heads/main/release/0.1.0/Yammerknit-v0.1.0.zip).

[![Yammerknit: turn source material into a retrieval-ready semantic mesh](https://stunspot.github.io/yammerknit/assets/yammerknit-sharecard.png)](https://stunspot.github.io/yammerknit/)

## What the customer kit contains

- `codex-plugin/yammerknit/` — the complete Codex plugin.
- `claude/yammerknit-v0.1.0.zip` — the upload-ready Claude skill.
- `docs/` — installation, use, data handling, recovery, and validation guidance.
- `assets/` — Stunspot identity artwork.
- `SHA256SUMS.txt` and `release-manifest.json` — package custody.

The kit contains both host distributions. The individual host packages are components, not separate Yammerknit products.

## What Yammerknit does

- Creates the canonical codefenced Yammerknit from supplied source material.
- Inspects, explains, and minimally repairs existing Yammerknits.
- Preserves source bytes, normalized text, artifacts, revisions, hashes, and provenance when the user chooses a workspace.
- Acquires publicly accessible YouTube subtitles when the optional `yt-dlp` dependency is available.
- Produces artifacts shaped for later vector embedding and semantic retrieval.

Yammerknit does not include a vector store, embedding model, or retrieval service. It does not claim that an artifact has been ingested when no vector system has performed that work.

## Source layout

- `skills/yammerknit/` — the self-contained runtime skill.
- `.codex-plugin/` and `assets/` — Codex plugin surfaces.
- `customer-docs/` — source for the packaged customer journey.
- `docs/` — the accessible public documentation site and sharecard.
- `verification/` — build and verification machinery.
- `release/0.1.0/` — the extracted customer kit and canonical customer ZIP.

## Build and verify

```text
python -X utf8 verification/build_release.py
python -X utf8 -m unittest discover -s skills/yammerknit/tests -v
python -X utf8 -m unittest verification/test_release.py -v
```

The repository and release are public. Marketplace submission and public announcements are separate launch actions and are not implied by repository publication.
