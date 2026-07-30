# Troubleshoot Yammerknit

## Codex reports the plugin as available but not installed

Run:

```text
codex plugin add yammerknit@personal
codex plugin list
```

Confirm the marketplace entry points to `./plugins/yammerknit` and that the target folder contains `.codex-plugin/plugin.json`. Start a new task after the status becomes `installed, enabled`.

## Claude cannot find the skill

Confirm the installed path ends in:

```text
yammerknit/SKILL.md
```

An extra directory level prevents discovery. Restart the host when the skills directory was created after the current session began.

## `yt-dlp is not available`

Install it separately:

```text
python -m pip install -U yt-dlp
```

If installation is unavailable, provide transcript text directly. Yammerknit creation does not otherwise depend on `yt-dlp`.

## No VTT subtitles were available

The video may have no accessible human or automatic subtitles. Provide an authorized transcript or another source document. The helper does not fall back to downloading or transcribing audio.

## The artifact fails validation

Read the `errors` array in `validation.json`. Ask the agent to repair only those structural failures, then validate the complete artifact again. A structural pass does not prove semantic quality; Giles must still inspect the mesh and source fidelity.

## Yammerknit refuses to overwrite a record

Keep the existing source and base artifact. Store the changed artifact as a revision or create a distinct record when the source itself changed.

## A moved workspace contains stale absolute paths

Version 0.1.0 manifests are designed to use relative internal links. If absolute paths appear inside a record produced by an earlier prerelease build, preserve the files and regenerate the manifests with the current helper rather than editing source or artifact bytes.
