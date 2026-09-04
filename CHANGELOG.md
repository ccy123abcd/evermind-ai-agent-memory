# Changelog

版本方案:**SemVer 2.0.0**(semver.org)——MAJOR=不兼容大改 / MINOR=向后兼容新功能 / PATCH=向后兼容修 bug;格式遵循 **Keep a Changelog**(keepachangelog.com):每版一节最新在上,日期 ISO 8601,改动按六类 Added/Changed/Deprecated/Removed/Fixed/Security。Unreleased 随做随记,发布时改版本号+日期,顶部重置空 Unreleased。

## [Unreleased]

### Changed
- (none pending)

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
