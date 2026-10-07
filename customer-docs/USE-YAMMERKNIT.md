# Create a useful Yammerknit and return to it

A Yammerknit is an authored map of a source's claims and relationships. It helps you reuse meaning while keeping the evidence close. Its structured form does not establish that a claim is true or that a model will retrieve it better.

## First task

Start with [the complete cooling-pilot example](../skills/yammerknit/examples/README.md). It includes the actual fictional source, full artifact, a reusable chunk and exact native commands. Compare the source's “observed reduction with confounders” with the tempting but unsupported “the checklist caused a 20% reduction.” The distinction is the point of the exercise.

For your own source, supply the document or transcript and ask: “Create a Yammerknit for later use in answering [my question]. Preserve qualifiers, exceptions and source locators, and label inferences and proposed transfers.” You can leave the question broad; the agent should inspect the available material before asking for more. A link it cannot read needs actual content before extraction.

Expect metadata, executive insight terrain, clusters, relationships, prompt seeds and a defined sigil lexicon. Read the ordinary-language claim in each cluster. Its limitation must travel with it when copied alone. Unknown facts stay unknown; a short source does not need invented complexity to fill a format.

## Save and revise

Ask the agent to preserve the source and organize the artifact in a named workspace outside the installation. Python 3.10+ supports the deterministic helpers; the agent performs semantic extraction. From the complete skill folder:

```text
python scripts/yammerknit_tool.py init-record --source "SOURCE.txt" --workspace "WORKSPACE" --title "Source title"
python scripts/yammerknit_tool.py validate --artifact "DRAFT.md"
python scripts/yammerknit_tool.py store-artifact --artifact "DRAFT.md" --workspace "WORKSPACE" --record-id "RETURNED-ID"
```

The first command preserves source bytes and returns the record ID. The second reports structural consistency; review the source claims separately. The third saves a complete base record. To correct the artifact, work in a new draft and use `revise-artifact` with the same arguments; the base remains intact and the new manifest identifies its parent. A changed source requires a distinct source record.

## Browse and return without knowing a query

```text
python scripts/yammerknit_tool.py inspect-record --workspace "WORKSPACE"
```

Browse titles, channels, IDs, health and current artifact paths. A damaged record is shown as an error without hiding its healthy neighbors. Select an ID and add `--record-id "ID"` to inspect its chain before reopening the current artifact. This is a local record inventory, not a semantic search engine. Read cluster titles and follow source locators to explore within an artifact; sigils are memory aids, not secret navigation keys.

`current: null` means only a source exists. `verified-present-bytes` means the stored bytes and manifests agree. No helper status establishes semantic truth, signed authenticity, authorship or successful embedding. Copy the entire workspace to move it; inspection at the new path verifies its relative custody links. See [recovery](TROUBLESHOOTING.md) for a mismatch or ambiguous revision chain.

## Optional subtitles and later retrieval

Read [the subtitle guide](../skills/yammerknit/references/youtube-transcripts.md) only when you need the optional YouTube route. For later chunking, use [the source-grounding practice](../skills/yammerknit/references/source-grounding.md#reuse-a-cluster-alone). Keep plain-language terms, qualifiers and original provenance with each chunk. The separate target system must perform and verify embedding, storage and retrieval. A static mesh cannot certify that those operations occurred or improved results.
