# Install Yammerknit

The customer ZIP contains both supported host distributions. Extract `Yammerknit-v0.1.1.zip` first; the resulting folder is `yammerknit-v0.1.1`.

## Install the Codex plugin

Prerequisites:

- Codex with plugin support.
- Permission to add a local personal marketplace plugin.

1. Copy `codex-plugin/yammerknit` from the customer kit to:

   ```text
   %USERPROFILE%\plugins\yammerknit
   ```

2. Open `%USERPROFILE%\.agents\plugins\marketplace.json`.
3. Preserve the existing object and unrelated plugin entries. Ensure its `plugins` array contains:

   ```json
   {
     "name": "yammerknit",
     "source": {
       "source": "local",
       "path": "./plugins/yammerknit"
     },
     "policy": {
       "installation": "AVAILABLE",
       "authentication": "ON_INSTALL"
     },
     "category": "Productivity"
   }
   ```

4. Run `codex plugin add yammerknit@personal`.
5. Run `codex plugin list`.

The package is installed and enabled only when `yammerknit@personal` reports `installed, enabled`. Start a new Codex task, then verify discovery with:

```text
Use $yammerknit to explain what source material you need and what a complete Yammerknit contains. Do not create an artifact yet.
```

A successful verification names the required source, codefenced artifact, insight clusters, relational mesh, prompt seeds, sigil lexicon, provenance boundary, and the distinction between a prepared mesh and an operating vector-RAG system. A generic summary is not proof of discovery.

If your personal marketplace uses another name, use that name after `@`.

## Install the Claude skill

Use `claude/yammerknit-v0.1.1.zip` from the customer kit.

### Claude Code

Extract its single `yammerknit` folder into:

```text
~/.claude/skills/yammerknit/
```

On Windows:

```text
%USERPROFILE%\.claude\skills\yammerknit\
```

The installed folder must contain `SKILL.md` directly. Start a new Claude conversation or restart the host when its skill catalog does not refresh.

### Claude chat

Enable **Code execution and file creation**, then open **Customize > Skills**. Choose **Create skill > Upload a skill**, upload `yammerknit-v0.1.1.zip` without extracting it, and enable Yammerknit in the skills list.

For either Claude host, make the same discovery-only request shown for Codex. Verify the response names the complete structure and evidence boundary before supplying private source material. Package structure is verified; live Claude activation is not claimed by this repository.

Anthropic's current references:

- [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- [Extend Claude Code with skills](https://code.claude.com/docs/en/skills)

## Use another capable agent

Give the host the complete `yammerknit` skill folder from either distribution. Keep `SKILL.md` and every sibling subfolder together. The host must support its own skill discovery; Python execution is required only for persistence, validation, revision, inspection, and subtitle helpers. Verify discovery with the same discovery-only request. Host-specific activation remains unverified unless that host is exercised directly.

## Update Yammerknit

Preserve workspaces outside the installed package. Replace only the installed plugin or skill folder with the newer distribution, start a new task or conversation, confirm the reported version, and repeat the discovery-only verification. Do not merge old and new runtime folders.

## Remove Yammerknit and clean up data

- Codex: run `codex plugin remove yammerknit@personal`, then remove `%USERPROFILE%\plugins\yammerknit` only after confirming it is the intended plugin directory.
- Claude Code: remove only `~/.claude/skills/yammerknit/` or `%USERPROFILE%\.claude\skills\yammerknit\` after confirming the final path.
- Claude chat: disable or delete Yammerknit from **Customize > Skills**.
- Other hosts: use that host's removal mechanism, then remove only the installed Yammerknit skill folder.

Removal does not delete workspaces, source records, artifacts, revisions, receipts, downloaded customer ZIPs, or extracted kits stored elsewhere. Review those separately under your retention policy; back up anything required, then delete only explicitly selected paths. Yammerknit has no cloud account, telemetry store, or vendor-side data store to purge.
