---
name: evermind-ai-agent-memory
version: 0.3.0
description: Never re-explain yourself. Evermind restores cross-session state in ~70% fewer tokens (measured 44K→12K) — so you can switch contexts anytime, at any task boundary, without losing your agent's memory. 100% local, zero deps, works with Claude Code, Hermes, Cursor & OpenClaw.
author: Evermind
license: MIT-0
metadata:
  hermes:
    tags: [memory, recovery, session, onboarding, context]
    related_skills: []
---

# Evermind

Progressive memory recovery for AI agents: your assistant stops losing context between sessions, without re-reading everything every time. Evermind first **discovers where your memory actually lives** (your files, your layout), then hands the agent a **shift handover** at session start.

Every new session feels like "day one at work"? This skill makes the agent read what matters (identity, rules, todos, latest work log), check an auto-generated **change index** before re-reading secondary files, and defer everything else until actually needed.

## Platform support

| Platform | How to use |
|---|---|
| **Hermes** (Nous Research) | Drop this folder into the agent's `skills/` directory. On each new session say "recover memory" (or wire the SKILL.md procedure into a session-reset hook). Hermes injects SOUL/MEMORY/USER automatically — the skill detects host-injected identity and skips duplicate reads (the 55-75% cumulative savings case). |
| **ClawHub / OpenClaw** | Frontmatter is dual-compatible (standard fields + `metadata.hermes`). Install via `clawhub install evermind-ai-agent-memory` or copy into the agent's skills dir. |
| **Claude Code / Cursor / Codex / other SKILL.md agents** | Copy this folder into the project or agent skills directory; at the start of a session, instruct the agent to follow SKILL.md (the procedure is model-agnostic). |
| **Any LLM, any OS** | Recovery logic is pure convention + one Python stdlib script — model-agnostic, runs on Windows/macOS/Linux, no GPU. |

## What it gives you

- 🧠 **No more lost context**: identity, rules, todos always loaded — nothing important silently dropped; new sessions resume where you left off
- ⚡ **Fast + cheap**: recovery cost ~44K → ~12K tokens (~70% less); with host-injected identity skipped, ~55-75% cumulative (measured 2026-09-04)
- 🔒 **100% local**: pure local scripts, zero API cost, nothing leaves your machine
- 📊 **Context health**: see your real context usage and get nudged before a session bloats (30/50/70% thresholds)

## How it works

| Layer | Reads | When | Cost |
|---|---|---|---|
| **L3 Must-read** | identity / rules / todos / latest journal | Every new session — the reliability anchor | small, fixed |
| **L2 Conditional** | other tracked files | **Only if the change index flags a change**; otherwise just the index summary line | ≈0 ← savings live here |
| **L1 On-demand** | detail docs / history | Only when actually needed | 0 |

The engine is `scripts/memory_index.py`: it **discovers** your memory files (role → real file), then hashes every L2-tracked file and flags only what changed (md5 + 24h window). No index → you either re-read everything (expensive) or gamble (risky). With the index you get **neither**.

## Setup (≈30 seconds)

```bash
# 1. get the skill (already done if you installed from ClawHub)
git clone https://github.com/ccy123abcd/evermind-ai-agent-memory.git
cp -r evermind-ai-agent-memory ~/.claude/skills/evermind   # or your agent's skills dir

# 2. cold start: no config needed — discovery finds your memory layout
cd evermind-ai-agent-memory
python scripts/memory_index.py --list .    # preview what discovery finds (nothing written)
python scripts/memory_index.py             # cold start: discover + write index

# 3. (optional) tune: copy config.example.yaml → config.yaml, set mode/roles/extras
#    or edit .evermind/discovery.json to override a discovered role

# 4. self-test
python scripts/memory_index.py --demo
```

Discovered roles are cached in `.evermind/discovery.json` — the agent reads it at recovery instead of re-scanning every session. Delete that file (or any discovered source) and it re-discovers automatically.

## Usage (start of every new session)

