# Changelog

## [1.0.1] - 2026-04-21

### Fixed
- `launch-mcp check` now refreshes `oxidize-pdf` in an existing plugin venv instead of short-circuiting once the package is importable. Prior behavior froze users on whatever version was installed the first time they ran the plugin — e.g. users still on `oxidize-pdf` 0.3.x never received the 7× TTF-subsetter size reduction shipped in 2.5.4.

### Added
- Upgrade throttle to keep `SessionStart` fast: the existing-venv upgrade path runs at most once every `OXIDIZE_UPGRADE_INTERVAL_SECONDS` (default 604800 = 7 days), tracked via a `.last_upgrade_check` stamp in `$CLAUDE_PLUGIN_DATA`.
- `OXIDIZE_SKIP_UPGRADE=1` escape hatch to disable auto-upgrade entirely for users who pin versions manually.

## [1.0.0] - 2026-04-13

### Added
- Claude Code plugin with 6 skills, 1 agent, and MCP server integration
- Self-hosted marketplace for direct GitHub installation
- Bootstrap script with smart dependency detection
