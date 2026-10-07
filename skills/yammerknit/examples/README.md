# A complete first Yammerknit

Read [the fictional source](pilot-source.txt), then [the complete artifact](pilot-yammerknit.md). The example demonstrates faithful extraction, not a real study, proven retrieval benefit or executed model trial. No network or private corpus is needed.

The useful question is “What does the cooling pilot justify?” The source supports an observed 15% to 12% difference and a proposal for further testing. It does not support “the checklist reduces defects by 20%,” because P3 names concurrent supplier and operator changes. That exact causal gap, not a generic mention of uncertainty, is the review target.

The artifact preserves two numbers that are easy to confuse: 3 percentage points and 20% relative reduction. It also carries the glass exception. Removing that exception would make a locally useful extraction unsafe to reuse as general work guidance. The manager slide repeats this memo; counting it as an independent study would inflate the evidence.

## Try the native record journey

From this complete skill folder, use Python 3.10 or later. Choose a new writable workspace outside the installation; the example uses `practice-workspace` in your current directory for clarity. Each command is one line and works in PowerShell or a typical terminal.

```text
python scripts/yammerknit_tool.py init-record --source examples/pilot-source.txt --workspace practice-workspace --channel "Fictional Workshop" --title "Cooling checklist pilot"
python scripts/yammerknit_tool.py inspect-record --workspace practice-workspace
```

Copy the returned `record_id` exactly as ID in the next commands. Inspection first shows `current: null`: preserving a source has not created an artifact.

```text
python scripts/yammerknit_tool.py validate --artifact examples/pilot-yammerknit.md
python scripts/yammerknit_tool.py store-artifact --artifact examples/pilot-yammerknit.md --workspace practice-workspace --record-id "ID"
python scripts/yammerknit_tool.py inspect-record --workspace practice-workspace --record-id "ID"
```

Expect a structural pass, a saved base artifact and `health: verified-present-bytes`. Read the source comparison above before treating it as reviewed content. The helper cannot perform that semantic judgment.

For a revision, copy the artifact to a separate working file and clarify the Prompt Seeding Kit question about comparing suppliers while holding operator experience constant. Keep the source claims unchanged. Use `revise-artifact` with your working file, then inspect again: the new revision names the previous artifact as parent, and the base remains intact. A request to assert universal benefit must instead be declined or rewritten as a proposed test because the source cannot support it.

## Reuse a cluster by itself

Here is a complete chunk that retains its warrant when separated from the artifact:

```text
Title/terms: Cooling checklist, observed damage, confounding, causal inference.
Claim: The fictional metal-unit pilot observed 15/100 damaged units then 12/100 across different batches. This is 3 percentage points or 20% relative; it does not identify a checklist effect because supplier and staffing also changed.
Origin: Source paraphrase, with arithmetic from the stated counts.
Source: Cooling checklist pilot — fictional teaching source; pilot-source.txt.
Original SHA-256: 7913bec2bd425d7d45e3a932b0ffeacee026af78162dfcdae08b4b232c1dae47
Locator/context: P2–P4. No control group; uncertainty and sustained effect unreported.
Limit: Metal units only. P5 excludes glass pending separate protocol review. No cost evidence.
Artifact revision: Teaching artifact; no claimed model execution or production ingestion.
```

Ask “Does this establish an effect for glass units?” The correct answer is no, and the reason is the specific excluded population plus the unresolved causal attribution. Ask “How much money does it save?” The answer is unknown. Fluently inventing a cost estimate would be a failure even if every structural field passed.

## Return and recover

Run `inspect-record --workspace "PATH"` without an ID to browse titles and health. Select a returned ID, open its verified current artifact and follow the original source locator. To move the work, copy the entire workspace, then inspect at its new path; copying only the Markdown leaves evidence behind. For damaged bytes, see [custody recovery](../references/data-handling.md#recover-without-rewriting-history).
