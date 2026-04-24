# Changelog

This repo hosts multiple integrations; each section is scoped per integration.
See [RELEASING.md](./RELEASING.md) for tag and versioning conventions.

## [langchain-v0.1.0] - 2026-04-24

### Added
- New `langchain/` sub-package — `langchain-oxidize-pdf` on PyPI.
- `OxidizePdfLoader(BaseLoader)` with three modes: `rag` (default, one `Document` per semantic chunk with `heading_context`, `element_types`, `page_numbers`, `token_estimate`), `pages` (one `Document` per page), `markdown` (single `Document`, full PDF as markdown).
- `lazy_load()` is the primary entry point returning a generator (not a materialized list), so large PDFs stream into downstream consumers without forcing full memory load. `load()` is inherited from LangChain's `BaseLoader` as the convenience materializer.
- File path is bound at construction (`OxidizePdfLoader("paper.pdf", mode=..., extra_info=...)`) following the LangChain convention established by `PyPDFLoader`.
- Adapter normalizes `page_numbers` to 1-indexed so metadata is consistent across modes and with `PyPDFLoader` expectations.
- 29 behavior tests (35 including parametrizations) covering construction, all three modes, metadata shape, `extra_info` merging, path-vs-str inputs, laziness (iterator contract), and disjointness (7 semantic regression tests spanning single-page and multi-section PDFs) — shipped from day one to avoid repeating the LlamaIndex 0.1.0 accumulation regression.
- Requires `langchain-core>=0.3,<0.4` and `oxidize-pdf>=0.4.3` (the `HybridChunker` disjointness fix from core 2.5.5).

## [llamaindex-v0.1.1] - 2026-04-22

### Fixed
- **`mode="rag"` now emits element-disjoint `Document` lists.** 0.1.0 inherited a bug from `oxidize-pdf-core` 2.5.4's `HybridChunker`: the overlap branch re-injected just-flushed elements into the working buffer, so each chunk i+1 contained chunk i as a prefix (quadratic accumulation). Audit on real PDFs in 0.1.0 produced output where a single source paragraph appeared in 3+ `Document`s, breaking de-duplication and embedding budgets in downstream RAG pipelines. 0.1.1 requires `oxidize-pdf>=0.4.3` (which pins `oxidize-pdf-core 2.5.5`, where the chunker fix lives) and adds 7 semantic regression tests in `tests/test_reader_disjoint.py` that build known PDFs and assert pairwise substring-containment is impossible and each source marker appears in exactly one `Document`.

### Changed
- Bumped minimum `oxidize-pdf` dependency from `>=0.4.2` to `>=0.4.3`.
- README updated to describe the disjointness guarantee and document the 0.1.0 regression.

### Note
- 0.1.0 was published with shape-only tests (the metadata fields existed; the chunk content was never inspected). 0.1.1 is the first release where the RAG-ready claim is backed by semantic regression tests in both this reader and the underlying bridge. **0.1.0 users should upgrade.**

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
