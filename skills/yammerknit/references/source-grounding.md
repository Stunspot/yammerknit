# Source-grounded extraction practice

## Preserve the claim's warrant

Read enough surrounding material to understand what the source actually asserts. Map the important claims to paragraphs, page numbers, section names or cue ranges. Preserve the source's units, population, denominator, date, negation, exceptions and uncertainty wherever removing one would change an answer. Distinguish missing information from evidence of absence. Report the source's claim as a claim when its truth has not been independently checked.

Mark exact quotations as quotations and reproduce them faithfully. Paraphrase with the same scope. Label deductions as analyst inference and applications to a new domain as proposed transfer. A source's rhetorical flourish can be useful texture without becoming a scientific fact. Transcript-only input cannot establish unseen graphs, demonstrations, facial expressions or slide text. If an important pronoun or visual reference remains unresolved, keep the gap explicit instead of reconstructing the missing scene.

Consolidate genuine repetition while retaining distinct speakers, disagreements and changes over time. Two clips, transcripts or articles quoting the same origin provide multiple representations of one source, not independent corroboration. Preserve a separate source identity for genuinely different origins and connect them with a labeled agreement or conflict rather than merging their authority.

## Make relationships earn their place

Name each endpoint using an existing cluster title or its defined sigil. Give the bridge a type, effect and strategic value. “Both mention learning” is a topical adjacency; it does not demonstrate a causal or explanatory relationship. Use contrast when the limits of one claim constrain the other. Label a speculative bridge proposed and say what evidence would test it. A one-cluster source may state “No supported bridge” with a reason.

Sigils are optional mnemonic scaffolding in use, though the canonical artifact format includes them. Define each used stack in plain language; keep meaningful titles and terms searchable without remembering the symbols. Latent Function and RAG Echo describe an intended use of the representation, not a measured effect in a model. Keep the whole artifact readable if every emoji is ignored.

## Reuse a cluster alone

Before handing a cluster to a later chunking or embedding pipeline, read it without the executive section. Can a reader identify the subject, what is claimed, for whom/when, the qualification, its origin and where to verify it? If not, carry the missing context into that unit. Use this compact envelope, adapting rather than mechanically filling unrelated fields:

```text
Title and ordinary retrieval terms:
Claim, with scope and qualifier:
Origin: source quotation / source paraphrase / analyst inference / proposed transfer
Source: title or record ID; original hash if actually available
Locator and necessary surrounding context:
Limit or conflicting evidence:
Artifact revision/hash if actually available:
```

A hash binds bytes, not truth or authorship. An absent hash remains unavailable. Do not fabricate it in a prompt. Store a source reference alongside each chunk in the destination system and keep the source readable. Rechunking or reembedding creates replaceable derivatives; it does not rewrite original evidence. The [worked example](../examples/README.md) includes a complete independent reuse unit.

## Review the intended performance

Ask a likely question of the extracted unit, then compare the answer it permits with the actual source. Probe the most consequential misunderstanding: causal versus observational, count versus rate, precision versus bias, recommendation versus permission, present versus historical scope. Merely sharing a topic or objective does not test that misunderstanding. Include an answerable query, a tempting unsupported conclusion and an unanswerable query; preserve refusal or uncertainty where the source runs out.

Mechanical structure checks complement this reading. They cannot determine whether a paraphrase is entailed, a locator supports a claim, or a sigil improves recall. To claim retrieval improvement, separately record actual queries, relevant source passages, target pipeline/model, comparison representation and observed errors. Hand-authored examples and expert continuation reviews are not executed model trials.
