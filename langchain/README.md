# langchain-oxidize-pdf

LangChain document loader backed by [oxidize-pdf](https://github.com/bzsanti/oxidize-python), a fast Rust-powered PDF engine with first-class RAG chunking.

> **0.1.0 (2026-04-24)** — Requires `oxidize-pdf>=0.4.3` (oxidize-pdf-core 2.5.5).
> First release. The sibling `llama-index-readers-oxidize-pdf` 0.1.0 shipped
> with shape-only tests that missed a quadratic accumulation bug in the
> underlying chunker; this loader ships from day one with the semantic
> regression suite (`test_loader_disjoint.py`) that guarantees the
> disjointness contract end-to-end.

## Install

```bash
pip install langchain-oxidize-pdf
```

## Usage

LangChain convention binds the file path to the loader instance and
uses `lazy_load()` as the primary entry point; `load()` is inherited
from `BaseLoader` as a convenience that materializes the iterator.

### RAG chunks (default)

```python
from langchain_oxidize_pdf import OxidizePdfLoader

loader = OxidizePdfLoader("paper.pdf")  # mode="rag" by default
documents = loader.load()

for doc in documents:
    print(doc.metadata["chunk_index"], doc.metadata["heading_context"])
    print(doc.page_content[:200])
```

Each `Document` carries:

| Field | Description |
|---|---|
| `chunk_index` | 0-based index within the document |
| `page_numbers` | list of 1-indexed pages covered by the chunk |
| `element_types` | list of semantic types detected (e.g. `title`, `paragraph`) |
| `heading_context` | nearest surrounding heading, or `None` |
| `token_estimate` | rough token count for budget planning |
| `file_path` / `file_name` / `total_pages` / `pdf_version` | source metadata |

### One document per page

```python
loader = OxidizePdfLoader("paper.pdf", mode="pages")
for doc in loader.lazy_load():
    print(doc.metadata["page_number"], len(doc.page_content))
```

### Whole PDF as markdown

```python
loader = OxidizePdfLoader("paper.pdf", mode="markdown")
[doc] = loader.load()
print(doc.page_content)
```

### Adding caller metadata

```python
loader = OxidizePdfLoader(
    "paper.pdf",
    extra_info={"source": "arxiv:2501.12345", "collection": "benchmarks"},
)
```

Keys in `extra_info` override base metadata (`file_path`, `file_name`,
`total_pages`, `pdf_version`) if they collide — explicit caller intent.

## Why oxidize-pdf

- **Rust parser**: fast on large PDFs, low memory footprint.
- **Native RAG primitives**: element-disjoint semantic chunking, element partitioning, heading-aware context — no post-processing needed. The disjointness contract (no chunk's text is a substring of another's; each source element appears in exactly one chunk) is enforced by regression tests in both this loader and the underlying bridge.
- **CJK friendly**: compact output for multibyte documents (see oxidize-pdf 2.5.4 subsetter fixes).
- **Pure Python install**: ships as a wheel for Linux/macOS/Windows via the `oxidize-pdf` package; no system dependencies.
- **Real lazy loading**: `lazy_load()` returns a generator, so large PDFs don't force every `Document` into memory upfront.

## Source

Part of [oxidize-pdf-integrations](https://github.com/bzsanti/oxidize-pdf-integrations), the ecosystem of integrations around oxidize-pdf. The Rust core and Python bridge live in [oxidize-python](https://github.com/bzsanti/oxidize-python).

## License

MIT
