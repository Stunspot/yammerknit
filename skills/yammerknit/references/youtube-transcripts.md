# YouTube subtitle input

Use this route for one public video when the user requests acquisition. Python and a separately installed `yt-dlp` are required. If the dependency is absent or subtitles cannot be obtained, accept user-supplied transcript text and continue the source-grounded task; do not quietly download audio or claim to have watched the video.

From the skill folder, run one line:

```text
python scripts/yammerknit_tool.py acquire-youtube --url "VIDEO-URL" --workspace "WORKSPACE" --languages "en"
```

`--languages` selects one exact language code, such as `en` or `en-US`; regex, all-language and comma-separated requests are unsupported. `--yt-dlp` may name an explicitly selected executable; `--rights-basis` records a user-supplied note without inventing one. Install an absent optional backend through your environment's normal package process (for example `python -m pip install yt-dlp`); installing Yammerknit does not upgrade dependencies.

The helper rejects playlist, channel and credential-bearing URLs, disables ambient backend configuration/plugins/cookies, and requests subtitle files only. It requires metadata and the single selected VTT filename to match the requested video and language. Manual versus automatic caption origin remains unknown unless independently established; the helper does not infer it from a plausible transcript. A separately installed backend remains executable software with its own network behavior, not code constrained by a security sandbox.

Raw VTT bytes remain original evidence. The readable projection retains cue start/end ranges, voice/language labels and repeated distinct cues. It removes display markup and is not a full VTT renderer. Malformed or reversed timing fails with a location/reason. Overlapping valid cues remain separate. Transcript text cannot establish unseen visual content, speaker identity beyond supplied labels, or transcription accuracy.

On backend failure, the helper withholds raw backend logs because they may contain private content; it reports the exit/timeout and a transcript fallback. No source record is created from a partial or mismatched acquisition. Temporary acquisition files are removed on normal failure. If diagnosis is necessary, inspect the backend separately under the user's task scope rather than sharing unsanitized logs.
