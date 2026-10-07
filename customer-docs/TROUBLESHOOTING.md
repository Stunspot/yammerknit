# Recover from an observable failure

## The host cannot find Yammerknit

Follow [the host-specific installation route](INSTALLATION.md). In Codex, check `codex plugin marketplace list` and `codex plugin list`; the included marketplace must resolve to the extracted customer root containing `codex-plugin/yammerknit/.codex-plugin/plugin.json`. In Claude Code the directory must end in `yammerknit/SKILL.md` without an extra nested folder. Start a fresh task after installation. If the host has no skill support, use the documented manual-context fallback.

## Python or yt-dlp is unavailable

Without Python, the agent can return the full artifact in chat but cannot claim native validation or saved records. Python 3.10+ is required for helpers. Run `python scripts/yammerknit_tool.py --help` from the complete skill folder, or use its absolute script path. Do not run an old kit's similarly named helper by accident.

If yt-dlp is missing, supply transcript text or install the optional backend through your normal environment process. No automatic upgrade is required. If acquisition fails, use the reported exit/timeout and the [subtitle guide](../skills/yammerknit/references/youtube-transcripts.md). The helper does not fall back to audio downloads. A language request must name one exact language code; mismatched or ambiguous files are rejected.

## Structure fails or the answer misrepresents the source

Read the `errors` array from `validate`. Correct the named structural defect in a separate draft, then validate again. For source fidelity, compare each consequential claim and qualifier with the actual locator, including conflicting passages. A structural pass cannot settle that review. Save a corrected artifact as a revision rather than overwriting the base.

## A file changed, disappeared or moved

Inspect the record before reuse. Restore a missing/changed file only from a known matching backup; otherwise preserve the damaged record as unverified and create a new source record for intentional new content. Do not regenerate manifests to bless changed bytes. Complete workspaces use relative references and can move without rewriting manifests. If an older unsupported record contains absolute links, retain it and reconstruct a new record from known original evidence, preserving the historical record separately.

## A revision fork, cycle or unknown parent appears

No artifact is selected current. Preserve the branches and compare their claims and parents. Reconcile in a complete copied workspace using [the detailed recovery procedure](../skills/yammerknit/references/data-handling.md#recover-without-rewriting-history). The latest timestamp is not evidence that a branch is authoritative.

## Overwrite, linked path or busy record is refused

For an existing base use `revise-artifact`; for changed source content use `init-record` to create a distinct record. IDs are single portable path components, not directory paths. Linked/junction directories are unsupported: use the physical directory or a complete ordinary copy. For a busy/interrupted record, the error names a lock with its process ID. Confirm the writer is no longer running before removing only that lock. Staging is never a current artifact.

For support, include version, package digest, host, exact command/error and failure stage. Remove private source text, credentials and unrelated metadata. [Support routes](../SUPPORT.md).
