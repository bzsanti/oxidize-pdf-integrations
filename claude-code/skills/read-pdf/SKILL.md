---
name: read-pdf
description: >
  Read PDF metadata, page count, and document information. Use when the user wants
  to open, inspect, or get info about a PDF file — page count, title, author,
  encryption status, or per-page dimensions.
---

# Read PDF

Read metadata and structural information from a PDF file using the `read_pdf` MCP tool.

## Tool: `read_pdf`

**Parameters:**
- `path` (required): Path to the PDF file
- `password` (optional): Password to unlock encrypted PDFs
- `include_page_details` (optional, default false): Include per-page width, height, and rotation

**Returns:** JSON with `page_count`, `is_encrypted`, `version`, `title`, `author`, `subject`, `keywords`. When `include_page_details=true`, includes a `pages` array with `index`, `width`, `height`, `rotation` per page.

## Usage patterns

**Basic metadata:**
Call `read_pdf` with the file path. Report the page count, title, author, and encryption status.

**Encrypted PDFs:**
If the response includes `"locked": true`, ask the user for a password and retry with the `password` parameter.

**Page dimensions:**
When the user asks about page sizes or layout, use `include_page_details=true` to get width/height per page. Dimensions are in PDF points (72 points = 1 inch).

## Examples

- "What's in report.pdf?" → `read_pdf(path="report.pdf")`
- "How many pages?" → `read_pdf(path="doc.pdf")` then report `page_count`
- "Is this encrypted?" → `read_pdf(path="secret.pdf")` then check `is_encrypted`
- "What are the page dimensions?" → `read_pdf(path="doc.pdf", include_page_details=true)`
