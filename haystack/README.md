# haystack-oxidize-pdf

Haystack converter backed by [oxidize-pdf](https://github.com/bzsanti/oxidize-python), a fast Rust-powered PDF engine with first-class RAG chunking.

> **0.1.0 (2026-05-19)** — Requires `oxidize-pdf>=0.4.3` (oxidize-pdf-core 2.5.5+).
> Ships from day one with the full semantic regression suite
> (`test_converter_disjoint.py`, 6 tests) that guarantees the
> RAG-chunk disjointness contract end-to-end. Mirrors the discipline
> applied to `langchain-oxidize-pdf` 0.1.0 after the
> `llama-index-readers-oxidize-pdf` 0.1.0 → 0.1.1 incident, where
> shape-only tests missed a quadratic accumulation bug in the
> underlying chunker.

## Install

```bash
pip install haystack-oxidize-pdf
```

## Usage

The converter is a Haystack `@component` and can be dropped straight into a `Pipeline`. Sources accept paths (`str` / `pathlib.Path`) and `ByteStream` objects interchangeably.

### Three modes

| Mode | Output | Use case |
|---|---|---|
| `rag` (default) | one `Document` per RAG chunk with `chunk_index`, `page_numbers`, `element_types`, `heading_context`, `token_estimate` | Vector-store ingestion for RAG |
| `pages` | one `Document` per page (plain text) with `page_number` | Page-level indexing or compatibility with PyPDFToDocument-style pipelines |
| `markdown` | one `Document` per source containing the whole PDF as markdown | Single-document export, no chunking |

### RAG chunks (default)

```python
from haystack_oxidize_pdf import OxidizePdfConverter

converter = OxidizePdfConverter()  # mode="rag"
result = converter.run(sources=["paper.pdf"])

for doc in result["documents"]:
    print(doc.meta["chunk_index"], doc.meta["heading_context"])
    print(doc.content[:200])
```

Each `Document.meta` for `mode="rag"` carries:

| Field | Description |
|---|---|
| `chunk_index` | 0-based index within the source (resets per source in batch mode) |
| `page_numbers` | list of 1-indexed pages covered by the chunk |
| `element_types` | list of semantic types detected (e.g. `title`, `paragraph`) |
| `heading_context` | `"Section title > Subsection"` string, prepended to `content` |
| `token_estimate` | conservative token-count estimate for chunk sizing |
| `file_path`, `file_name`, `total_pages`, `pdf_version` | source-level fields |

### Pipeline integration

```python
from haystack import Pipeline
from haystack_oxidize_pdf import OxidizePdfConverter

pipeline = Pipeline()
pipeline.add_component("converter", OxidizePdfConverter(mode="rag"))
# ...add embedder, writer, etc.

result = pipeline.run({"converter": {"sources": ["paper.pdf"]}})
```

### ByteStream input

Unlike LangChain / LlamaIndex loaders which take only file paths, the Haystack converter accepts `ByteStream` objects natively, leveraging `PdfReader.from_bytes` under the hood:

```python
from haystack.dataclasses import ByteStream
from haystack_oxidize_pdf import OxidizePdfConverter

with open("paper.pdf", "rb") as f:
    stream = ByteStream(data=f.read(), mime_type="application/pdf",
                        meta={"upstream_origin": "s3://bucket/key"})

docs = OxidizePdfConverter().run(sources=[stream])["documents"]
# stream.meta is merged into each Document.meta (here: upstream_origin)
```

### Batch sources with per-source metadata

```python
docs = OxidizePdfConverter(mode="markdown").run(
    sources=["doc-a.pdf", "doc-b.pdf"],
    meta=[{"tag": "first"}, {"tag": "second"}],
)["documents"]
# docs[0].meta["tag"] == "first"
# docs[1].meta["tag"] == "second"
```

Or broadcast a single dict to every output document:

```python
docs = OxidizePdfConverter().run(
    sources=["a.pdf", "b.pdf"], meta={"source_tag": "batch-A"}
)["documents"]
# all docs carry source_tag == "batch-A"
```

### Metadata precedence

Three layers, deepest wins:

1. Base file-level fields (`file_path`, `file_name`, `total_pages`, `pdf_version`).
2. Caller-supplied `meta` (overrides base fields by design, lets callers re-label).
3. Per-document fields (`chunk_index`, `page_numbers`, `page_number`) applied last and never overwritten.

## Related packages

- [`langchain-oxidize-pdf`](https://pypi.org/project/langchain-oxidize-pdf/) — same engine, LangChain `BaseLoader` interface.
- [`llama-index-readers-oxidize-pdf`](https://pypi.org/project/llama-index-readers-oxidize-pdf/) — same engine, LlamaIndex `BaseReader` interface.
- [`oxidize-pdf`](https://pypi.org/project/oxidize-pdf/) — the underlying PyO3 bridge (also ships the `oxidize-mcp` MCP server entry point).
- [`OxidizePdf.NET`](https://www.nuget.org/packages/OxidizePdf.NET) — .NET bindings.
- [oxidize-pdf core (Rust)](https://crates.io/crates/oxidize-pdf) — the Rust engine, 99.3% parse success on 9k+ real-world PDFs.

## License

MIT.
