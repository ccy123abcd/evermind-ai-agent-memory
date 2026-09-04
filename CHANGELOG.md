# Changelog

版本方案:**SemVer 2.0.0**(semver.org)——MAJOR=不兼容大改 / MINOR=向后兼容新功能 / PATCH=向后兼容修 bug;格式遵循 **Keep a Changelog**(keepachangelog.com):每版一节最新在上,日期 ISO 8601,改动按六类 Added/Changed/Deprecated/Removed/Fixed/Security。Unreleased 随做随记,发布时改版本号+日期,顶部重置空 Unreleased。

## [Unreleased]

### Changed
- (none pending)

## [0.3.0] - 2026-09-04

### Added
- **Environment discovery** (fixes the "assumes our file layout" flaw): `memory_index.py --discover`/`--list` locate the user's memory carriers by community conventions (rules/identity/todos/journal) → `.evermind/discovery.json`. Fresh installs work with zero config.
- **Semantic roles**: config `roles:` maps rules/identity/todos/journal/profile → real files (file or directory; directory resolves to newest `YYYY-MM-DD.*`); extras stay L3/L2.
- **Context gauge + threshold nudges**: per-platform context-usage query table (Hermes `/status`, Claude Code `/context`, …); honest reporting — never invent a percentage; 30/50/70% switch nudges.
- `--mode internal|auto|manual` (internal = fixed-layout for the maintainers' own vault; published/community default = auto).

### Changed
- Recovery is honest about sources: reports which files each role resolved to, and **lists empty roles instead of claiming a full recovery** (fixes silent false-recovery).
- Discovery cache is stat-validated before reuse — a moved/deleted source triggers re-discovery (never reuse stale paths).
- Legacy 0.2.x config (`must_read`/`tracked_files`) migrates automatically, preserving L3/L2 semantics (never upgrades L2 to per-session reads).
- Security wording updated for the discovery layer (name-only scan, no content reads); README/config/SKILL.md synchronized; root `version` file corrected (was stale 0.1.1).

### Fixed
- config.example.yaml key mismatches (`note:` vs code's `desc:`; `index_output` vs `output_index`) resolved by full rewrite.

## [0.2.2] - 2026-09-04

### Changed
- Positioning upgrade (user insight): headline benefit reframed as **free context switches** — cheap reliable recovery means users can switch sessions at any task boundary without losing state, instead of stretching one context until it breaks. README adds a "Why this changes your workflow" section; storefront description now leads with cross-session restore + switch-anytime + ~70% fewer tokens.
- README version badge corrected to 0.2.2 (was stale 0.1.1 through 0.2.0/0.2.1).

## [0.2.1] - 2026-09-04

### Changed
- Storefront description rewritten benefit-first: "Never re-explain yourself to your AI..." (value hook → quantified savings → platform list), replacing the mechanism-first wording — clearer what users get in the first 3 seconds.

## [0.2.0] - 2026-09-04

### Added
- L2 read policy split: index entries whose one-line description already answers the need (role cards / member summaries) now require only the **index summary line**, not a full-file read — full reads reserved for substantive docs.
- Single-source-of-truth note: index descriptions are display rows; authoritative one-line roles live in the roster table; agents self-evolving their SOULs must log the change and update the roster row.

### Changed
- SKILL.md Usage step 2 & How-it-works L2 row updated to the split policy (previously "changed → read in full").
- Honest-numbers wording aligned to the measured 2026-09-04 range (~55-75% cumulative for host-injected identity; retired the 85%/6.5K projection phrasing).
- Install references updated to the final slug `evermind-ai-agent-memory` (brand residue `txj/tiered-memory` removed).

### Fixed
- (none)

Private (not for release): the 9-member Tianxuan roster itself, local paths, Chinese docs.

## [0.1.1] - 2026-09-03

### Changed
- Renamed to **Evermind** (repo `evermind`; brand prefix dropped, low-key credit in README footer).
- README rewritten in English with per-platform install guide (Hermes / ClawHub / Claude Code / Cursor / generic SKILL.md agents).
- SKILL.md fully English; platform-support section added; frontmatter description extended (85%+ host-injection case).
- config.example.yaml comments and sample names in English.
- Script user-facing output (docstring, CLI messages, demo) localized to English.
- Chinese docs kept out of the published tree (archived locally).

### Added
- LICENSE file added (MIT-0).

## [0.1.0] - 2026-09-03

### Added
- Tiered progressive memory recovery (SKILL.md): L3 must-read / L2 conditional reads driven by a change index / L1 on-demand.
- Companion script `scripts/memory_index.py`: config-driven change-index generation, pure stdlib, hash-idempotent with a 24h freshness window.
- `config.example.yaml` template; README (pitch / how-it-works / install / safety / roadmap).
- Dual-compatible frontmatter (standard fields + Hermes `metadata.hermes`).
