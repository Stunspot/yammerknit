# Install Yammerknit

Extract `Yammerknit-v0.1.0.zip` to a stable folder. The customer root is `yammerknit-v0.1.0`. Keep your sources and workspaces elsewhere. The kit includes both host distributions; choose one for the host you use.

## Install the Codex plugin

With Codex plugin support available, run these commands from the extracted customer root:

```text
codex plugin marketplace add .
codex plugin add yammerknit@yammerknit-local
codex plugin list
```

The included `.agents/plugins/marketplace.json` points to `./codex-plugin/yammerknit` relative to this customer root. Keep that root in place. This route does not require editing another personal marketplace or replacing unrelated entries. If the marketplace name already exists, inspect `codex plugin marketplace list` and use the existing intended root or remove only that old Yammerknit marketplace registration before adding this one. Preserve workspaces and unrelated plugins.

Start a fresh task after installation. Ask: “Use $yammerknit with the included fictional cooling-pilot source. Explain what the 15-to-12 comparison establishes and what it does not, then create the full artifact.” Confirm the host actually loaded Yammerknit and compare the result with [the worked example](../skills/yammerknit/examples/README.md). Merely listing vocabulary is not proof that source constraints survived.

## Install the Claude skill

For Claude Code, extract the single `yammerknit` folder from `claude/yammerknit-v0.1.0.zip` into `~/.claude/skills/`. The resulting `~/.claude/skills/yammerknit/SKILL.md` must exist directly. Keep every sibling folder. Start a fresh session and check skill discovery. [Claude Code skill documentation](https://code.claude.com/docs/en/skills).

For Claude chat, enable code execution and file creation if available, open **Customize > Skills**, choose **+ Create skill**, then **Upload a skill**. Upload the nested `claude/yammerknit-v0.1.0.zip`, not the whole customer kit, and enable it. Organization policy may control availability. [Claude skill instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

Use the same worked-source request to check the task, not just discovery. This repair verifies the package's structure; fresh Claude activation is not claimed.

## Use another capable agent

Give it the complete skill folder from either distribution and point it to `SKILL.md`. If skills are not supported, attach the source plus the active skill and its referenced method files in a normal conversation, explicitly requesting a full Yammerknit. The no-Python fallback is an inline artifact with source locators; it cannot claim a saved workspace or mechanical validation. Do not paste the historical persona alone and assume it contains the active custody and fidelity guidance.

## Update, remove and recover

Keep user workspaces outside the runtime. For an update, preserve a copy of the old kit, select the new complete kit, reinstall the intended plugin/skill through the same host route and start a fresh task. Do not merge runtime folders. A same-version repair is distinguished by its package digest, not by the displayed version alone.

For Codex removal use `codex plugin remove yammerknit@yammerknit-local`; optionally remove that marketplace registration with `codex plugin marketplace remove yammerknit-local` when no longer needed. For Claude Code remove only the exact installed Yammerknit skill directory; in Claude chat disable or delete that skill. Package removal leaves separately stored records intact. Before deleting any workspace, choose the exact data and keep required backups. See [recovery](TROUBLESHOOTING.md) if installation or inspection fails.
