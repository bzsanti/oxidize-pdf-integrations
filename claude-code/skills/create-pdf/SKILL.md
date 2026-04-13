---
name: create-pdf
description: >
  Create new PDF documents from scratch with text and styling. Use when the user
  wants to generate a new PDF, create a report, build an invoice, or compose
  any document from scratch.
---

# Create PDF

Create new PDF documents using a stateful three-step workflow: `create_pdf` → `add_pdf_content` (repeat) → `save_pdf`.

## Step 1: Start session with `create_pdf`

**Parameters:**
- `title` (required): Document title
- `author` (optional): Document author
- `page_size` (optional, default "a4"): Page size — use `oxidize://page-sizes` resource for available options

**Returns:** `{"session_id": "...", "status": "created", "page_size": "a4"}`

Save the `session_id` — it is required for all subsequent calls.

## Step 2: Add content with `add_pdf_content`

**Parameters:**
- `session_id` (required): From step 1
- `content_type` (required): `"text"` or `"new_page"`
- `content` (for text): The text string to add
- `x`, `y` (for text): Position in PDF points (origin is bottom-left, 72 points = 1 inch)
- `font` (optional): Font name — use `oxidize://fonts` resource for available options
- `font_size` (optional, default 12.0): Font size in points

Call this tool multiple times to build up the document content. Use `content_type="new_page"` to add additional pages.

## Step 3: Save with `save_pdf`

**Parameters:**
- `session_id` (required): From step 1
- `output_path` (required): Where to save the PDF file
- `user_password` (optional): Set user password for encryption
- `owner_password` (optional): Set owner password for encryption

**Returns:** `{"status": "ok", "path": "...", "page_count": N}`

## Coordinate system

- Origin (0, 0) is at the **bottom-left** of the page
- X increases to the right, Y increases upward
- A4 dimensions: 595.28 x 841.89 points
- Letter dimensions: 612.0 x 792.0 points
- Title at top of A4: y ~ 800, body text starts at y ~ 750, decreasing ~15 per line

## Usage patterns

**Simple document:**
1. `create_pdf(title="My Report")`
2. `add_pdf_content(session_id=ID, content_type="text", content="Title", x=50, y=800, font_size=24)`
3. `add_pdf_content(session_id=ID, content_type="text", content="Body text...", x=50, y=750, font_size=12)`
4. `save_pdf(session_id=ID, output_path="report.pdf")`

**Multi-page document:**
After filling a page, call `add_pdf_content(session_id=ID, content_type="new_page")` then continue adding text to the new page starting at the top (y ~ 800 for A4).

**Encrypted document:**
Pass both `user_password` and `owner_password` to `save_pdf`.

## Examples

- "Create a one-page report" → create_pdf + add_pdf_content (text) + save_pdf
- "Make an invoice for Acme Corp" → create_pdf(title="Invoice - Acme Corp") + multiple add_pdf_content + save_pdf
- "Create an encrypted PDF" → full workflow + save_pdf with passwords
