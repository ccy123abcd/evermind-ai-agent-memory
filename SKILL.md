---
name: evermind-ai-agent-memory
version: 0.1.1
description: Use when starting a new session and the assistant needs to recall who the user is and where work left off. Tiered progressive memory recovery — always read the core layer, check an auto-generated change index before re-reading secondary files, defer the rest until needed. Cuts recovery token cost ~70% versus reading everything every session (85%+ when the host already injects identity memory).
author: Evermind
license: MIT-0
metadata:
  hermes:
    tags: [memory, recovery, session, onboarding, context]
    related_skills: []
---

# Evermind

Progressive memory recovery for AI agents: your assistant stops losing context between sessions, without re-reading everything every time.

Every new session feels like "day one at work"? This skill hands the agent a **shift handover**: it always reads what matters (identity, rules, todos, latest work log), checks an auto-generated **change index** before re-reading secondary files, and defers everything else until actually needed.

## Platform support

| Platform | How to use |
|---|---|
| **Hermes** (Nous Research) | Drop this folder into the agent's `skills/` directory. On each new session say "recover memory" (or wire the SKILL.md procedure into a session-reset hook). Hermes injects SOUL/MEMORY/USER automatically — the skill detects host-injected identity and skips duplicate reads (the 85%+ savings case). |
| **ClawHub / OpenClaw** | Frontmatter is dual-compatible (standard fields + `metadata.hermes`). Install via `clawhub install txj/tiered-memory` or copy into the agent's skills dir. |
| **Claude Code / Cursor / Codex / other SKILL.md agents** | Copy this folder into the project or agent skills directory; at the start of a session, instruct the agent to follow SKILL.md (the procedure is model-agnostic). |
| **Any LLM, any OS** | Recovery logic is pure convention + one Python stdlib script — model-agnostic, runs on Windows/macOS/Linux, no GPU. |

## What it gives you

- 🧠 **No more lost context**: identity, rules, todos always loaded — nothing important silently dropped; new sessions resume where you left off
- ⚡ **Fast + cheap**: L3 always-read + L2 change-indexed reads (hash check — unchanged files are never re-read). ~44K → ~12K tokens per recovery (~70% less); with host-injected identity skipped, up to 85%+ total
- 🔒 **100% local**: pure local scripts, zero API cost, nothing leaves your machine

## How it works

| Layer | Reads | When | Cost |
|---|---|---|---|
| **L3 Must-read** | identity / rules / user profile / latest todos / latest work log | Every new session — the reliability anchor | small, fixed |
| **L2 Conditional** | secondary files (roles, members, configs) | **Only if the auto-generated change index flags a change**; otherwise just the index summary line | ≈0 ← savings live here |
| **L1 On-demand** | detail docs / history | Only when actually needed | 0 |

The engine is `scripts/memory_index.py`: run it daily (Task Scheduler / cron / launchd). It hashes every L2-tracked file and flags only what changed (md5 + 24h window). No index → you either re-read everything (expensive) or gamble (risky). With the index you get **neither**.

## Setup

1. Copy `config.example.yaml` → `config.yaml` and fill in:
   - `memory_root`: your memory files root
   - `must_read`: L3 files read every session
   - `tracked_files`: L2 files tracked for changes (path / display name / one-line description)
2. Generate the index (schedule it, e.g. daily):
   ```bash
   python scripts/memory_index.py --config config.yaml
   ```
   Produces `memory_index.md` (human-readable) + `memory_index_state.json` (script state, don't hand-edit).
3. Adjust lists to your own vault layout — must-read lives under `must_read`, change-tracked under `tracked_files`.

## Usage (start of every new session)

1. **Read the L3 must-read files** from your config — every one, no shortcuts.
2. **Read the change index** `memory_index.md`:
   - ✅ new change → read that file in full
   - ⏸ unchanged → read only its index summary line ← **savings live here**
3. **L1 on-demand**: consult detail docs only when a task actually needs them.
4. **Report recovery done** (identity ✅ / changes ✅ / N todos) so the user can confirm recovery ran.

## Files

- `scripts/memory_index.py` — change-index generator (pure stdlib, zero deps; first run flags everything new, then only real changes; files touched within 24h are also flagged)
- `config.example.yaml` — configuration template
- Outputs: `memory_index.md` + `memory_index_state.json`

## Security

- Reads only files listed in your `config.yaml`; never writes memory files themselves (only index md + state json)
- Nothing is uploaded anywhere — fully local, no remote install pipelines, no script-to-shell execution
- Python standard library only (PyYAML used when present, graceful degradation without)

## Roadmap (managed edition)

- Auto user-profiling (preferences / habits)
- Cross-device sync + web console
- One-click deploy — don't want to self-configure? Managed edition = zero-setup, full system, continuous updates. → [Managed edition entry: TBD]

## License

MIT-0 — free to use, modify, and sell.
