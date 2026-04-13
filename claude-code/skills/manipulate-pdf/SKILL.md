---
name: manipulate-pdf
description: >
  Split, merge, rotate, reorder, extract pages, overlay PDFs, add annotations,
  and manage form fields. Use when the user wants to combine PDFs, split pages,
  rotate, add sticky notes or highlights, create forms, or fill form fields.
---

# Manipulate PDF

Manipulate PDF documents using `manipulate_pdf`, `annotate_pdf`, and `manage_forms` MCP tools.

## Tool: `manipulate_pdf`

**Parameters:**
- `operation` (required): One of `"split"`, `"merge"`, `"rotate"`, `"extract_pages"`, `"reverse"`, `"overlay"`
- `input_path` (for single-file ops): Source PDF path
- `input_paths` (for merge): List of PDF paths to merge
- `output_path` (required): Destination path (directory for split, file for others)
- `degrees` (for rotate): Rotation angle (90, 180, 270)
- `page_indices` (for extract_pages): List of 0-based page indices to extract
- `overlay_path` (for overlay): Path to the overlay PDF

### Operations

- **split**: Splits PDF into individual page files in `output_path` directory
- **merge**: Combines multiple PDFs from `input_paths` into one file
- **rotate**: Rotates all pages by `degrees`
- **extract_pages**: Extracts specific pages by `page_indices`
- **reverse**: Reverses page order
- **overlay**: Overlays `overlay_path` on top of `input_path`

## Tool: `annotate_pdf`

**Parameters:**
- `input_path` (required): Source PDF
- `output_path` (required): Destination PDF
- `annotation_type` (required): `"text"` (sticky note) or `"highlight"`
- `page` (required): 0-based page index
- `x`, `y` (required): Position in PDF points (origin bottom-left)
- `contents` (optional, for text): Note contents
- `width`, `height` (optional, for highlight): Rectangle dimensions (default 100x20)

## Tool: `manage_forms`

**Parameters:**
- `operation` (required): `"create"`, `"fill"`, `"read"`, `"validate"`
- `output_path` (for create, fill): Destination path
- `input_path` (for fill, read, validate): Source PDF with form
- `fields` (for create): List of field definitions `[{"name", "type", "x", "y", "width", "height", "page"}]`
- `values` (for fill, validate): Dict of `{"field_name": "value"}` pairs

### Form operations

- **create**: Create a new PDF with form fields
- **fill**: Fill form fields and save (overlays on original)
- **read**: Read form structure by extracting text entities
- **validate**: Validate field values against required rules

## Usage patterns

**Merge PDFs:**
`manipulate_pdf(operation="merge", input_paths=["a.pdf", "b.pdf", "c.pdf"], output_path="merged.pdf")`

**Split into pages:**
`manipulate_pdf(operation="split", input_path="doc.pdf", output_path="./pages/")`

**Extract specific pages:**
`manipulate_pdf(operation="extract_pages", input_path="doc.pdf", output_path="excerpt.pdf", page_indices=[0, 2, 5])`

**Add a sticky note:**
`annotate_pdf(input_path="doc.pdf", output_path="annotated.pdf", annotation_type="text", page=0, x=100, y=700, contents="Review this section")`

**Fill a form:**
1. `manage_forms(operation="read", input_path="form.pdf")` — discover fields
2. Map user values to field names
3. `manage_forms(operation="fill", input_path="form.pdf", output_path="filled.pdf", values={"name": "John", "date": "2026-04-13"})`

## Examples

- "Merge these 3 PDFs" → `manipulate_pdf(operation="merge", ...)`
- "Rotate page 2 by 90 degrees" → `manipulate_pdf(operation="rotate", input_path=..., output_path=..., degrees=90)`
- "Extract pages 1, 3, 5" → `manipulate_pdf(operation="extract_pages", page_indices=[0, 2, 4], ...)`
- "Add a note on page 1" → `annotate_pdf(annotation_type="text", page=0, ...)`
- "Fill this tax form" → read first, then fill with values
