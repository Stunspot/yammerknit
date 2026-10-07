# Data, portability and custody

Your workspace separates original source bytes, normalized text, authored artifacts, revisions and receipts. Read [the full layout and recovery contract](../skills/yammerknit/references/data-handling.md). Preserve the complete workspace when moving or backing it up; the installation is replaceable and should not contain user records.

Inspection checks actual hashes, receipt agreement and ancestry before naming a current artifact. It does not authenticate the source, prove authorship or resist coordinated alteration of content and manifests. A separately trusted backup or digest is needed for that stronger check. Older records missing historical source bindings are labeled explicitly; updating the helper does not invent those bindings.

The core helper has no telemetry, cloud account or vector-storage service. Your agent host may send supplied content to its model/provider under its own configuration. Optional subtitle acquisition runs separately installed yt-dlp and contacts YouTube; a local command is not an offline operation merely because records are stored locally. Private source content and user-supplied metadata can themselves contain sensitive information. Minimize them before sharing support logs, publishing or using a remote embedding service.

The helper rejects linked/reparse paths and preserves existing records on collision. It is intended for a user-controlled local workspace, not a hostile shared filesystem. Staging and record locks support recoverable writes. An interrupted lock needs a check for a still-running writer before removal. See [troubleshooting](TROUBLESHOOTING.md).
