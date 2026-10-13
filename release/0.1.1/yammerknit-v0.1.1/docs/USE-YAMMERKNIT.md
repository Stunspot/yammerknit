# Create a thoughtbase and return to it

A Yammerknit is a modular mesh of reusable insight: meaning-nodes, relational bridges, sigil stacks, latent functions, echo shards and prompt seeds. It is built to help a later model think with the material. Its source locators and distinctions keep that intellectual work connected to where it began.

## First task

Start with [the complete cooling-pilot example](../codex-plugin/yammerknit/skills/yammerknit/examples/README.md). Read the source, then follow the thoughtbase's three connected mental moves. Try them on the invented service-team problem in the tutorial. A useful result notices changing context, repeated evidence and a changed applicability boundary, then turns those observations into a discriminating next inquiry.

For your own source, ask: “Build a Yammerknit thoughtbase from this material. Follow conceptual gravity, construct its keystone bridges and seed new reasoning for [my intended use].” You can leave the use broad. A document, narrative, poem or strategic discussion can carry valuable frames and tensions as well as factual claims. Supply the actual content when a URL cannot be read.

Expect the canonical codefenced artifact, from executive terrain through insight clusters, relational mesh, prompt seeds and sigil lexicon. Read what each cluster enables, then what its bridge changes. Ordered sigils carry defined relational and affective intent; ordinary language makes that intent inspectable. When carrying a cluster elsewhere, preserve those operative fields alongside its source and relevant limitations. Rich structure should arise from the material, not invented padding.

## Save and revise

Ask the agent to preserve the source and organize the artifact in a named workspace outside the installation. Python 3.10+ supports the deterministic helpers; the agent constructs the thoughtbase. From the complete skill folder:

```text
python scripts/yammerknit_tool.py init-record --source "SOURCE.txt" --workspace "WORKSPACE" --title "Source title"
python scripts/yammerknit_tool.py validate --artifact "DRAFT.md"
python scripts/yammerknit_tool.py store-artifact --artifact "DRAFT.md" --workspace "WORKSPACE" --record-id "RETURNED-ID"
```

The first command preserves source bytes and returns the record ID. The second reports structural consistency; review both source fidelity and whether the mesh enables useful new reasoning separately. The third saves a complete base record. To correct the artifact, work in a new draft and use `revise-artifact` with the same arguments; the base remains intact and the new manifest identifies its parent. A changed source requires a distinct source record.

## Browse and return without knowing a query

```text
python scripts/yammerknit_tool.py inspect-record --workspace "WORKSPACE"
```

Browse titles, channels, IDs, health and current artifact paths. A damaged record is shown as an error without hiding its healthy neighbors. Select an ID and add `--record-id "ID"` to inspect its chain before reopening the current artifact. This is a local record inventory, not a semantic search engine. Read cluster titles, follow bridge endpoints and use the lexicon to recover each sigil stack’s relational intent. Open the source locators when a transfer depends on the original conditions.

`current: null` means only a source exists. `verified-present-bytes` means the stored bytes and manifests agree. No helper status establishes semantic truth, signed authenticity, authorship or successful embedding. Copy the entire workspace to move it; inspection at the new path verifies its relative custody links. See [recovery](TROUBLESHOOTING.md) for a mismatch or ambiguous revision chain.

## Optional subtitles and later retrieval

Read [the subtitle guide](../codex-plugin/yammerknit/skills/yammerknit/references/youtube-transcripts.md) only when you need the optional YouTube route. For later chunking, use [the source-grounding practice](../codex-plugin/yammerknit/skills/yammerknit/references/source-grounding.md#reuse-a-cluster-alone). Keep the sigil stack, latent function, echo shard, relevant bridge and priming use with each chunk, along with plain-language terms, qualifiers and original provenance. The separate target system must perform and verify embedding, storage and retrieval. A static mesh cannot certify that those operations occurred or improved results.
