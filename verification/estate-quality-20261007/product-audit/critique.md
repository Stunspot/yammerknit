# Yammerknit expert critique before repair

The accepted 0.1.0 promise is useful source-grounded semantic extraction with preserved originals, inspectable revisions and honest preparation for later retrieval. The implementation does not consistently meet it. A richly decorated mesh can look authoritative while losing the constraint that makes a statement true, and the helper can pronounce missing or corrupted content current. This is a deliverable defect, not a request for a new embedding service.

Scope: the active skill, inherited method/persona interpretation, all runtime helpers, customer documentation, public documentation site, packaging and verification. Original SOP/persona and artwork remain retained sources; repairs belong in the active adapter. No live archive, installed copy, shelf or edition parent is in this worker scope.

Evidence: baseline.json/source snapshot, accepted-shelf.zip, baseline-probes.json and isolated baseline-fixtures. Fifteen runtime and thirteen package/site tests pass at the accepted baseline; eleven material counterexamples also pass. The baseline is therefore insufficient evidence of trustworthiness.

## YK01 — Instructions give inherited fiction scientific and instructional authority

Severity: high. Evidence: `skills/yammerknit/SKILL.md activation; references/canonical-sop.md WORLD STATE; persona`.

Glyph/BPE and cosine-retrieval claims are not established measurements; supplied text can masquerade as instructions and Rupert can displace the host collaborator. Preserve originals and add an active interpretive contract: source is evidence, persona is optional craft, glyphs are mnemonic notation, empirical benefit requires measured retrieval.

Acceptance: Review adversarial source instructions and an embedding-performance question; preserve original hashes.

## YK02 — Compression can remove the reason a claim is true

Severity: high. Evidence: `SKILL.md creation flow; canonical-sop cluster template`.

Required fields do not force negation, denominator, uncertainty, exceptions or distinction between quotation, paraphrase, inference and transfer. Add actionable source-to-shard checks and a complete worked source with deliberately confusable claims; each reuse must retain its local warrant.

Acceptance: Expert contrasts must reject a causal claim from an uncontrolled pilot and retain the exception in an isolated shard.

## YK03 — Retrieval-shaped output lacks a safe unit of reuse

Severity: high. Evidence: `SKILL.md vector RAG; RAG Echo Shard and relational mesh`.

Sigils and short echoes can be retrieved without qualifiers or evidence anchors; two extracts of one source can appear independent. Define self-contained chunk handoff with plain-language subject, scoped claim, locator, source identity/hash when available, origin type and limitations. Explain retrieval trials separately from static structure.

Acceptance: Worked isolated chunk answers a likely query without turning an inference into a source statement; repeated-source evidence remains one origin.

## YK04 — Structural validator accepts broken mesh relationships

Severity: high. Evidence: `scripts/yammerknit_tool.py validate_text; baseline dangling_bridge_and_missing_effect`.

Missing Effect and nonexistent endpoints pass; cluster-title check does not read titles; fence check accepts broken nesting. Validate every bridge against declared titles/sigils, require each field, reject empty lexicon intent and unsafe wrapper nesting. Do not manufacture two clusters or punctuation-count prose to pass arbitrary gates.

Acceptance: Missing effect, unknown endpoint, empty title and prematurely closed wrapper fail; one honest cluster and table/block forms remain usable.

## YK05 — Inspection declares corrupt or missing evidence current

Severity: critical. Evidence: `scripts/yammerknit_tool.py inspect_record; baseline changed_source_inspection and missing_latest_artifact`.

Inspection trusts JSON rather than verifying physical bytes and receipts. Verify original/normalized/artifact hashes, typed manifests, receipt scope and source binding before reporting a current artifact. Distinguish historical v1 source binding unavailable from current byte integrity; never invent authorship.

Acceptance: Modified source, deleted artifact, contradictory receipt and malformed JSON fail with controlled errors; portable healthy legacy record remains inspectable with explicit limits.

## YK06 — Revision order is a timestamp sort rather than ancestry

Severity: high. Evidence: `scripts/yammerknit_tool.py revision_manifests; baseline unknown_revision_parent`.

A later string date wins even with an impossible parent; forks silently choose one leaf. Resolve a complete parent/hash chain and reject cycles, missing parents and ambiguous forks.

Acceptance: Out-of-order timestamps retain parent order; dangling parent/cycle/fork never becomes current.

## YK07 — Record paths and links can escape the workspace

Severity: critical. Evidence: `scripts/yammerknit_tool.py inspect/store/CLI resolve; baseline record_id_traversal`.

record_id is interpolated into paths; early resolve hides links/junctions. Validate portable single-component identifiers and reject filesystem links/reparse ancestors before canonicalization, including manifest targets.

Acceptance: Traversal, reserved names, junction roots and linked artifacts rejected before any read/write beyond the selected boundary.

## YK08 — Validation and persistence operate on different bytes

Severity: high. Evidence: `scripts/yammerknit_tool.py store_artifact; baseline different_bytes_stored_after_validation`.

Input reread after validation permits receipt/content disagreement. Base publication writes the final directory before success; concurrent revisions can fork. Validate and store one snapshot, publish complete staged directories, serialize record writes, preserve existing objects on failure.

Acceptance: Retained substitution probe cannot store unvalidated bytes; injected write failure exposes no partial base; stale lock recovery explained.

