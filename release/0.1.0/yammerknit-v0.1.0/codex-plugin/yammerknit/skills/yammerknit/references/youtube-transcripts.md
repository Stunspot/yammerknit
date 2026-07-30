# YouTube subtitle acquisition

Use transcript acquisition when the user supplies:

- one YouTube video URL;
- the destination workspace.

Run:

```text
python scripts/yammerknit_tool.py acquire-youtube --url <URL> --workspace <PATH>
```

If the user supplies a relevant rights or usage note, preserve it with `--rights-basis "<note>"`. Do not require the user to perform legal analysis as an access ritual.

The helper delegates subtitle retrieval to `yt-dlp` when available. It requests human or automatic subtitles, skips audiovisual download, rejects playlists, supplies no cookies or credentials, and preserves both the raw subtitle file and normalized timestamped text with a provenance manifest. `yt-dlp` is an optional host dependency; package presence alone does not establish that acquisition is available.

Keep account access, paywall or age-gate bypass, playlist crawling, browser-cookie inspection, and audiovisual download outside this helper. Follow the source's access conditions and the user's authority. If subtitles or `yt-dlp` are unavailable, report that boundary and accept user-supplied transcript text.
