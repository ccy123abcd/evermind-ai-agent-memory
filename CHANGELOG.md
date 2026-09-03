# Changelog

## 0.1.1 (2026-09-03)

Renamed to **Evermind** (repo `evermind`; brand prefix dropped, low-key credit in README footer).
International release polish:
- README rewritten in English with per-platform install guide (Hermes / ClawHub / Claude Code / Cursor / generic SKILL.md agents)
- SKILL.md fully English; platform-support section added; frontmatter description extended (85%+ host-injection case)
- LICENSE file added (MIT-0)
- config.example.yaml comments and sample names in English
- Script user-facing output (docstring, CLI messages, demo) localized to English
- Chinese docs kept out of the published tree (archived locally)

## 0.1.0 (2026-09-03)

First release:
- Tiered progressive memory recovery (SKILL.md): L3 must-read / L2 conditional reads driven by a change index / L1 on-demand
- Companion script `scripts/memory_index.py`: config-driven change-index generation, pure stdlib, hash-idempotent with a 24h freshness window
- `config.example.yaml` template; README (pitch / how-it-works / install / safety / roadmap)
- Dual-compatible frontmatter (standard fields + Hermes `metadata.hermes`)
