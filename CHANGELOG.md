# Changelog

This repo hosts multiple integrations; each section is scoped per integration.
See [RELEASING.md](./RELEASING.md) for tag and versioning conventions.

## [llamaindex-v0.1.0] - 2026-04-21

### Added
- New `llamaindex/` sub-package — `llama-index-readers-oxidize-pdf` on PyPI.
- `OxidizePdfReader(BaseReader)` with three modes: `rag` (default, one `Document` per semantic chunk with `heading_context`, `element_types`, `page_numbers`, `token_estimate`), `pages` (one `Document` per page), `markdown` (single `Document`, full PDF as markdown).
- Adapter normalizes `page_numbers` to 1-indexed so metadata is consistent across modes, with a regression test guarding the behavior. The underlying oxidize-pdf `RagChunk` emits 0-indexed pages today.
- 22 behavior tests covering construction, all three modes, metadata shape, `extra_info` merging, and path-vs-str inputs. PDFs generated programmatically in `conftest.py` — no binary fixtures checked in.

## [claude-code-v1.0.1] - 2026-04-21

### Fixed
- `launch-mcp check` now refreshes `oxidize-pdf` in an existing plugin venv instead of short-circuiting once the package is importable. Prior behavior froze users on whatever version was installed the first time they ran the plugin — e.g. users still on `oxidize-pdf` 0.3.x never received the 7× TTF-subsetter size reduction shipped in 2.5.4.

### Added
- Upgrade throttle to keep `SessionStart` fast: the existing-venv upgrade path runs at most once every `OXIDIZE_UPGRADE_INTERVAL_SECONDS` (default 604800 = 7 days), tracked via a `.last_upgrade_check` stamp in `$CLAUDE_PLUGIN_DATA`.
- `OXIDIZE_SKIP_UPGRADE=1` escape hatch to disable auto-upgrade entirely for users who pin versions manually.

## [claude-code-v1.0.0] - 2026-04-13

Released under the unprefixed tag `v1.0.0` (grandfathered — see [RELEASING.md](./RELEASING.md)).

### Added
- Claude Code plugin with 6 skills, 1 agent, and MCP server integration
- Self-hosted marketplace for direct GitHub installation
- Bootstrap script with smart dependency detection
