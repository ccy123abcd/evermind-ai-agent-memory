# Evermind

**Cross-session memory recovery for AI agents. Stop your assistant from forgetting — without re-reading everything every session.**

![version](https://img.shields.io/badge/version-0.1.1-blue)
![license](https://img.shields.io/badge/license-MIT--0-green)
![platform](https://img.shields.io/badge/platform-Hermes%20%7C%20Claude%20Code%20%7C%20Cursor%20%7C%20OpenClaw-lightgrey)
![deps](https://img.shields.io/badge/deps-zero-orange)

Every new session feels like "day one at work"? Your agent doesn't know who you are, what the rules are, or where work left off — so you re-explain everything, and it still drops things.

Evermind hands your agent a **shift handover** before it starts working:

- **Always reads** the core layer — identity, rules, user profile, latest todos, latest work log (nothing important silently dropped)
- **Checks a change index** (auto-generated, hash-based) before re-reading secondary files — unchanged files cost ~0
- **Defers everything else** until it is actually needed

Measured on our own production system: recovery drops from **~44K to ~12K tokens** (~70% less). When the host already injects identity memory (e.g. Hermes), the duplicated read is skipped automatically — **up to 85%+ total savings**.

## Quick start

```bash
# 1. get the skill
git clone https://github.com/ccy123abcd/evermind.git
cp -r evermind ~/.claude/skills/          # or your agent's skills dir

# 2. configure
cd evermind && cp config.example.yaml config.yaml
#   edit config.yaml: memory_root + must_read (L3) + tracked_files (L2)

# 3. generate the change index (schedule it daily)
python scripts/memory_index.py --config config.yaml

# 4. self-test (3 scenarios: first run / unchanged / changed)
python scripts/memory_index.py --config config.yaml --demo
```

Then, at the start of each new session, instruct your agent to follow `SKILL.md` (or wire it into a session-reset hook for Hermes).

## Platform support

| Platform | How to use |
|---|---|
| **Hermes** (Nous Research) | Drop into the agent's `skills/` directory; invoke "recover memory" per session or wire SKILL.md into a session-reset hook. Hermes injects SOUL/MEMORY/USER automatically — the skill detects host-injected identity and skips duplicate reads (the 85%+ case). |
| **ClawHub / OpenClaw** | Dual-compatible frontmatter (standard + `metadata.hermes`). Install into the skills directory or via your hub client. |
| **Claude Code / Cursor / Codex** | Copy the folder into the project or agent skills directory (`~/.claude/skills/`, etc.); instruct the agent to follow SKILL.md at session start. |
| **Any LLM, any OS** | Recovery logic is pure convention + one Python stdlib script — model-agnostic; Windows / macOS / Linux; no GPU. |

## Why not just another memory plugin?

Existing memory/marketplace skills are mostly about **storing** memories. Nobody solves **cheap, reliable recovery**:

- Naive recovery = re-read everything → expensive (44K tokens per session adds up fast on API pricing)
- "Trust the model to remember" = gamble → it forgets, and you don't know what it forgot

The missing piece is a **change index**: a daily hash pass that tells the agent *what actually changed* since the last session. With it, recovery is **neither expensive nor risky**. That index is what this skill automates (`scripts/memory_index.py`, pure stdlib, ~0 cost).

## How it works

| Layer | Reads | When | Cost |
|---|---|---|---|
| **L3 Must-read** | identity / rules / user profile / latest todos / latest work log | Every new session — reliability anchor | small & fixed |
| **L2 Conditional** | secondary files (roles, members, configs) | **Only if the auto-generated index flags a change**; otherwise just the index summary line | ≈0 ← savings live here |
| **L1 On-demand** | detail docs / history | Only when actually needed | 0 |

`scripts/memory_index.py` hashes every L2-tracked file (md5 + 24h freshness window) and writes a human-readable `memory_index.md`. No index → all-or-nothing. With an index → read the few files that changed.

> Honest numbers: ~12K is our measured tiered-recovery cost vs ~44K naive. ~6.5K is a projection for hosts that already inject identity (44K → 12K → 6.5K = ~85% cumulative). Highest-value users: heavy multi-session automation (many sessions/day).

## Configuration

Copy `config.example.yaml` → `config.yaml`:

- `memory_root` — root of your memory files
- `must_read` — L3 files, read in full every session
- `tracked_files` — L2 files, change-tracked (path / display name / one-line description)

Outputs: `memory_index.md` (readable) + `memory_index_state.json` (state — don't hand-edit).

## Usage protocol (start of every new session)

1. Read the L3 must-read files — every one, no shortcuts.
2. Read `memory_index.md`:
   - ✅ new change → read that file in full
   - ⏸ unchanged → index summary line only
3. Consult L1 detail docs only when a task needs them.
4. Report recovery done (identity ✅ / changes ✅ / N todos) so the user can confirm.

## Repository layout

```
evermind/
├── SKILL.md                 # agent-facing instructions (progressive disclosure)
├── README.md                # this file
├── config.example.yaml      # configuration template
├── scripts/
│   └── memory_index.py      # change-index generator (pure stdlib, zero deps)
├── CHANGELOG.md
├── LICENSE                  # MIT-0
└── version
```

## Security

- Reads only files listed in your `config.yaml`; never writes memory files themselves (only index md + state json)
- Nothing leaves your machine — no remote install pipelines, no script-to-shell execution
- Python standard library only (PyYAML used if present, graceful degradation without)

## Roadmap (managed edition)

- Auto user-profiling (preferences / habits)
- Cross-device sync + web console
- One-click deploy

**Don't want to self-configure?** The managed edition = zero-setup, full system, continuous updates. → [Managed edition: TBD]

## License

MIT-0 — free to use, modify, and sell.

---

*Crafted by 天玄镜 (Evermind) · TXJ system*  

⭐ Found this useful? Star the repo — it helps others find it. Found a bug? [Open an issue](https://github.com/ccy123abcd/evermind/issues).
