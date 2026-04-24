"""Behavior tests for OxidizePdfConverter.

All tests verify real extracted content and metadata — no smoke tests.

Haystack conventions differ from LlamaIndex / LangChain in three
user-visible ways this suite locks down:

- The converter is a class decorated with ``@component`` and its
  ``run`` method is decorated with ``@component.output_types(...)``.
  The component must be addable to a ``Pipeline``.
- ``run(sources=[...], meta=...)`` is batch-oriented: ``sources`` is a
  list, and ``meta`` can be a single dict (broadcast to all docs) or a
  list of dicts (one per source).
- ``Document`` exposes ``.content`` (not ``.page_content`` or ``.text``).
"""

from __future__ import annotations

import pathlib

import pytest
from haystack import Pipeline
from haystack.dataclasses import Document

from haystack_oxidize_pdf import OxidizePdfConverter


class TestComponentRegistration:
    def test_can_be_added_to_pipeline(self, sample_pdf: pathlib.Path):
        # Pipeline.add_component raises if the instance is not a
        # Haystack component. This exercises the @component decorator
        # registration end-to-end, not just presence of an attribute.
        pipeline = Pipeline()
        pipeline.add_component("converter", OxidizePdfConverter())
        result = pipeline.run({"converter": {"sources": [str(sample_pdf)]}})
        assert "converter" in result
        assert "documents" in result["converter"]

    def test_run_returns_dict_with_documents_key(self, sample_pdf: pathlib.Path):
        result = OxidizePdfConverter().run(sources=[sample_pdf])
        assert isinstance(result, dict)
        assert "documents" in result
        assert isinstance(result["documents"], list)

    def test_documents_are_haystack_document_instances(
        self, sample_pdf: pathlib.Path
    ):
        result = OxidizePdfConverter().run(sources=[sample_pdf])
        assert all(isinstance(d, Document) for d in result["documents"])


class TestConstruction:
    def test_default_mode_is_rag(self):
        converter = OxidizePdfConverter()
        assert converter.mode == "rag"

    @pytest.mark.parametrize("mode", ["rag", "pages", "markdown"])
    def test_known_modes_accepted(self, mode):
        converter = OxidizePdfConverter(mode=mode)
        assert converter.mode == mode

    def test_unknown_mode_rejected(self):
        with pytest.raises(ValueError, match="Unknown mode"):
            OxidizePdfConverter(mode="invalid")  # type: ignore[arg-type]


class TestPagesMode:
    def test_one_source_produces_one_doc_per_page(self, sample_pdf: pathlib.Path):
        result = OxidizePdfConverter(mode="pages").run(sources=[sample_pdf])
        docs = result["documents"]
        assert len(docs) == 2

    def test_page_content_contains_expected_text(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="pages").run(sources=[sample_pdf])[
            "documents"
        ]
        assert "Chapter 1" in docs[0].content
        assert "first paragraph" in docs[0].content
        assert "Chapter 2" in docs[1].content
        assert "detailed information" in docs[1].content

    def test_page_numbers_are_one_indexed(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="pages").run(sources=[sample_pdf])[
            "documents"
        ]
        assert docs[0].meta["page_number"] == 1
        assert docs[1].meta["page_number"] == 2

    def test_base_metadata_populated(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="pages").run(sources=[sample_pdf])[
            "documents"
        ]
        meta = docs[0].meta
        assert meta["file_path"] == str(sample_pdf)
        assert meta["file_name"] == "sample.pdf"
        assert meta["total_pages"] == 2
        assert meta["pdf_version"].startswith("1.")


class TestRagMode:
    def test_produces_at_least_one_chunk(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="rag").run(sources=[sample_pdf])["documents"]
        assert len(docs) >= 1

    def test_chunk_content_references_source_text(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="rag").run(sources=[sample_pdf])["documents"]
        combined = " ".join(d.content for d in docs)
        assert "Chapter 1" in combined
        assert "Chapter 2" in combined

    def test_chunk_metadata_fields_present(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="rag").run(sources=[sample_pdf])["documents"]
        for doc in docs:
            meta = doc.meta
            assert "chunk_index" in meta
            assert "page_numbers" in meta and isinstance(meta["page_numbers"], list)
            assert "element_types" in meta and isinstance(meta["element_types"], list)
            assert "token_estimate" in meta and isinstance(meta["token_estimate"], int)

    def test_chunk_indexes_are_sequential_per_source(
        self, sample_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="rag").run(sources=[sample_pdf])["documents"]
        indexes = [d.meta["chunk_index"] for d in docs]
        assert indexes == list(range(len(docs)))

    def test_chunk_page_numbers_are_one_indexed(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="rag").run(sources=[sample_pdf])["documents"]
        all_pages = {pn for d in docs for pn in d.meta["page_numbers"]}
        assert 0 not in all_pages
        assert min(all_pages) >= 1