1. **Step 0 — Discover (first time or when sources moved)**: run `python scripts/memory_index.py --discover .` — it locates your memory carriers by common conventions (candidate list lives in the script header constants) and writes `.evermind/discovery.json`. Python unavailable? Fall back to the hand-list below (derived from the script; the script is authoritative). At every recovery, first **stat the stored paths** — any missing/unreadable source triggers re-discovery (never reuse stale paths).
2. **Read the L3 must-read files**: roles resolved in step 0/1 (rules, identity, todos, journal) + `must_read_extra`. Every one, no shortcuts. Host injected identity (Hermes/OpenClaw)? Mark `identity ✅ (host)` and skip the file probe.
3. **Read the change index** `memory_index.md`:
   - ✅ new change → read that file in full
   - ⏸ unchanged → read only its index summary line ← **savings live here**
4. **L1 on-demand**: consult detail docs only when a task actually needs them.
5. **Context gauge**: report real context usage — query your platform (Hermes `/status`; Claude Code `/context`; others: see the platform table below). Never invent a percentage; if the platform exposes none, say so. Optionally append `context: N%` to your recovery report.
6. **Report recovery honestly**: `identity ✅ (host) · rules ✅ CLAUDE.md · todos ✅ docs/TODO.md · journal ✅ journal/2026-09-04.md`. If a role came up empty, list it explicitly — never claim a full recovery that didn't happen.

### Context threshold nudges (30 / 50 / 70)

Check context usage at recovery and at long-task boundaries. Thresholds are tunable in spirit, defaults:

- **< 30%** — healthy, nothing to say
- **30–50%** — fine; keep working
- **50–70%** — suggest: "task boundary reached? Good moment to switch to a fresh session — recovery is ~12K tokens, nothing is lost."
- **≥ 70%** — recommend: "wrap up the current task and switch — this context is near its ceiling."

Switching is safe and cheap: that is the whole point of Evermind (recovery ≈ 12K tokens instead of tens of thousands of re-explaining).

### Platform context queries

| Platform | How to see context usage |
|---|---|
| Hermes | `/status` (usage %) |
| Claude Code | `/context` (window + usage — convert to %) |
| Cursor | composer status / model context indicator |
| OpenClaw | session/context indicator (varies by build) |
| unknown | report "this platform exposes no context gauge" — do not invent a number |

## Manual discovery fallback (Python unavailable)

Look for, in order (the script header candidate constants are authoritative — this is a summary):

- **rules/identity**: `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/` in the project; `~/.claude/CLAUDE.md` in home (candidate constants in the script header are authoritative)
- **todos**: `TODO.md` / `todo.md` / `todo.txt` / `tasks.md` (root or `docs/`); `~/todo.txt` or `~/.todo/` (todo.txt-cli)
- **journal**: newest `YYYY-MM-DD.md/.txt` under `journal/`, `logs/`, `notes/`, or `docs/journal/`
- **profile**: only if you configured one

## Files

- `scripts/memory_index.py` — discovery + change-index generator (pure stdlib; `--discover` / `--list` / `--demo` / `--mode internal|auto|manual`)
- `config.example.yaml` — configuration template (mode / roles / extras)
- Outputs: `.evermind/discovery.json` + `memory_index.md` + `memory_index_state.json`

## Security

- Discovery scans candidate paths by **name only** (metadata, no content) and writes `.evermind/discovery.json`; the index reads and hashes only files you listed (roles + extras)
- Never writes your memory files themselves (only discovery json + index md + state json)
- Nothing is uploaded anywhere — fully local, no remote install pipelines, no script-to-shell execution
- Python standard library only (PyYAML used when present, graceful degradation without)

## Roadmap (managed edition)

- Auto user-profiling (preferences / habits)
- Cross-device sync + web console
- One-click deploy — don't want to self-configure? Managed edition = zero-setup, full system, continuous updates. → [Managed edition entry: TBD]

## License

MIT-0 — free to use, modify, and sell.
