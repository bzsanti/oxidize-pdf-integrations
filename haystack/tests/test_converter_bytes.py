"""Native ByteStream support tests.

LangChain and LlamaIndex loaders take only file paths; Haystack accepts
``ByteStream`` objects as first-class sources. The bridge exposes
``PdfReader.from_bytes(data)`` (READ-003), so this converter can honor
the Haystack convention without detouring through temporary files.

These tests guard that optional-but-idiomatic feature: if a future
refactor introduces a ``if isinstance(src, (str, Path))`` guard and
forgets ByteStream, this file fails loudly before release.
"""

from __future__ import annotations

import pathlib

from haystack.dataclasses import ByteStream

from haystack_oxidize_pdf import OxidizePdfConverter


class TestByteStreamInput:
    def test_accepts_bytestream_as_source(self, sample_pdf_bytes: bytes):
        stream = ByteStream(data=sample_pdf_bytes, mime_type="application/pdf")
        docs = OxidizePdfConverter(mode="pages").run(sources=[stream])["documents"]
        assert len(docs) == 2
        assert "Chapter 1" in docs[0].content
        assert "Chapter 2" in docs[1].content

    def test_bytestream_metadata_falls_back_gracefully(
        self, sample_pdf_bytes: bytes
    ):
        # For a ByteStream there is no on-disk path — the adapter must
        # still populate total_pages / pdf_version, and must not crash
        # trying to compute file_name / file_path.
        stream = ByteStream(data=sample_pdf_bytes, mime_type="application/pdf")
        docs = OxidizePdfConverter(mode="pages").run(sources=[stream])["documents"]
        meta = docs[0].meta
        assert meta["total_pages"] == 2
        assert meta["pdf_version"].startswith("1.")
        # file_path and file_name either absent or present with a sentinel.
        # Implementation-defined — we only forbid hard crashes.

    def test_mixed_sources_paths_and_bytestreams(
        self, sample_pdf: pathlib.Path, sample_pdf_bytes: bytes
    ):
        stream = ByteStream(data=sample_pdf_bytes, mime_type="application/pdf")
        docs = OxidizePdfConverter(mode="markdown").run(
            sources=[sample_pdf, stream]
        )["documents"]
        # 2 sources → 2 markdown docs, content identical (same underlying PDF).
        assert len(docs) == 2
        assert docs[0].content == docs[1].content

    def test_bytestream_meta_attribute_is_merged(self, sample_pdf_bytes: bytes):
        # ByteStream can carry its own meta dict; the converter should
        # merge it into the output Document's meta without silently
        # dropping it.
        stream = ByteStream(
            data=sample_pdf_bytes,
            mime_type="application/pdf",
            meta={"upstream_origin": "s3://bucket/key"},
        )
        docs = OxidizePdfConverter(mode="markdown").run(sources=[stream])[
            "documents"
        ]
        assert docs[0].meta.get("upstream_origin") == "s3://bucket/key"
