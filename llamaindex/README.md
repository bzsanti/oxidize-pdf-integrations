# llama-index-readers-oxidize-pdf

LlamaIndex reader backed by [oxidize-pdf](https://github.com/bzsanti/oxidize-python), a fast Rust-powered PDF engine with first-class RAG chunking.

> **0.1.1 (2026-04-22)** — Requires `oxidize-pdf>=0.4.3` (oxidize-pdf-core 2.5.5).
> Fixes a regression carried by 0.1.0: the underlying `HybridChunker` in
> oxidize-pdf-core 2.5.4 re-injected just-flushed elements through its
> overlap branch, so each `Document` produced by `mode="rag"` contained
> the previous one as a prefix (quadratic accumulation). 0.1.1 is the
> first release where the disjointness contract is verified end-to-end
> by semantic regression tests; **0.1.0 should not be used for RAG ingestion**.

## Install

```bash
pip install llama-index-readers-oxidize-pdf
```

## Usage

### RAG chunks (default)

```python
from llama_index.readers.oxidize_pdf import OxidizePdfReader

reader = OxidizePdfReader()  # mode="rag" by default
documents = reader.load_data("paper.pdf")

for doc in documents:
    print(doc.metadata["chunk_index"], doc.metadata["heading_context"])
    print(doc.text[:200])
```

Each ``Document`` carries:

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
reader = OxidizePdfReader(mode="pages")
docs = reader.load_data("paper.pdf")
for doc in docs:
    print(doc.metadata["page_number"], len(doc.text))
```

### Whole PDF as markdown

```python
reader = OxidizePdfReader(mode="markdown")
[doc] = reader.load_data("paper.pdf")
print(doc.text)
```

## Why oxidize-pdf

- **Rust parser**: fast on large PDFs, low memory footprint.
- **Native RAG primitives**: element-disjoint semantic chunking, element partitioning, heading-aware context — no post-processing needed. The disjointness contract (no chunk's text is a substring of another's; each source element appears in exactly one chunk) is enforced by regression tests in both this reader and the underlying bridge.
- **CJK friendly**: compact output for multibyte documents (see oxidize-pdf 2.5.4 subsetter fixes).
- **Pure Python install**: ships as a wheel for Linux/macOS/Windows via the `oxidize-pdf` package; no system dependencies.

## Source

Part of [oxidize-pdf-integrations](https://github.com/bzsanti/oxidize-pdf-integrations), the ecosystem of integrations around oxidize-pdf. The Rust core and Python bridge live in [oxidize-python](https://github.com/bzsanti/oxidize-python).

## License

MIT
