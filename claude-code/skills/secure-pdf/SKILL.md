---
name: secure-pdf
description: >
  Encrypt PDFs with passwords, check encryption status and permissions, and verify
  digital signatures. Use when the user wants to password-protect a PDF, check if
  a PDF is encrypted, inspect permissions, or verify signatures.
---

# Secure PDF

Secure PDF operations using the `secure_pdf` MCP tool.

## Tool: `secure_pdf`

**Parameters:**
- `operation` (required): One of `"encrypt"`, `"permissions"`, `"verify_signatures"`
- `input_path` (required for all operations): Path to the source PDF
- `output_path` (required for encrypt): Path to save the encrypted PDF
- `user_password` (required for encrypt): Password users need to open the PDF
- `owner_password` (required for encrypt): Password for full access (editing, printing)
- `password` (optional for permissions): Password to unlock and check a locked PDF

## Operations

### encrypt

Encrypts a PDF with user and owner passwords. Both passwords are required.

**Important limitation:** Encryption reconstructs the document preserving text content and layout, but may lose non-text elements (images, embedded fonts, vector graphics). Warn the user about this before encrypting documents with images.

**Returns:** `{"status": "ok", "operation": "encrypt", "page_count": N, "note": "..."}`

### permissions

Checks if a PDF is encrypted and reports its status. Pass a `password` to unlock and inspect a locked PDF.

**Returns:** `{"path", "is_encrypted", "unlocked", "permissions": {"encrypted": bool}}`

### verify_signatures

Verifies digital signatures in a PDF. Reports each signature's validity and signer.

**Returns:** `{"path", "signatures": [{"valid", "signer"}], "signature_count": N}`

## Usage patterns

**Encrypt a PDF:**
1. First `read_pdf` to confirm the document content
2. Warn user about non-text element limitation
3. Call `secure_pdf(operation="encrypt", input_path=..., output_path=..., user_password=..., owner_password=...)`

**Check encryption status:**
Call `secure_pdf(operation="permissions", input_path=...)`.

**Verify signatures:**
Call `secure_pdf(operation="verify_signatures", input_path=...)`. Report how many signatures were found and whether each is valid.

## Examples

- "Encrypt report.pdf with password 'secret'" → `secure_pdf(operation="encrypt", input_path="report.pdf", output_path="report_encrypted.pdf", user_password="secret", owner_password="secret")`
- "Is this PDF encrypted?" → `secure_pdf(operation="permissions", input_path="doc.pdf")`
- "Check digital signatures" → `secure_pdf(operation="verify_signatures", input_path="signed.pdf")`