class TestMarkdownMode:
    def test_one_source_produces_one_markdown_doc(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="markdown").run(sources=[sample_pdf])[
            "documents"
        ]
        assert len(docs) == 1

    def test_markdown_contains_both_chapters(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="markdown").run(sources=[sample_pdf])[
            "documents"
        ]
        body = docs[0].content
        assert "Chapter 1" in body
        assert "Chapter 2" in body

    def test_markdown_metadata_has_no_page_number(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="markdown").run(sources=[sample_pdf])[
            "documents"
        ]
        assert "page_number" not in docs[0].meta


class TestBatchSources:
    """Haystack converters accept multiple sources in one run call."""

    def test_markdown_mode_batches_one_doc_per_source(
        self, sample_pdf: pathlib.Path, second_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="markdown").run(
            sources=[sample_pdf, second_pdf]
        )["documents"]
        assert len(docs) == 2
        # Order preserved: docs[i] corresponds to sources[i]
        assert "Chapter 1" in docs[0].content
        assert "Chapter 1" not in docs[1].content
        assert "Appendix: References" in docs[1].content

    def test_pages_mode_preserves_source_order(
        self, sample_pdf: pathlib.Path, second_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="pages").run(
            sources=[sample_pdf, second_pdf]
        )["documents"]
        # sample_pdf has 2 pages, second_pdf has 1 page => 3 total docs.
        assert len(docs) == 3
        assert "Chapter 1" in docs[0].content
        assert "Chapter 2" in docs[1].content
        assert "Appendix" in docs[2].content

    def test_rag_mode_chunk_indexes_reset_per_source(
        self, sample_pdf: pathlib.Path, second_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="rag").run(
            sources=[sample_pdf, second_pdf]
        )["documents"]

        # Group docs by source path to verify per-source sequential indexing.
        by_source: dict[str, list[int]] = {}
        for d in docs:
            by_source.setdefault(d.meta["file_path"], []).append(
                d.meta["chunk_index"]
            )
        for fpath, indexes in by_source.items():
            assert indexes == list(range(len(indexes))), (
                f"chunk_index should reset to 0 for each source; source "
                f"{fpath} got {indexes}"
            )


class TestMetaAsDict:
    """``meta`` can be a single dict applied (broadcast) to every document."""

    def test_dict_meta_attaches_to_all_output_docs(
        self, sample_pdf: pathlib.Path, second_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="markdown").run(
            sources=[sample_pdf, second_pdf], meta={"source_tag": "batch-A"}
        )["documents"]
        assert all(d.meta["source_tag"] == "batch-A" for d in docs)

    def test_dict_meta_merges_under_caller_precedence(
        self, sample_pdf: pathlib.Path
    ):
        # Caller's meta overrides base fields intentionally — same precedence
        # rule as the LangChain loader and LlamaIndex reader.
        docs = OxidizePdfConverter(mode="pages").run(
            sources=[sample_pdf], meta={"total_pages": 999, "owner": "unit"}
        )["documents"]
        assert docs[0].meta["total_pages"] == 999
        assert docs[0].meta["owner"] == "unit"
        # Page-level fields still present — merged after caller meta.
        assert docs[0].meta["page_number"] == 1


class TestMetaAsList:
    """``meta`` can be a list of dicts, one per source, with per-source scoping."""

    def test_list_meta_applies_each_dict_to_its_source(
        self, sample_pdf: pathlib.Path, second_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="markdown").run(
            sources=[sample_pdf, second_pdf],
            meta=[{"tag": "first"}, {"tag": "second"}],
        )["documents"]
        assert docs[0].meta["tag"] == "first"
        assert docs[1].meta["tag"] == "second"

    def test_list_meta_length_mismatch_raises(
        self, sample_pdf: pathlib.Path, second_pdf: pathlib.Path
    ):
        with pytest.raises(ValueError, match="meta"):
            OxidizePdfConverter(mode="markdown").run(
                sources=[sample_pdf, second_pdf],
                meta=[{"tag": "only-one"}],
            )

    def test_list_meta_scopes_per_source_in_pages_mode(
        self, sample_pdf: pathlib.Path, second_pdf: pathlib.Path
    ):
        docs = OxidizePdfConverter(mode="pages").run(
            sources=[sample_pdf, second_pdf],
            meta=[{"tag": "sample"}, {"tag": "appendix"}],
        )["documents"]
        # sample_pdf → 2 docs; second_pdf → 1 doc
        assert docs[0].meta["tag"] == "sample"
        assert docs[1].meta["tag"] == "sample"
        assert docs[2].meta["tag"] == "appendix"


class TestFileInputs:
    def test_accepts_string_paths(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="pages").run(sources=[str(sample_pdf)])[
            "documents"
        ]
        assert len(docs) == 2

    def test_accepts_pathlib_paths(self, sample_pdf: pathlib.Path):
        docs = OxidizePdfConverter(mode="pages").run(sources=[sample_pdf])[
            "documents"
        ]
        assert len(docs) == 2

    def test_empty_sources_returns_empty_documents(self):
        docs = OxidizePdfConverter(mode="pages").run(sources=[])["documents"]
        assert docs == []
