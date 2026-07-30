# Yammerknit data handling

Giles keeps five objects distinct:

1. **Original source** — the exact supplied or acquired bytes.
2. **Normalized source** — UTF-8 working text derived from the original.
3. **Artifact** — the Yammerknit produced from that source.
4. **Revision** — a new artifact version; never an overwrite.
5. **Receipt** — provenance, hashes, validation, and tool evidence.

## Default record layout

```text
<workspace>/
  sources/<record-id>/
    source.original.<extension>
    source.txt
    source-manifest.json
  artifacts/<record-id>/
    yammerknit.md
    artifact-manifest.json
    validation.json
  revisions/<record-id>/
    <revision-id>/
      yammerknit.md
      revision-manifest.json
      validation.json
```

Use a stable, length-bounded, Windows-safe `record-id` derived from date, channel, cleaned title, and a short source hash. Preserve a safe original extension while the manifest retains the supplied filename. Use UTC timestamps in receipts. Record the source kind, origin, URL when supplied, acquisition method, a rights or usage note when the user supplies one, original filename, relative file names, hashes, transformations, and tool version. Mark unknown fields `null` or `N/A`; do not infer them.

## Custody rules

- Preserve the original before normalization or analysis.
- Write new paths only. On collision, stop or create a distinct revision.
- Keep manifest links relative to the record so the workspace remains portable.
- Give each revision its own directory, validation receipt, and explicit parent.
- Use `inspect-record` to identify the current base or latest revision from immutable manifests.
- Keep temporary acquisition files in a staging directory until verified.
- Never store browser cookies, access tokens, passwords, or unrelated page data.
- Treat indexes, chunks, embeddings, and vector-store entries as replaceable derivatives. The source and governed artifact remain canonical.
- Do not claim backup, ingestion, publication, or deletion without a receipt from that operation.
- If a source is sensitive, minimize copies and keep manifests free of unnecessary personal data.

Before completion, a reader should be able to answer: What was the source? Where did it come from? What transformed it? Which artifact is current? What changed? Did validation pass?
