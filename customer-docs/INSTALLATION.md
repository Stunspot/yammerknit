# Install Yammerknit

The customer ZIP contains both supported host distributions. Extract `Yammerknit-v0.1.0.zip` first; the resulting folder is `yammerknit-v0.1.0`.

## Install the Codex plugin

Prerequisites:

- Codex with plugin support.
- Permission to add a local personal marketplace plugin.

1. Copy `codex-plugin/yammerknit` from the customer kit to:

   ```text
   %USERPROFILE%\plugins\yammerknit
   ```

2. Open `%USERPROFILE%\.agents\plugins\marketplace.json`.
3. Ensure its `plugins` array contains this entry:

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

4. Run:

   ```text
   codex plugin add yammerknit@personal
   ```

5. Run `codex plugin list`.

The installation is complete when `yammerknit@personal` reports `installed, enabled`. Start a new Codex task so the refreshed skill catalog is available.

If your personal marketplace uses another name, use that name after `@`. Preserve the existing marketplace file and unrelated entries.

## Install the Claude skill

Use `claude/yammerknit-v0.1.0.zip`.

For Claude Code, extract its single `yammerknit` folder into:

```text
~/.claude/skills/yammerknit/
```

On Windows:

```text
%USERPROFILE%\.claude\skills\yammerknit\
```

The installed folder must contain `SKILL.md` directly. Start a new Claude conversation or restart the host when its skill catalog does not refresh.

For Claude chat, enable **Code execution and file creation**, then open
**Customize > Skills**. Choose **Create skill > Upload a skill**, upload
`yammerknit-v0.1.0.zip` without extracting it, and enable Yammerknit in the
skills list.

Anthropic's current references:

- [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- [Extend Claude Code with skills](https://code.claude.com/docs/en/skills)

## Update or remove Yammerknit

To update, preserve your workspaces, replace only the installed plugin or skill folder with the newer distribution, and start a new task.

To disable the Codex plugin:

```text
codex plugin remove yammerknit@personal
```

Removing the plugin does not remove Yammerknit workspaces you created elsewhere.
