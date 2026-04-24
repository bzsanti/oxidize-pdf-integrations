"""LangChain document loader backed by oxidize-pdf."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, Literal, Optional, Union

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

import oxidize_pdf as _ox

LoaderMode = Literal["rag", "pages", "markdown"]


class OxidizePdfLoader(BaseLoader):
    """PDF document loader powered by oxidize-pdf.

    Three modes control how the PDF is turned into ``Document`` objects:

    - ``"rag"`` (default): one ``Document`` per RAG chunk, built with
      oxidize-pdf's semantic chunker. Metadata exposes ``chunk_index``,
      ``page_numbers`` (1-indexed), ``element_types``,
      ``heading_context`` and ``token_estimate``. Best for vector-store
      ingestion pipelines.
    - ``"pages"``: one ``Document`` per page (plain text). Best for
      compatibility with pipelines that expect page-level splits.
    - ``"markdown"``: a single ``Document`` containing the whole PDF as
      markdown (via oxidize-pdf's ``MarkdownExporter``).

    Follows LangChain conventions: the file path is bound in
    ``__init__``, and ``lazy_load()`` is the primary entry point —
    ``load()`` is inherited as the convenience materializer.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        mode: LoaderMode = "rag",
        extra_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        if mode not in ("rag", "pages", "markdown"):
            raise ValueError(
                f"Unknown mode {mode!r}; expected 'rag', 'pages', or 'markdown'."
            )
        self.file_path: str = str(file_path)
        self.mode: LoaderMode = mode
        self.extra_info: Optional[Dict[str, Any]] = extra_info

    def lazy_load(self) -> Iterator[Document]:
        path = Path(self.file_path)
        reader = _ox.PdfReader.open(str(path))
        base_meta: Dict[str, Any] = {
            "file_path": str(path),
            "file_name": path.name,
            "total_pages": reader.page_count,
            "pdf_version": reader.version,
        }
        if self.extra_info:
            base_meta.update(self.extra_info)

        if self.mode == "rag":
            yield from self._iter_rag(reader, base_meta)
        elif self.mode == "pages":
            yield from self._iter_pages(reader, base_meta)
        else:
            yield from self._iter_markdown(reader, base_meta)

    def _iter_rag(
        self, reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> Iterator[Document]:
        for chunk in reader.rag_chunks():
            yield Document(
                page_content=chunk.full_text,
                metadata={
                    **base_meta,
                    "chunk_index": chunk.chunk_index,
                    # oxidize-pdf's RagChunk emits 0-indexed pages; LangChain's
                    # PyPDFLoader (and this loader's "pages" mode) are 1-indexed.
                    # Normalize so metadata is consistent across modes.
                    "page_numbers": [pn + 1 for pn in chunk.page_numbers],
                    "element_types": list(chunk.element_types),
                    "heading_context": chunk.heading_context,
                    "token_estimate": chunk.token_estimate,
                },
            )

    def _iter_pages(
        self, reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> Iterator[Document]:
        for i, page_text in enumerate(reader.extract_text()):
            yield Document(
                page_content=page_text,
                metadata={**base_meta, "page_number": i + 1},
            )

    def _iter_markdown(
        self, reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> Iterator[Document]:
        pages = reader.extract_text()
        exporter = _ox.MarkdownExporter.default()
        body = "\n\n".join(exporter.export(page) for page in pages)
        yield Document(page_content=body, metadata=base_meta)
