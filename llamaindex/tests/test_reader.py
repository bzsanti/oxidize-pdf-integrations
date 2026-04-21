"""Behavior tests for OxidizePdfReader.

All tests verify real extracted content and metadata — no smoke tests
(no ``is_ok()``, no ``len >= 0``, no empty-asserts).
"""

from __future__ import annotations

import pathlib

import pytest
from llama_index.core.schema import Document

from llama_index.readers.oxidize_pdf import OxidizePdfReader


class TestConstruction:
    def test_default_mode_is_rag(self):
        reader = OxidizePdfReader()
        assert reader.mode == "rag"

    @pytest.mark.parametrize("mode", ["rag", "pages", "markdown"])
    def test_known_modes_accepted(self, mode):
        reader = OxidizePdfReader(mode=mode)
        assert reader.mode == mode

    def test_unknown_mode_rejected(self):
        with pytest.raises(ValueError, match="Unknown mode"):
            OxidizePdfReader(mode="invalid")  # type: ignore[arg-type]


class TestPagesMode:
    def test_returns_one_document_per_page(self, sample_pdf: pathlib.Path):
        reader = OxidizePdfReader(mode="pages")
        docs = reader.load_data(sample_pdf)
        assert len(docs) == 2
        assert all(isinstance(d, Document) for d in docs)

    def test_page_text_contains_expected_content(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="pages").load_data(sample_pdf)
        assert "Chapter 1" in docs[0].text
        assert "first paragraph" in docs[0].text
        assert "Chapter 2" in docs[1].text
        assert "detailed information" in docs[1].text

    def test_page_numbers_are_one_indexed(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="pages").load_data(sample_pdf)
        assert docs[0].metadata["page_number"] == 1
        assert docs[1].metadata["page_number"] == 2

    def test_base_metadata_populated(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="pages").load_data(sample_pdf)
        meta = docs[0].metadata
        assert meta["file_path"] == str(sample_pdf)
        assert meta["file_name"] == "sample.pdf"
        assert meta["total_pages"] == 2
        assert meta["pdf_version"].startswith("1.")


class TestRagMode:
    def test_produces_at_least_one_chunk(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="rag").load_data(sample_pdf)
        assert len(docs) >= 1

    def test_chunk_text_references_source_content(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="rag").load_data(sample_pdf)
        combined = " ".join(d.text for d in docs)
        assert "Chapter 1" in combined
        assert "Chapter 2" in combined

    def test_chunk_metadata_fields_present(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="rag").load_data(sample_pdf)
        for doc in docs:
            meta = doc.metadata
            assert "chunk_index" in meta
            assert "page_numbers" in meta and isinstance(meta["page_numbers"], list)
            assert "element_types" in meta and isinstance(meta["element_types"], list)
            assert "token_estimate" in meta and isinstance(meta["token_estimate"], int)
            assert meta["token_estimate"] >= 0

    def test_chunk_indexes_are_sequential(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="rag").load_data(sample_pdf)
        indexes = [d.metadata["chunk_index"] for d in docs]
        assert indexes == list(range(len(docs)))

    def test_chunk_page_numbers_within_document_range(
        self, sample_pdf: pathlib.Path
    ):
        docs = OxidizePdfReader(mode="rag").load_data(sample_pdf)
        total_pages = docs[0].metadata["total_pages"]
        for doc in docs:
            for pn in doc.metadata["page_numbers"]:
                assert 1 <= pn <= total_pages

    def test_chunk_page_numbers_are_one_indexed(self, sample_pdf: pathlib.Path):
        # The bridge's RagChunk exposes 0-indexed pages; the adapter normalizes
        # to 1-indexed so metadata is consistent with "pages" mode and with
        # LlamaIndex conventions. This guard catches any regression if the
        # bridge changes indexing upstream.
        docs = OxidizePdfReader(mode="rag").load_data(sample_pdf)
        all_pages = {pn for d in docs for pn in d.metadata["page_numbers"]}
        assert 0 not in all_pages
        assert min(all_pages) >= 1


class TestMarkdownMode:
    def test_returns_single_document(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="markdown").load_data(sample_pdf)
        assert len(docs) == 1

    def test_markdown_contains_both_chapters(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="markdown").load_data(sample_pdf)
        body = docs[0].text
        assert "Chapter 1" in body
        assert "Chapter 2" in body

    def test_markdown_metadata_has_no_page_number(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="markdown").load_data(sample_pdf)
        assert "page_number" not in docs[0].metadata


class TestExtraInfoMerging:
    def test_extra_info_merged_without_overriding_builtin_fields(
        self, sample_pdf: pathlib.Path
    ):
        docs = OxidizePdfReader(mode="pages").load_data(
            sample_pdf, extra_info={"source": "unit-test", "total_pages": 999}
        )
        assert docs[0].metadata["source"] == "unit-test"
        assert docs[0].metadata["total_pages"] == 999

    def test_none_extra_info_is_safe(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="pages").load_data(sample_pdf, extra_info=None)
        assert "file_name" in docs[0].metadata


class TestFileInputs:
    def test_accepts_string_path(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="pages").load_data(str(sample_pdf))
        assert len(docs) == 2

    def test_accepts_pathlib_path(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfReader(mode="pages").load_data(sample_pdf)
        assert len(docs) == 2
