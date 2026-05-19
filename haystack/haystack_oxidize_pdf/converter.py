"""Haystack PDF converter component backed by oxidize-pdf."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Optional, Union

from haystack import component
from haystack.dataclasses import ByteStream, Document

import oxidize_pdf as _ox

ConverterMode = Literal["rag", "pages", "markdown"]
Source = Union[str, Path, ByteStream]
SourceMeta = Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]


@component
class OxidizePdfConverter:
    """PDF converter powered by oxidize-pdf, exposed as a Haystack ``@component``.

    Three modes control how each source is converted into ``Document`` objects:

    - ``"rag"`` (default): one ``Document`` per RAG chunk produced by
      oxidize-pdf's semantic chunker. Per-chunk metadata exposes
      ``chunk_index``, ``page_numbers`` (1-indexed), ``element_types``,
      ``heading_context`` and ``token_estimate``. ``chunk_index`` resets to
      0 at the start of each source.
    - ``"pages"``: one ``Document`` per page (plain text); metadata carries
      ``page_number`` (1-indexed).
    - ``"markdown"``: a single ``Document`` per source containing the whole
      PDF as markdown (via oxidize-pdf's ``MarkdownExporter``); no
      ``page_number`` is emitted.

    The component accepts paths (``str`` / ``pathlib.Path``) and
    ``ByteStream`` instances interchangeably as sources. ``ByteStream.meta``
    is merged into the output ``Document.meta``; for ByteStream sources
    there is no on-disk path, so ``file_path`` / ``file_name`` are omitted.

    Caller-supplied ``meta`` may be a single dict (broadcast to all output
    documents) or a list of dicts (scoped per source). Caller meta has
    precedence over base file-level fields, but per-document fields
    (``page_number``, ``chunk_index``, etc.) are applied last and cannot be
    silently overwritten by the caller.
    """

    def __init__(self, mode: ConverterMode = "rag") -> None:
        if mode not in ("rag", "pages", "markdown"):
            raise ValueError(
                f"Unknown mode {mode!r}; expected 'rag', 'pages', or 'markdown'."
            )
        self.mode: ConverterMode = mode

    @component.output_types(documents=List[Document])
    def run(
        self,
        sources: List[Source],
        meta: SourceMeta = None,
    ) -> Dict[str, List[Document]]:
        if not sources:
            return {"documents": []}

        if isinstance(meta, list) and len(meta) != len(sources):
            raise ValueError(
                f"meta is a list of length {len(meta)} but sources has length "
                f"{len(sources)}; when meta is a list, lengths must match."
            )

        all_docs: List[Document] = []
        for idx, src in enumerate(sources):
            caller_meta: Optional[Dict[str, Any]]
            if isinstance(meta, list):
                caller_meta = meta[idx]
            elif isinstance(meta, dict):
                caller_meta = meta
            else:
                caller_meta = None

            reader, base_meta = self._open_source(src)
            combined_base = {**base_meta, **caller_meta} if caller_meta else base_meta

            if self.mode == "rag":
                all_docs.extend(self._iter_rag(reader, combined_base))
            elif self.mode == "pages":
                all_docs.extend(self._iter_pages(reader, combined_base))
            else:
                all_docs.extend(self._iter_markdown(reader, combined_base))

        return {"documents": all_docs}

    @staticmethod
    def _open_source(src: Source) -> tuple["_ox.PdfReader", Dict[str, Any]]:
        if isinstance(src, ByteStream):
            reader = _ox.PdfReader.from_bytes(src.data)
            base_meta: Dict[str, Any] = {
                "total_pages": reader.page_count,
                "pdf_version": reader.version,
            }
            stream_meta = getattr(src, "meta", None) or {}
            if stream_meta:
                base_meta.update(stream_meta)
            return reader, base_meta

        path = Path(src)
        reader = _ox.PdfReader.open(str(path))
        base_meta = {
            "file_path": str(path),
            "file_name": path.name,
            "total_pages": reader.page_count,
            "pdf_version": reader.version,
        }
        return reader, base_meta

    @staticmethod
    def _iter_rag(
        reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> Iterator[Document]:
        for chunk in reader.rag_chunks():
            yield Document(
                content=chunk.full_text,
                meta={
                    **base_meta,
                    "chunk_index": chunk.chunk_index,
                    "page_numbers": [pn + 1 for pn in chunk.page_numbers],
                    "element_types": list(chunk.element_types),
                    "heading_context": chunk.heading_context,
                    "token_estimate": chunk.token_estimate,
                },
            )

    @staticmethod
    def _iter_pages(
        reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> Iterator[Document]:
        for i, page_text in enumerate(reader.extract_text()):
            yield Document(
                content=page_text,
                meta={**base_meta, "page_number": i + 1},
            )

    @staticmethod
    def _iter_markdown(
        reader: "_ox.PdfReader", base_meta: Dict[str, Any]
    ) -> Iterator[Document]:
        pages = reader.extract_text()
        exporter = _ox.MarkdownExporter.default()
        body = "\n\n".join(exporter.export(page) for page in pages)
        yield Document(content=body, meta=dict(base_meta))
