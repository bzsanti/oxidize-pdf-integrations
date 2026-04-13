---
name: analyze-pdf
description: >
  Analyze PDF structure, validate integrity, detect corruption, check PDF/A
  compliance, compare two documents, and extract structured entities (text chunks
  with position and font info). Use when the user wants to validate, audit,
  compare, or deeply inspect PDF documents.
---

# Analyze PDF

Analyze and inspect PDF documents using `analyze_pdf` and `extract_entities` MCP tools.

## Tool: `analyze_pdf`

**Parameters:**
- `path` (required): Path to the PDF file
- `check` (optional, default "validate"): Analysis mode — one of:
  - `"validate"` — Check structural validity, report error/warning counts
  - `"corruption"` — Detect corruption, report severity and type
  - `"compliance"` — Check PDF/A compliance against a specific level
  - `"compare"` — Compare two PDFs for structural and content equivalence
- `compare_path` (required for compare): Path to the second PDF
- `compliance_level` (optional, default "a1b"): PDF/A level — `a1a`, `a1b`, `a2a`, `a2b`, `a2u`, `a3a`, `a3b`, `a3u`

**Returns by mode:**
- validate: `{"valid", "error_count", "warning_count"}`
- corruption: `{"corrupted", "corruption_type", "severity", "found_pages", "file_size", "errors"}`
- compliance: `{"level", "is_valid", "error_count", "warning_count", "compliance_percentage"}`
- compare: `{"structurally_equivalent", "content_equivalent", "similarity_score", "difference_count"}`

## Tool: `extract_entities`

**Parameters:**
- `path` (required): Path to the PDF file

**Returns:** `{"entities": [{"text", "page", "x", "y", "font_size", "font_name"}], "entity_count", "page_count"}`

Extracts every text chunk with its position, font, and page index. Use for detailed layout analysis or when you need to understand document structure beyond plain text.

## Usage patterns

**Quick validation:**
Call `analyze_pdf` with default `check="validate"`. Report whether the PDF is valid and any error/warning counts.

**Corruption check:**
Use `check="corruption"`. Severity 0 = no corruption. Higher values indicate more severe issues.

**PDF/A compliance:**
Use `check="compliance"`. The `compliance_percentage` shows how close the document is to meeting the standard.

**Document comparison:**
Use `check="compare"` with both `path` and `compare_path`. Report similarity score and differences.

**Layout analysis:**
Use `extract_entities` to get text positions. Useful for understanding document layout, finding headers, or locating specific content regions.

**Comprehensive audit:**
Chain multiple calls: validate → corruption → compliance → extract_entities for a full document report.

## Examples

- "Is this PDF valid?" → `analyze_pdf(path="doc.pdf")`
- "Check for corruption" → `analyze_pdf(path="doc.pdf", check="corruption")`
- "Is this PDF/A-2b compliant?" → `analyze_pdf(path="doc.pdf", check="compliance", compliance_level="a2b")`
- "Compare these two PDFs" → `analyze_pdf(path="v1.pdf", check="compare", compare_path="v2.pdf")`
- "Show me the document layout" → `extract_entities(path="doc.pdf")`
