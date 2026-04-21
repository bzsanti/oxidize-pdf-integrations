"""LlamaIndex reader backed by oxidize-pdf."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document

import oxidize_pdf as _ox

ReaderMode = Literal["rag", "pages", "markdown"]


class OxidizePdfReader(BaseReader):
    """PDF reader powered by oxidize-pdf.

    Three modes control how the PDF is turned into ``Document`` objects:

    - ``"rag"`` (default): one ``Document`` per RAG chunk, built with
      oxidize-pdf's semantic chunker. Metadata exposes ``chunk_index``,
      ``page_numbers``, ``element_types``, ``heading_context``, and
      ``token_estimate``. Best for vector-store ingestion pipelines.
    - ``"pages"``: one ``Document`` per page (plain text). Best for
      compatibility with pipelines that expect page-level splits.
    - ``"markdown"``: a single ``Document`` containing the whole PDF as
      markdown (via oxidize-pdf's ``MarkdownExporter``).
    """

    def __init__(self, mode: ReaderMode = "rag") -> None:
        if mode not in ("rag", "pages", "markdown"):
            raise ValueError(
                f"Unknown mode {mode!r}; expected 'rag', 'pages', or 'markdown'."
            )
        self.mode: ReaderMode = mode

    def load_data(
        self,
        file: Union[str, Path],
        extra_info: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        path = Path(file)
        reader = _ox.PdfReader.open(str(path))
        base_meta: Dict[str, Any] = {
            "file_path": str(path),
            "file_name": path.name,
            "total_pages": reader.page_count,
            "pdf_version": reader.version,
        }
        if extra_info:
            base_meta.update(extra_info)

        if self.mode == "rag":
            return self._load_rag(reader, base_meta)
        if self.mode == "pages":
            return self._load_pages(reader, base_meta)
        return self._load_markdown(reader, base_meta)

    def _load_rag(
        self, reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> List[Document]:
        chunks = reader.rag_chunks()
        return [
            Document(
                text=chunk.full_text,
                metadata={
                    **base_meta,
                    "chunk_index": chunk.chunk_index,
                    # oxidize-pdf's RagChunk emits 0-indexed pages; LlamaIndex
                    # and this reader's "pages" mode are 1-indexed. Normalize
                    # so metadata is consistent across modes.
                    "page_numbers": [pn + 1 for pn in chunk.page_numbers],
                    "element_types": list(chunk.element_types),
                    "heading_context": chunk.heading_context,
                    "token_estimate": chunk.token_estimate,
                },
            )
            for chunk in chunks
        ]

    def _load_pages(
        self, reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> List[Document]:
        return [
            Document(
                text=page_text,
                metadata={**base_meta, "page_number": i + 1},
            )
            for i, page_text in enumerate(reader.extract_text())
        ]

    def _load_markdown(
        self, reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> List[Document]:
        pages = reader.extract_text()
        exporter = _ox.MarkdownExporter.default()
        body = "\n\n".join(exporter.export(page) for page in pages)
        return [Document(text=body, metadata=base_meta)]
