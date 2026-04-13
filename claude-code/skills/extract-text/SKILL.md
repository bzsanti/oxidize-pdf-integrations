---
name: extract-text
description: >
  Extract text content from PDF documents and convert PDFs to markdown, chunks,
  or RAG format. Use when the user wants text from a PDF, needs to search within
  a PDF, or wants to convert PDF to another text representation.
---

# Extract Text

Extract text content from PDFs and convert to different formats using `extract_text` and `convert_pdf` MCP tools.

## Tool: `extract_text`

**Parameters:**
- `path` (required): Path to the PDF file
- `page` (optional): Specific page index (0-based) to extract from
- `password` (optional): Password for encrypted PDFs

**Returns:** JSON with `text` (extracted content), `page_count`, and optionally `page` index.

## Tool: `convert_pdf`

**Parameters:**
- `path` (required): Path to the PDF file
- `format` (required): One of `"markdown"`, `"chunks"`, `"rag"`
- `password` (optional): Password for encrypted PDFs
- `max_tokens` (optional, default 256): Token limit per chunk (for `chunks` format)
- `overlap` (optional, default 50): Token overlap between chunks (for `chunks` format)

**Returns:**
- `markdown`: `{"content": "...", "format": "markdown"}`
- `chunks`: `{"chunks": [{"id", "content", "tokens", "chunk_index", "page_numbers"}], "format": "chunks"}`
- `rag`: `{"chunks": [{"text", "chunk_index", "page_numbers", "token_estimate", "heading_context"}], "format": "rag"}`

## Usage patterns

**Full text extraction:**
Call `extract_text` with just the path. The entire document text is returned.

**Single page:**
Use the `page` parameter (0-based index). Good when the user says "page 3" — pass `page=2`.

**Markdown conversion:**
Use `convert_pdf` with `format="markdown"` for structured output with headings and formatting.

**RAG ingestion:**
Use `convert_pdf` with `format="rag"` for semantic chunks with heading context, optimized for embedding.

**LLM-sized chunks:**
Use `convert_pdf` with `format="chunks"` and adjust `max_tokens` for your context window.

## Examples

- "Extract text from report.pdf" → `extract_text(path="report.pdf")`
- "Get text from page 5" → `extract_text(path="doc.pdf", page=4)`
- "Convert to markdown" → `convert_pdf(path="doc.pdf", format="markdown")`
- "Prepare for RAG" → `convert_pdf(path="doc.pdf", format="rag")`
- "Split into 512-token chunks" → `convert_pdf(path="doc.pdf", format="chunks", max_tokens=512)`
