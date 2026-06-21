# Changelog

This repo hosts multiple integrations; each section is scoped per integration.
See [RELEASING.md](./RELEASING.md) for tag and versioning conventions.

## [mcp-v0.12.0] - 2026-06-21

### Changed
- Track `oxidize-pdf` **0.12.0** (was 0.11.0): `mcp/server.json` `version` and `packages[0].version` bumped to 0.12.0. The MCP server runs the `oxidize-mcp` entry point shipped in the `oxidize-pdf` PyPI wheel, so this pins the registry entry to the 0.12.0 bridge — an MCP-only release that overhauls the Tool Definition Quality of all 12 tools (no upstream change, `oxidize-pdf` stays 2.16.3). Every tool now ships per-parameter descriptions (units in PDF points, 0-based page indices, bottom-left coordinate origin, defaults, mode applicability), MCP `ToolAnnotations` (`title`, `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint=False`), descriptions that distinguish sibling tools and state when to use each (and the alternative when not), and honest behavioural/return disclosure. Free-form mode parameters (`operation`, `check`, `content_type`, `compliance_level`, `page_size`, `annotation_type`) are now `Literal` enums surfaced in the JSON schema, so an unknown value is rejected by schema validation before the tool runs. This raises Glama's Tool Definition Quality Score for the listed server. Published to the MCP Registry via the `publish-mcp` workflow (`workflow_dispatch`, version `0.12.0`).

## [mcp-v0.11.0] - 2026-06-21

### Changed
- Track `oxidize-pdf` **0.11.0** (was 0.10.0): `mcp/server.json` `version` and `packages[0].version` bumped to 0.11.0. The MCP server runs the `oxidize-mcp` entry point shipped in the `oxidize-pdf` PyPI wheel, so this pins the registry entry to the 0.11.0 bridge — bringing upstream `oxidize-pdf` 2.16.3 with the new experimental Analysis SPI surfaced in `oxidize_pdf.experimental` (`AnalysisPipeline` builder + `PdfReader.rag_chunks_with_pipeline` for pluggable chunking/classification/metadata-enrichment, semver-exempt matching the upstream `unstable-spi` contract), the always-on enriched `RagChunk` metadata (21 new getters: `heading_path`, `dominant_font[_size]`, `is_bold`/`is_italic`, `content_types`, char/word/sentence counts, ISO 639-3 language detection, `chunk_id` chain, `page_span`/`page_regions`), and document-source stamping. Inherited upstream 2.16.1–2.16.3 bug fixes (xref-stream double-decode #341, bounded-memory lenient parse #339, deterministic extraction/XMP #329/#331/#334) with no bridge API change. The native extension now ships a single abi3 (stable ABI) `cp310-abi3` wheel covering Python 3.10+, which also resolved the Windows 3.13 link failure (LNK1181 `python313.lib`). Non-breaking, additive at the stable API level. Published to the MCP Registry via the `publish-mcp` workflow (`workflow_dispatch`, version `0.11.0`).

## [mcp-v0.10.0] - 2026-06-14

### Changed
- Track `oxidize-pdf` **0.10.0** (was 0.9.0): `mcp/server.json` `version` and `packages[0].version` bumped to 0.10.0. The MCP server runs the `oxidize-mcp` entry point shipped in the `oxidize-pdf` PyPI wheel, so this pins the registry entry to the 0.10.0 bridge — bringing upstream `oxidize-pdf` 2.15.0 with the new `IncrementalFormFiller`: AcroForm fields are filled on an already-serialized PDF by appending an ISO 32000-1 §7.5.6 incremental update (original bytes preserved verbatim, only the modified field objects and `/AcroForm` rewritten in a new revision with a partial cross-reference section, chained `/Prev` and regenerated `/ID`, #318), plus inherited text-extraction fixes (#319): content-stream parsing is now best-effort (a single malformed operator no longer discards a whole page) and text drawn inside a Form XObject invoked with `Do` is now extracted (277 files recover previously-dropped text in the upstream 9051-PDF corpus). Published to the MCP Registry via the `publish-mcp` workflow (`workflow_dispatch`, version `0.10.0`).

## [mcp-v0.9.0] - 2026-06-11

### Changed
- Track `oxidize-pdf` **0.9.0** (was 0.8.0): `mcp/server.json` `version` and `packages[0].version` bumped to 0.9.0. The MCP server runs the `oxidize-mcp` entry point shipped in the `oxidize-pdf` PyPI wheel, so this pins the registry entry to the 0.9.0 bridge — bringing upstream `oxidize-pdf` 2.14.0 with real axial/radial gradient rendering (a shading now emits a proper PDF `/Function` Type 2/Type 3 plus `/ColorSpace` instead of the placeholder `/Function 1`, #297) exposed through the new `Page.add_shading` / `Page.paint_shading` / `Page.clip` / `Page.clip_even_odd` / `Page.end_path` paint path, plus inherited text-extraction fixes: word scramble in dense and multi-column documents (#302, #305), the `DocumentChunker::chunk_text` infinite-loop guard (#308), and non-ASCII WinAnsi glyph measurement corrections (#309, #313). Published to the MCP Registry via the `publish-mcp` workflow (`workflow_dispatch`, version `0.9.0`).

## [mcp-v0.8.0] - 2026-06-08

### Changed
- Track `oxidize-pdf` **0.8.0** (was 0.7.0): `mcp/server.json` `version` and `packages[0].version` bumped to 0.8.0. The MCP server runs the `oxidize-mcp` entry point shipped in the `oxidize-pdf` PyPI wheel, so this pins the registry entry to the 0.8.0 bridge — bringing upstream `oxidize-pdf` 2.13.0, per-chunk/document RAG language detection (#293), the token-efficient and JSON chunk exporters (#291), the `prefer_ruling_tables` partition flag (#292), and the `/SMask` alpha + flate-ratio image-extraction fixes (#286). MSRV raised to Rust 1.88. Published to the MCP Registry via the `publish-mcp` workflow (`workflow_dispatch`, version `0.8.0`).

## [mcp-v0.7.0] - 2026-06-04

### Changed
- Track `oxidize-pdf` **0.7.0** (was 0.5.0): `mcp/server.json` `version` and `packages[0].version` bumped to 0.7.0. The MCP server runs the `oxidize-mcp` entry point shipped in the `oxidize-pdf` PyPI wheel, so this pins the registry entry to the 0.7.0 bridge — bringing upstream `oxidize-pdf` 2.12.0, GFX-019 colour spaces, the `add_page`-by-reference fix (#80), custom-font measurement (#78), and glyph-coverage diagnostics (#287). Published to the MCP Registry via the `publish-mcp` workflow (`workflow_dispatch`, version `0.7.0`).

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