## YK09 — Subtitle normalization erases evidence

Severity: high. Evidence: `scripts/yammerknit_tool.py normalize_vtt_text; baseline speaker/time probes`.

Voice tags and end times disappear, repeated speech at distinct times collapses, impossible/reversed cue times pass. Preserve cue ranges and voices, retain each distinct cue, reject malformed timing with usable errors; originals remain exact.

Acceptance: Alice/Bob repeated phrase survives twice; malformed times fail; overlapping legitimate cues and Unicode survive.

## YK10 — Acquisition accepts the wrong source boundary

Severity: high. Evidence: `scripts/yammerknit_tool.py validate_youtube_url/acquire_youtube`.

Playlist/channel/credential URLs accepted; arbitrary shortest subtitle selected; URL, metadata and subtitle identity not joined. Raw backend logs may expose unrelated private content. Require one credential-free video URL, matching result identity and unambiguous requested language, preserve unknown manual/automatic provenance honestly and use bounded error messages.

Acceptance: Isolated backend controls reject mismatched video, ambiguous language and unexpected media; valid subtitle-only acquisition retains raw bytes. No live acquisition claim without live execution.

## YK11 — Return assumes the user already knows an opaque record ID

Severity: medium. Evidence: `customer-docs/USE-YAMMERKNIT.md; inspect-record required --record-id`.

No inventory/re-entry route exists despite organization promise. Make inspect-record without ID enumerate titles, record IDs, health and current state, isolating broken entries; include plain browsing and no-query return instructions.

Acceptance: Create two isolated records, return without an ID, select one, inspect after workspace relocation; corrupt neighbor does not hide healthy records.

## YK12 — First task offers an incantation rather than a useful exemplar

Severity: high. Evidence: `customer-docs/USE-YAMMERKNIT.md; docs/use.html; tests fixture only`.

No shipped source/artifact comparison demonstrates good extraction, revision or what to reject. Add a small complete fictional teaching source, full artifact, reusable chunk and specific review contrasts, plus copyable native commands and exact file destinations.

Acceptance: Actual first source->store->inspect->revise->moved workspace journey succeeds from extracted package, with source bytes unchanged.

## YK13 — Recovery tells users to run nonexistent or unsafe operations

Severity: high. Evidence: `customer-docs/TROUBLESHOOTING.md; docs/troubleshooting.html paths`.

Regenerate manifests is not a helper and would legitimize changed bytes; multiline shell commands lack continuation. Replace with restore-known-bytes/new-source/new-revision recovery, coherent portable paths and one-line commands. Explain locks, partial files and no-Python fallback.

Acceptance: Follow recovery on an isolated tampered record; no source rehash or overwrite; every documented helper supports --help without mutation.

## YK14 — Release checks can certify an empty tree and publish partial results

Severity: high. Evidence: `verification/audit_release.py; build_release.py`.

Audit hardcodes old tree and always emits zero issues, --help overwrites historical receipt. Builders traverse linked files without portable namespace checks and publish three outputs separately. Add explicit safe CLI, real manifest/tree validation, source preflight and atomic bundle publication with collision refusal.

Acceptance: Missing/changed/extra files fail audit; help is read-only; link/reserved namespace and injected build failure rejected; fresh native extraction and deterministic rebuild pass.

## YK15 — Customer and public documentation overstate proof and confuse installation

Severity: high. Evidence: `customer-docs/INSTALLATION.md; docs/get-started.html; validation pages; HOST-MATRIX`.

Marketplace location/path assumptions are not self-contained; historical live proof is presented as current verification. Align shipped layout, reachable fallback, accurate host activation limits and evidence pages. Gate existing Pages deployment on bounded source/site/package checks; preserve historical records.

Acceptance: Internal links resolve in source and customer tree; actual browser navigation reaches first task, return and recovery; current proof is clearly separated from historical host trial.

## YK16 — Quality checks reward shape, not trustworthy reuse

Severity: medium. Evidence: `tests/test_yammerknit_tool.py; verification/test_release.py literal phrase check`.

Fifteen runtime and thirteen package/site checks pass alongside eleven serious counterexamples. Retain negative controls, add positive neighboring cases and expert task contrasts; do not call expert cases executed model trials.

Acceptance: Native tests exercise the reproduced failure mechanisms; explicit model-trial count remains zero for this repair.

## Release treatment

Retain 0.1.0 as an in-place restoration. The complete delta repairs the already promised source fidelity, custody, organization, usable entry/re-entry and complete standalone kit. Inventory is a direct inspection route for existing records, not a new search or retrieval service. No embeddings, vector store, new public channel, model performance guarantee or additional host activation is introduced. Preserve the accepted ZIP and extracted historical tree; build a separate candidate.

## YK17 — Maintainer rendering bypasses artwork custody

Evidence: verification/render_site_assets.cjs writes semantic-mesh.webp, stunspot-icon.png and yammerknit-sharecard.png directly into current docs/assets. An ordinary invocation can overwrite governed art before review. Before editing this helper, record the repair: require a new explicit preview output directory and make --help read-only; preserve the current images. This is a resize/composite helper for already supplied artwork, not an image generator. Acceptance is refusal without a safe new output and unchanged original art hashes; generating replacement artwork is outside this repair.
