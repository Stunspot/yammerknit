# Use Yammerknit

Talk to the agent normally. Yammerknit recognizes creation, inspection, repair, explanation, and source-organization work.

## Create a Yammerknit

Supply a transcript or document:

```text
Turn this transcript into a Yammerknit. Return the complete codefenced artifact.
```

Yammerknit should preserve supplied metadata, mark missing metadata `N/A`, follow semantic gravity rather than transcript order, and include the full cluster mesh, relational bridges, prompt seeds, and sigil lexicon.

## Save an organized record

Name a workspace when you want durable files:

```text
Turn this transcript into a Yammerknit. Preserve the source and organize the result in <workspace>\Yammerknits.
```

The workspace keeps original source bytes, normalized text, the base artifact, later revisions, manifests, and validation receipts distinct.

Use the helper directly when needed:

```text
python scripts/yammerknit_tool.py inspect-record --workspace <PATH> --record-id "<ID>"
```

The result identifies the base artifact, revision count, and current artifact without changing the record.

## Inspect or repair an artifact

```text
Inspect this Yammerknit against the canonical SOP. Explain every material defect.
```

```text
Repair only the failed structure, preserve sound content and sigil order, and save a new revision.
```

A repair creates a revision. It does not overwrite the original artifact.

## Acquire a YouTube transcript

The optional helper requires `yt-dlp`:

```text
python -m pip install -U yt-dlp
```

Then ask:

```text
Acquire the subtitles from <YouTube URL>, preserve them in <workspace>, and create a Yammerknit.
```

The helper requests subtitles without downloading audiovisual media, opening browser cookies, or traversing playlists. If `yt-dlp` or accessible subtitles are unavailable, provide transcript text directly.

## Configure and verify deterministic helpers

Run helper commands from the complete `yammerknit` skill folder. For direct subtitle acquisition:

```text
python scripts/yammerknit_tool.py acquire-youtube --url <URL> --workspace <PATH> --languages "en" [--rights-basis "<USER-SUPPLIED NOTE>"] [--yt-dlp <PATH-OR-COMMAND>]
```

`--languages` defaults to `en`. `--rights-basis` records a note the user supplied; it is not a fabricated legal clearance. `--yt-dlp` selects a separately installed executable when it is not on `PATH`.

Successful acquisition returns JSON with `status: created`, the `record_id`, source directory, manifest path, physical source SHA-256, and selected subtitle file. Validation returns `valid: true` only when every required structural check passes; it does not judge semantic excellence.

Use `init-record` for an existing UTF-8 source file, `validate` for a completed artifact, `store-artifact` for the first governed artifact, `revise-artifact` for a non-destructive successor, and `inspect-record` to identify the current artifact. Run `python scripts/yammerknit_tool.py <COMMAND> --help` for exact arguments.

## Prepare for vector RAG

Yammerknits are designed to preserve semantically useful shards, relationships, sigils, and provenance before embedding. A Yammerknit becomes part of an operating vector-RAG system only after a separate embedding and vector-storage pipeline ingests it.
