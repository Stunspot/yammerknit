# Data handling and privacy

Yammerknit keeps source evidence separate from generated knowledge artifacts.

## Workspace layout

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
  revisions/<record-id>/<revision-id>/
    yammerknit.md
    revision-manifest.json
    validation.json
```

The source manifest records relative filenames and hashes. Artifact and revision manifests use relative links so the complete workspace can move without losing its internal references.

## Default behavior

- Existing records are not overwritten.
- Original bytes remain distinct from normalized UTF-8 text.
- Revisions identify their parent artifact.
- `inspect-record` determines the current artifact from immutable manifests.
- Unknown metadata remains `N/A` or `null`.
- Credentials, browser cookies, tokens, and unrelated page data are not collected.

## Network behavior

Core Yammerknit creation uses only the source supplied to the agent. The optional YouTube helper invokes the separately installed `yt-dlp` program and contacts YouTube for accessible subtitle data. Yammerknit includes no telemetry service and no vector-storage service.

The user chooses the workspace and any later transfer, embedding, backup, or publication destination. Package installation does not upload existing Yammerknit records.
