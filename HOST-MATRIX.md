# Host matrix

| Host | Customer object | Structural state | Live state | Optional dependency |
|---|---|---|---|---|
| Codex | `codex-plugin/yammerknit/` | Plugin and skill validation required | Local installation, discovery, and a fresh-task representative request required | Python for deterministic record tools |
| Claude | `claude/yammerknit-v0.1.1.zip` | One top-level `yammerknit` folder with complete runtime closure | Not established without a Claude host | Python for deterministic record tools |
| Other agents | `skills/yammerknit/` from either distribution | Model-facing files are self-contained beneath the skill root | Host-specific discovery is not claimed | Host must expose file/script capabilities for persistence |

Core artifact creation is model work. Deterministic persistence and validation require a host that can run Python. YouTube subtitle acquisition additionally requires `yt-dlp`.
